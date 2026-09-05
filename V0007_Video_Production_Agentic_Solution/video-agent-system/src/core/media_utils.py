"""Shared FFmpeg and workspace-safety primitives for core media operations."""

import shutil
import subprocess
from pathlib import Path
from typing import Sequence

from src.config import OUTPUT_DIR, TEMP_DIR, WORKSPACE_DIR


class MediaOperationError(RuntimeError):
    """A media command failed with diagnostic output safe for an agent to inspect."""


def ffmpeg_executable() -> str:
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as exc:
        raise MediaOperationError("FFmpeg is required. Install imageio-ffmpeg or put ffmpeg on PATH.") from exc


def workspace_path(path: str | Path, *, must_exist: bool = False, output: bool = False) -> Path:
    candidate = Path(path).expanduser().resolve()
    root = WORKSPACE_DIR.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("Media paths must stay within the project workspace")
    if must_exist and (not candidate.is_file() or candidate.stat().st_size == 0):
        raise FileNotFoundError(f"Media file does not exist or is empty: {candidate}")
    if output:
        candidate.parent.mkdir(parents=True, exist_ok=True)
        if candidate.exists():
            raise FileExistsError(f"Output already exists: {candidate}")
    return candidate


def default_output(filename: str) -> Path:
    return workspace_path(OUTPUT_DIR / filename, output=True)


def run_ffmpeg(arguments: Sequence[str], *, timeout: int = 180) -> str:
    command = [ffmpeg_executable(), "-hide_banner", "-y", *arguments]
    completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()[-2000:]
        raise MediaOperationError(f"FFmpeg failed ({completed.returncode}): {detail}")
    return completed.stderr


def ensure_nonempty_output(path: Path) -> dict[str, int | str]:
    if not path.is_file() or path.stat().st_size == 0:
        raise MediaOperationError(f"Media operation did not create a non-empty output: {path}")
    return {"output_path": str(path), "file_size_bytes": path.stat().st_size}


def temporary_file(name: str) -> Path:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    return workspace_path(TEMP_DIR / name, output=True)
