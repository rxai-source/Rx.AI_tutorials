"""Media inspection built on FFmpeg's portable diagnostic output."""

import re
import subprocess
from pathlib import Path
from typing import Any

from src.core.media_utils import ffmpeg_executable, workspace_path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif"}


def _duration_seconds(value: str) -> float:
    parts = value.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return round(int(hours) * 3600 + int(minutes) * 60 + float(seconds), 3)
    elif len(parts) == 2:
        minutes, seconds = parts
        return round(int(minutes) * 60 + float(seconds), 3)
    return round(float(parts[0]), 3)


def _calculate_aspect_ratio_str(width: int, height: int) -> str:
    if width <= 0 or height <= 0:
        return "unknown"
    ratio = width / height
    common_ratios = [
        (16 / 9, "16:9"),
        (9 / 16, "9:16"),
        (1.0, "1:1"),
        (4 / 5, "4:5"),
        (4 / 3, "4:3"),
        (21 / 9, "21:9"),
    ]
    for target_ratio, label in common_ratios:
        if abs(ratio - target_ratio) < 0.05:
            return label
    return f"{width}:{height}"


def get_media_info(media_path: str) -> dict[str, Any]:
    """Return inspectable stream metadata without requiring a system ffprobe binary."""
    path = workspace_path(media_path, must_exist=True)
    result = subprocess.run(
        [ffmpeg_executable(), "-hide_banner", "-i", str(path)], capture_output=True, text=True, timeout=30
    )
    diagnostic = result.stderr
    if "Invalid data found" in diagnostic or "No such file" in diagnostic:
        raise ValueError(f"Invalid media file: {path}")

    duration_match = re.search(r"Duration:\s*(\d{2}:\d{2}:\d{2}(?:\.\d+)?)", diagnostic)
    video_match = re.search(r"Video:\s*([^,]+).*?(\d{2,5})x(\d{2,5}).*?(\d+(?:\.\d+)?)\s*fps", diagnostic)
    if not video_match:
        video_match = re.search(r"Video:\s*([^,]+).*?(\d{2,5})x(\d{2,5})", diagnostic)
    audio_matches = re.findall(r"Audio:\s*([^,\s]+)", diagnostic)
    
    raw_video_codec = video_match.group(1).strip() if video_match else None
    video_codec = raw_video_codec.split()[0].split("(")[0].strip() if raw_video_codec else None
    width = int(video_match.group(2)) if video_match else None
    height = int(video_match.group(3)) if video_match else None
    frame_rate = float(video_match.group(4)) if video_match and video_match.lastindex and video_match.lastindex >= 4 else None
    duration = _duration_seconds(duration_match.group(1)) if duration_match else None
    
    is_image = path.suffix.lower() in IMAGE_EXTENSIONS
    if is_image and not duration:
        media_type = "image"
    elif video_match and duration is not None:
        media_type = "video"
    elif audio_matches:
        media_type = "audio"
    elif video_match:
        media_type = "video"
    else:
        media_type = "unknown"

    if duration is None and not video_match and not audio_matches and not is_image:
        raise ValueError(f"Could not read media streams from: {path}")

    aspect_ratio_val = round(width / height, 4) if width and height else None
    aspect_ratio_str = _calculate_aspect_ratio_str(width, height) if width and height else None

    return {
        "path": str(path),
        "file_size_bytes": path.stat().st_size,
        "duration_seconds": duration,
        "duration": duration,
        "width": width,
        "height": height,
        "aspect_ratio": aspect_ratio_val,
        "aspect_ratio_str": aspect_ratio_str,
        "frame_rate": frame_rate,
        "video_codec": video_codec,
        "video_codec_detailed": raw_video_codec,
        "audio_streams": [{"codec": codec} for codec in audio_matches],
        "audio_codec": audio_matches[0] if audio_matches else None,
        "media_type": media_type,
    }

