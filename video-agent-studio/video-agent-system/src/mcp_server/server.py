"""FastMCP exposure layer for atomic, workspace-safe media operations."""

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    from fastmcp import FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

from src.core.audio_engine import generate_tts as core_generate_tts
from src.core.image_engine import (
    add_text_overlay as core_add_text_overlay,
    format_image_aspect_ratio as core_format_image_aspect_ratio,
)
from src.core.media_info import get_media_info as core_get_media_info
from src.core.media_utils import workspace_path
from src.core.subtitle_engine import generate_and_burn_subtitles as core_generate_and_burn_subtitles
from src.core.video_engine import (
    adjust_audio_volume as core_adjust_audio_volume,
    concatenate_video_clips as core_concatenate_video_clips,
    create_video_from_image_audio as core_create_video_from_image_audio,
    extract_audio as core_extract_audio,
    generate_thumbnail as core_generate_thumbnail,
    merge_audio_tracks as core_merge_audio_tracks,
    replace_video_audio as core_replace_video_audio,
    trim_media as core_trim_media,
    validate_final_video as core_validate_final_video,
)

mcp = FastMCP("media_tools")


def _workspace_output(output_path: Optional[str]) -> Optional[str]:
    """Validate caller-chosen destinations before delegating to core functions."""
    return str(workspace_path(output_path, output=True)) if output_path else None


@mcp.tool()
def get_media_info(media_path: str) -> Dict[str, Any]:
    """Inspect media file properties including duration, dimensions, aspect ratio, codecs, audio streams, frame rate, and file size."""
    return core_get_media_info(media_path)


@mcp.tool()
def generate_tts(
    text: str,
    output_path: Optional[str] = None,
    model_name: Optional[str] = "gtts",
    voice: Optional[str] = "en",
    return_bytes: bool = False,
) -> Dict[str, Any]:
    """Convert text script into a voiceover audio file using a configured TTS engine (gTTS, edge-tts, pyttsx3)."""
    safe_output = _workspace_output(output_path)
    result = core_generate_tts(text, safe_output, model_name, voice, return_bytes)
    if not Path(result["output_path"]).is_file() or result["file_size_bytes"] <= 0:
        raise RuntimeError("TTS provider did not create a non-empty audio file")
    return result


@mcp.tool()
def merge_audio_tracks(
    voiceover_path: str,
    background_music_path: str,
    output_path: str,
    background_volume: float = 0.18,
    ducking_ratio: float = 8.0,
) -> Dict[str, Any]:
    """Mix voiceover narration and background music track, automatically ducking music during narration."""
    return core_merge_audio_tracks(
        voiceover_path, background_music_path, _workspace_output(output_path), background_volume, ducking_ratio
    )


@mcp.tool()
def extract_audio(video_path: str, output_path: str) -> Dict[str, Any]:
    """Extract audio stream from an input video into an MP3, AAC, or WAV file."""
    return core_extract_audio(video_path, _workspace_output(output_path))


@mcp.tool()
def format_image_aspect_ratio(image_path: str, output_path: str, aspect_ratio: str) -> Dict[str, Any]:
    """Fit an input image into a target video canvas (e.g. '16:9' -> 1920x1080, '9:16' -> 1080x1920, '1:1' -> 1080x1080) with letterbox padding."""
    return core_format_image_aspect_ratio(image_path, _workspace_output(output_path), aspect_ratio)


@mcp.tool()
def add_text_overlay(
    image_path: str,
    output_path: str,
    text: str,
    position: str = "bottom",
    font_size: int = 64,
    color: str = "white",
    background: bool = True,
) -> Dict[str, Any]:
    """Add a title, caption, or lower-third text overlay onto an image canvas."""
    return core_add_text_overlay(
        image_path, _workspace_output(output_path), text, position, font_size, color, background
    )


@mcp.tool()
def create_video_from_image_audio(
    image_path: str,
    audio_path: str,
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
) -> Dict[str, Any]:
    """Create an MP4 video clip from a still image and audio track, matching the audio duration (H.264/AAC yuv420p)."""
    return core_create_video_from_image_audio(
        image_path, audio_path, _workspace_output(output_path), width, height, fps
    )


@mcp.tool()
def concatenate_video_clips(
    input_clips: List[str],
    output_path: str,
    auto_normalize: bool = True,
) -> Dict[str, Any]:
    """Join multiple video clips sequentially into a single timeline with auto-normalization for differing resolutions and audio formats."""
    return core_concatenate_video_clips(input_clips, _workspace_output(output_path), auto_normalize=auto_normalize)


@mcp.tool()
def replace_video_audio(video_path: str, audio_path: str, output_path: str) -> Dict[str, Any]:
    """Replace the audio track of a video with a supplied audio track, synchronized to the shorter stream."""
    return core_replace_video_audio(video_path, audio_path, _workspace_output(output_path))


@mcp.tool()
def generate_and_burn_subtitles(
    video_path: str,
    output_path: str,
    subtitle_path: Optional[str] = None,
    transcript: Optional[str] = None,
    subtitle_output_path: Optional[str] = None,
    font_size: int = 22,
    font_color: str = "white",
) -> Dict[str, Any]:
    """Generate and burn SRT subtitles/captions into a video, supporting direct subtitle files, transcript text, or Whisper ASR."""
    safe_sub_out = _workspace_output(subtitle_output_path) if subtitle_output_path else None
    return core_generate_and_burn_subtitles(
        video_path,
        _workspace_output(output_path),
        subtitle_path,
        transcript,
        safe_sub_out,
        font_size=font_size,
        font_color=font_color,
    )


@mcp.tool()
def validate_final_video(
    video_path: str,
    expected_width: Optional[int] = 1920,
    expected_height: Optional[int] = 1080,
    require_audio: bool = True,
) -> Dict[str, Any]:
    """Run automated QC checks on a final video (file existence, readability, duration, resolution, video/audio streams)."""
    return core_validate_final_video(video_path, expected_width, expected_height, require_audio)


@mcp.tool()
def trim_media(
    media_path: str,
    output_path: str,
    start_time: float = 0.0,
    end_time: Optional[float] = None,
    duration: Optional[float] = None,
) -> Dict[str, Any]:
    """Trim a video or audio clip to a specified start time, end time, or duration."""
    return core_trim_media(media_path, _workspace_output(output_path), start_time, end_time, duration)


@mcp.tool()
def adjust_audio_volume(
    audio_path: str,
    output_path: str,
    volume: float = 1.0,
) -> Dict[str, Any]:
    """Adjust audio gain/volume multiplier (e.g. 0.5 for 50%, 1.5 for 150%)."""
    return core_adjust_audio_volume(audio_path, _workspace_output(output_path), volume)


@mcp.tool()
def generate_thumbnail(
    video_path: str,
    output_path: str,
    timestamp_seconds: float = 0.5,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> Dict[str, Any]:
    """Extract a high-quality frame/thumbnail from a video at a specified timestamp."""
    return core_generate_thumbnail(video_path, _workspace_output(output_path), timestamp_seconds, width, height)


# Tool registry mapping tool names to their underlying callable functions
TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {
    "get_media_info": get_media_info,
    "generate_tts": generate_tts,
    "merge_audio_tracks": merge_audio_tracks,
    "extract_audio": extract_audio,
    "format_image_aspect_ratio": format_image_aspect_ratio,
    "add_text_overlay": add_text_overlay,
    "create_video_from_image_audio": create_video_from_image_audio,
    "concatenate_video_clips": concatenate_video_clips,
    "replace_video_audio": replace_video_audio,
    "generate_and_burn_subtitles": generate_and_burn_subtitles,
    "validate_final_video": validate_final_video,
    "trim_media": trim_media,
    "adjust_audio_volume": adjust_audio_volume,
    "generate_thumbnail": generate_thumbnail,
}


if __name__ == "__main__":
    mcp.run()

