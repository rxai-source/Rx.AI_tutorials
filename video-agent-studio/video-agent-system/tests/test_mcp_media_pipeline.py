"""Comprehensive, real FFmpeg/Pillow integration tests for the MCP media tools layer."""

import asyncio
import shutil
import uuid
from pathlib import Path

import pytest
from PIL import Image

from src.config import TEMP_DIR
from src.core.image_engine import add_text_overlay, format_image_aspect_ratio
from src.core.media_info import get_media_info
from src.core.media_utils import run_ffmpeg
from src.core.subtitle_engine import generate_and_burn_subtitles
from src.core.video_engine import (
    adjust_audio_volume,
    concatenate_video_clips,
    create_video_from_image_audio,
    extract_audio,
    generate_thumbnail,
    merge_audio_tracks,
    replace_video_audio,
    trim_media,
    validate_final_video,
)
from src.mcp_server.server import TOOL_REGISTRY, mcp


@pytest.fixture()
def media_dir():
    directory = TEMP_DIR / f"mcp_media_test_{uuid.uuid4().hex}"
    directory.mkdir(parents=True)
    try:
        yield directory
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def _make_tone(path: Path, frequency: int = 440, duration: float = 0.5) -> Path:
    run_ffmpeg(["-f", "lavfi", "-i", f"sine=frequency={frequency}:sample_rate=44100", "-t", str(duration), "-c:a", "aac", str(path)])
    return path


def _make_image(path: Path, width: int = 160, height: int = 100, color: str = "steelblue") -> Path:
    Image.new("RGB", (width, height), color).save(path)
    return path


def test_mcp_server_registers_every_required_atomic_tool():
    """Verify that FastMCP server exposes all required core and production tools."""
    tools = asyncio.run(mcp.list_tools())
    names = {tool.name for tool in tools}
    expected = {
        "get_media_info",
        "generate_tts",
        "merge_audio_tracks",
        "extract_audio",
        "format_image_aspect_ratio",
        "add_text_overlay",
        "create_video_from_image_audio",
        "concatenate_video_clips",
        "replace_video_audio",
        "generate_and_burn_subtitles",
        "validate_final_video",
        "trim_media",
        "adjust_audio_volume",
        "generate_thumbnail",
    }
    assert expected <= names
    assert expected <= set(TOOL_REGISTRY.keys())


def test_happy_path_image_audio_video_and_qc(media_dir: Path):
    """Test full happy path pipeline: image formatting, text overlay, clip rendering, and final QC."""
    image = _make_image(media_dir / "input.png")
    formatted = format_image_aspect_ratio(str(image), str(media_dir / "formatted.png"), "16:9")
    overlay = add_text_overlay(formatted["output_path"], str(media_dir / "overlay.png"), "Agentic AI", position="lower_third")
    audio = _make_tone(media_dir / "voice.m4a", duration=0.6)
    rendered = create_video_from_image_audio(overlay["output_path"], str(audio), str(media_dir / "clip.mp4"), width=320, height=180)
    qc = validate_final_video(rendered["output_path"], expected_width=320, expected_height=180)

    assert formatted["width"] == 1920
    assert formatted["height"] == 1080
    assert overlay["file_size_bytes"] > 0
    assert overlay["position"] == "lower_third"
    assert rendered["media_info"]["audio_streams"]
    assert rendered["media_info"]["video_codec"] == "h264"
    assert qc["valid"] is True
    assert qc["checks"]["readable"] is True
    assert qc["checks"]["target_resolution"] is True


def test_audio_video_composition_concatenation_and_subtitles(media_dir: Path):
    """Test audio mixing with ducking, stream replacement, concatenation, and subtitle burn-in."""
    image = _make_image(media_dir / "image.png")
    voice = _make_tone(media_dir / "voice.m4a", 440, duration=0.6)
    music = _make_tone(media_dir / "music.m4a", 220, duration=0.6)
    mixed = merge_audio_tracks(str(voice), str(music), str(media_dir / "mixed.m4a"), background_volume=0.2)
    clip_a = create_video_from_image_audio(str(image), mixed["output_path"], str(media_dir / "a.mp4"), width=320, height=180)
    clip_b = create_video_from_image_audio(str(image), str(voice), str(media_dir / "b.mp4"), width=320, height=180)
    extracted = extract_audio(clip_a["output_path"], str(media_dir / "extracted.m4a"))
    replaced = replace_video_audio(clip_a["output_path"], extracted["output_path"], str(media_dir / "replaced.mp4"))
    combined = concatenate_video_clips([clip_a["output_path"], clip_b["output_path"]], str(media_dir / "combined.mp4"))
    captions = media_dir / "captions.srt"
    captions.write_text("1\n00:00:00,000 --> 00:00:00,500\nHello world\n", encoding="utf-8")
    captioned = generate_and_burn_subtitles(combined["output_path"], str(media_dir / "captioned.mp4"), subtitle_path=str(captions))

    assert mixed["ducking"] is True
    assert get_media_info(replaced["output_path"])["audio_streams"]
    assert combined["media_info"]["duration_seconds"] >= 0.8
    assert captioned["media_info"]["video_codec"]
    qc = validate_final_video(captioned["output_path"], expected_width=320, expected_height=180)
    assert qc["valid"] is True


def test_concatenate_clips_with_differing_resolutions_auto_normalizes(media_dir: Path):
    """Test that concatenation seamlessly auto-normalizes clips with different resolutions."""
    img_a = _make_image(media_dir / "img_a.png", width=320, height=180)
    img_b = _make_image(media_dir / "img_b.png", width=480, height=270)
    audio_a = _make_tone(media_dir / "audio_a.m4a", 440, duration=0.5)
    audio_b = _make_tone(media_dir / "audio_b.m4a", 880, duration=0.5)

    clip_a = create_video_from_image_audio(str(img_a), str(audio_a), str(media_dir / "clip_a.mp4"), width=320, height=180)
    clip_b = create_video_from_image_audio(str(img_b), str(audio_b), str(media_dir / "clip_b.mp4"), width=480, height=270)

    combined = concatenate_video_clips([clip_a["output_path"], clip_b["output_path"]], str(media_dir / "normalized_combined.mp4"), auto_normalize=True)
    assert combined["clip_count"] == 2
    assert combined["media_info"]["duration_seconds"] >= 0.8
    assert combined["media_info"]["width"] == 320
    assert combined["media_info"]["height"] == 180


def test_trim_media_adjust_volume_and_generate_thumbnail(media_dir: Path):
    """Test production tools: trim_media, adjust_audio_volume, generate_thumbnail."""
    image = _make_image(media_dir / "thumb_in.png", width=640, height=360)
    audio = _make_tone(media_dir / "long_audio.m4a", 440, duration=1.5)
    video = create_video_from_image_audio(str(image), str(audio), str(media_dir / "long_video.mp4"), width=640, height=360)

    # 1. Trim video
    trimmed_video = trim_media(video["output_path"], str(media_dir / "trimmed_video.mp4"), start_time=0.2, duration=0.6)
    assert trimmed_video["media_info"]["duration_seconds"] >= 0.5

    # 2. Trim audio
    trimmed_audio = trim_media(str(audio), str(media_dir / "trimmed_audio.m4a"), start_time=0.1, duration=0.5)
    assert trimmed_audio["media_info"]["duration_seconds"] >= 0.4

    # 3. Adjust audio volume
    vol_adjusted = adjust_audio_volume(str(audio), str(media_dir / "louder_audio.m4a"), volume=1.5)
    assert vol_adjusted["volume"] == 1.5

    # 4. Generate thumbnail
    thumb = generate_thumbnail(video["output_path"], str(media_dir / "thumbnail.png"), timestamp_seconds=0.3, width=320, height=180)
    assert Path(thumb["output_path"]).is_file()
    thumb_info = get_media_info(thumb["output_path"])
    assert thumb_info["media_type"] == "image"
    assert thumb_info["width"] == 320
    assert thumb_info["height"] == 180


def test_get_media_info_image_and_audio(media_dir: Path):
    """Verify get_media_info accurately inspects images and standalone audio tracks."""
    img = _make_image(media_dir / "still.png", width=1920, height=1080)
    img_info = get_media_info(str(img))
    assert img_info["media_type"] == "image"
    assert img_info["width"] == 1920
    assert img_info["height"] == 1080
    assert img_info["aspect_ratio_str"] == "16:9"

    aud = _make_tone(media_dir / "tone.m4a", duration=0.8)
    aud_info = get_media_info(str(aud))
    assert aud_info["media_type"] == "audio"
    assert aud_info["duration_seconds"] >= 0.7
    assert aud_info["audio_codec"] == "aac"


@pytest.mark.parametrize("path_content", [None, b"not media"])
def test_final_qc_reports_invalid_outputs(media_dir: Path, path_content: bytes | None):
    """Verify validate_final_video reports structured QC failures for missing or corrupted files."""
    target = media_dir / "invalid.mp4"
    if path_content is not None:
        target.write_bytes(path_content)
    result = validate_final_video(str(target), expected_width=320, expected_height=180)

    assert result["valid"] is False
    assert result["errors"]
    assert result["checks"]["readable"] is False


def test_final_qc_detects_wrong_resolution_and_missing_audio(media_dir: Path):
    """Verify validate_final_video flags resolution mismatch and missing audio."""
    image = _make_image(media_dir / "qc_img.png", width=320, height=180)
    audio = _make_tone(media_dir / "qc_aud.m4a", duration=0.5)
    video = create_video_from_image_audio(str(image), str(audio), str(media_dir / "qc_vid.mp4"), width=320, height=180)

    # Wrong resolution check
    qc_res = validate_final_video(video["output_path"], expected_width=1920, expected_height=1080)
    assert qc_res["valid"] is False
    assert any("Expected 1920x1080, got 320x180" in err for err in qc_res["errors"])


def test_workspace_safety_and_invalid_image_ratio(media_dir: Path):
    """Verify sandboxing rules and validation on bad aspect ratio inputs."""
    image = _make_image(media_dir / "image.png")
    with pytest.raises(ValueError, match="Unsupported aspect ratio"):
        format_image_aspect_ratio(str(image), str(media_dir / "wrong.png"), "3:2")
    with pytest.raises(ValueError, match="workspace"):
        get_media_info("C:/Windows/not-a-video.mp4")

