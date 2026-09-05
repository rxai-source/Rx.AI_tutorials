"""Atomic FFmpeg audio/video operations for the production pipeline."""

import uuid
from pathlib import Path
from typing import Any, Sequence

from src.core.media_info import get_media_info
from src.core.media_utils import ensure_nonempty_output, run_ffmpeg, temporary_file, workspace_path


def extract_audio(video_path: str, output_path: str) -> dict[str, Any]:
    """Extract the audio stream from a video into an audio file."""
    source = workspace_path(video_path, must_exist=True)
    destination = workspace_path(output_path, output=True)
    suffix = destination.suffix.lower()
    if suffix == ".mp3":
        codec = "libmp3lame"
    elif suffix == ".wav":
        codec = "pcm_s16le"
    else:
        codec = "aac"
    run_ffmpeg(["-i", str(source), "-vn", "-c:a", codec, str(destination)])
    return {"status": "success", **ensure_nonempty_output(destination), "source_path": str(source), "audio_codec": codec}


def merge_audio_tracks(
    voiceover_path: str,
    background_music_path: str,
    output_path: str,
    background_volume: float = 0.18,
    ducking_ratio: float = 8.0,
) -> dict[str, Any]:
    """Combine narration and background music with sidechain audio ducking."""
    if not 0 < background_volume <= 2.0:
        raise ValueError("background_volume must be between 0.01 and 2.0")
    voiceover = workspace_path(voiceover_path, must_exist=True)
    music = workspace_path(background_music_path, must_exist=True)
    destination = workspace_path(output_path, output=True)
    filter_graph = (
        f"[1:a]volume={background_volume}[music];"
        f"[music][0:a]sidechaincompress=ratio={ducking_ratio}:threshold=0.02[ducked];"
        "[0:a][ducked]amix=inputs=2:duration=first:normalize=0[aout]"
    )
    run_ffmpeg(["-i", str(voiceover), "-i", str(music), "-filter_complex", filter_graph, "-map", "[aout]", "-c:a", "aac", str(destination)])
    return {"status": "success", **ensure_nonempty_output(destination), "ducking": True, "background_volume": background_volume}


def create_video_from_image_audio(
    image_path: str,
    audio_path: str,
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
) -> dict[str, Any]:
    """Create an MP4 clip from a still image and audio track."""
    if width <= 0 or height <= 0 or fps <= 0:
        raise ValueError("width, height, and fps must be positive")
    image = workspace_path(image_path, must_exist=True)
    audio = workspace_path(audio_path, must_exist=True)
    destination = workspace_path(output_path, output=True)
    scale_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
    run_ffmpeg([
        "-loop", "1", "-i", str(image), "-i", str(audio), "-shortest", "-r", str(fps),
        "-vf", scale_filter, "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-c:a", "aac", str(destination),
    ])
    info = get_media_info(str(destination))
    if not info["video_codec"] or not info["audio_streams"]:
        raise ValueError("Generated clip is missing expected video or audio streams")
    return {"status": "success", **ensure_nonempty_output(destination), "media_info": info}


def concatenate_video_clips(
    input_clips: Sequence[str],
    output_path: str,
    auto_normalize: bool = True,
) -> dict[str, Any]:
    """Join multiple video clips sequentially into a single timeline."""
    if len(input_clips) < 2:
        raise ValueError("At least two clips are required for concatenation")
    clips = [workspace_path(clip, must_exist=True) for clip in input_clips]
    destination = workspace_path(output_path, output=True)
    metadata = [get_media_info(str(clip)) for clip in clips]
    signatures = {(item["width"], item["height"], item["video_codec"], item["audio_codec"]) for item in metadata}

    if len(signatures) == 1 and not auto_normalize:
        manifest = temporary_file(f"concat_{uuid.uuid4().hex}.txt")
        try:
            manifest.write_text("".join(f"file '{clip.as_posix()}'\n" for clip in clips), encoding="utf-8")
            run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(manifest), "-c", "copy", str(destination)])
        finally:
            manifest.unlink(missing_ok=True)
    elif len(signatures) == 1 and all(item["video_codec"] and item["audio_codec"] for item in metadata):
        manifest = temporary_file(f"concat_{uuid.uuid4().hex}.txt")
        try:
            manifest.write_text("".join(f"file '{clip.as_posix()}'\n" for clip in clips), encoding="utf-8")
            run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(manifest), "-c", "copy", str(destination)])
        finally:
            manifest.unlink(missing_ok=True)
    else:
        # Auto-normalize mismatched clips to standard canvas & audio format
        target_w = metadata[0]["width"] or 1920
        target_h = metadata[0]["height"] or 1080
        cmd_inputs: list[str] = []
        filter_parts: list[str] = []
        concat_inputs: list[str] = []

        for i, clip in enumerate(clips):
            cmd_inputs.extend(["-i", str(clip)])
            filter_parts.append(
                f"[{i}:v]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
                f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v{i}];"
            )
            has_audio = bool(metadata[i]["audio_streams"])
            if has_audio:
                filter_parts.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo[a{i}];")
            else:
                filter_parts.append(f"aevalsrc=0:d=10[a{i}];")
            concat_inputs.append(f"[v{i}][a{i}]")

        filter_graph = "".join(filter_parts) + f"{''.join(concat_inputs)}concat=n={len(clips)}:v=1:a=1[outv][outa]"
        run_ffmpeg([
            *cmd_inputs,
            "-filter_complex", filter_graph,
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            str(destination),
        ])

    return {"status": "success", **ensure_nonempty_output(destination), "clip_count": len(clips), "media_info": get_media_info(str(destination))}


def replace_video_audio(video_path: str, audio_path: str, output_path: str) -> dict[str, Any]:
    """Replace a video's audio track with a supplied audio file."""
    video = workspace_path(video_path, must_exist=True)
    audio = workspace_path(audio_path, must_exist=True)
    destination = workspace_path(output_path, output=True)
    run_ffmpeg([
        "-i", str(video), "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-shortest", str(destination),
    ])
    info = get_media_info(str(destination))
    if not info["audio_streams"]:
        raise ValueError("Replaced video has no audio stream")
    return {"status": "success", **ensure_nonempty_output(destination), "media_info": info}


def trim_media(
    media_path: str,
    output_path: str,
    start_time: float = 0.0,
    end_time: float | None = None,
    duration: float | None = None,
) -> dict[str, Any]:
    """Trim an audio or video file to a specified start/end timestamp or duration."""
    if start_time < 0:
        raise ValueError("start_time cannot be negative")
    source = workspace_path(media_path, must_exist=True)
    destination = workspace_path(output_path, output=True)
    
    cmd = ["-ss", str(start_time), "-i", str(source)]
    if duration is not None:
        if duration <= 0:
            raise ValueError("duration must be positive")
        cmd.extend(["-t", str(duration)])
    elif end_time is not None:
        if end_time <= start_time:
            raise ValueError("end_time must be greater than start_time")
        cmd.extend(["-t", str(end_time - start_time)])
    
    info = get_media_info(str(source))
    if info["media_type"] == "video":
        cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac"])
    elif info["media_type"] == "audio":
        codec = "libmp3lame" if destination.suffix.lower() == ".mp3" else "aac"
        cmd.extend(["-c:a", codec])
    
    cmd.append(str(destination))
    run_ffmpeg(cmd)
    return {"status": "success", **ensure_nonempty_output(destination), "media_info": get_media_info(str(destination))}


def adjust_audio_volume(
    audio_path: str,
    output_path: str,
    volume: float = 1.0,
) -> dict[str, Any]:
    """Adjust the gain / volume level of an audio track."""
    if volume <= 0:
        raise ValueError("volume must be positive")
    source = workspace_path(audio_path, must_exist=True)
    destination = workspace_path(output_path, output=True)
    codec = "libmp3lame" if destination.suffix.lower() == ".mp3" else "aac"
    run_ffmpeg(["-i", str(source), "-filter:a", f"volume={volume}", "-c:a", codec, str(destination)])
    return {"status": "success", **ensure_nonempty_output(destination), "volume": volume, "media_info": get_media_info(str(destination))}


def generate_thumbnail(
    video_path: str,
    output_path: str,
    timestamp_seconds: float = 0.5,
    width: int | None = None,
    height: int | None = None,
) -> dict[str, Any]:
    """Extract a high-quality still frame/thumbnail from a video at a specified timestamp."""
    source = workspace_path(video_path, must_exist=True)
    destination = workspace_path(output_path, output=True)
    cmd = ["-ss", str(max(0.0, timestamp_seconds)), "-i", str(source), "-vframes", "1"]
    if width and height and width > 0 and height > 0:
        cmd.extend(["-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease"])
    cmd.append(str(destination))
    run_ffmpeg(cmd)
    return {"status": "success", **ensure_nonempty_output(destination), "timestamp_seconds": timestamp_seconds}


def validate_final_video(
    video_path: str,
    expected_width: int | None = 1920,
    expected_height: int | None = 1080,
    require_audio: bool = True,
) -> dict[str, Any]:
    """Perform quality-control checks on a rendered video file."""
    checks: dict[str, bool] = {
        "file_exists_and_nonempty": False,
        "readable": False,
        "duration_valid": False,
        "video_stream_present": False,
        "audio_stream_present": False,
    }
    errors: list[str] = []
    warnings: list[str] = []
    try:
        path = workspace_path(video_path, must_exist=True)
        checks["file_exists_and_nonempty"] = True
        info = get_media_info(str(path))
        checks["readable"] = True
    except Exception as exc:
        return {"valid": False, "checks": checks, "errors": [str(exc)], "warnings": warnings, "media_info": None}

    checks["duration_valid"] = bool(info["duration_seconds"] and info["duration_seconds"] > 0)
    checks["video_stream_present"] = bool(info["video_codec"])
    checks["audio_stream_present"] = bool(info["audio_streams"])
    if not checks["duration_valid"]:
        errors.append("Video duration is missing or zero")
    if not checks["video_stream_present"]:
        errors.append("Video stream is missing")
    if require_audio and not checks["audio_stream_present"]:
        errors.append("Required audio stream is missing")
    if expected_width and expected_height:
        checks["target_resolution"] = info["width"] == expected_width and info["height"] == expected_height
        if not checks["target_resolution"]:
            errors.append(f"Expected {expected_width}x{expected_height}, got {info['width']}x{info['height']}")
    elif info["width"] is None or info["height"] is None:
        warnings.append("Video resolution could not be determined")
    return {"valid": not errors, "checks": checks, "errors": errors, "warnings": warnings, "media_info": info}

