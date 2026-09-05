"""Small, shared artifact helpers for API and developer-console uploads."""

import re
import uuid
from pathlib import Path
from typing import Any

from src.config import INPUT_DIR

SUPPORTED_ARTIFACT_EXTENSIONS = {
    ".txt", ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".mp3", ".wav", ".mp4", ".mov",
}
MAX_ARTIFACT_BYTES = 25 * 1024 * 1024


def save_artifact(filename: str, content: bytes, media_type: str | None = None) -> dict[str, str]:
    """Validate and store an uploaded artifact in the existing workspace input area."""
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename).name)
    suffix = Path(safe_name).suffix.lower()
    if not safe_name or suffix not in SUPPORTED_ARTIFACT_EXTENSIONS:
        raise ValueError(f"Unsupported artifact type: {suffix or 'no extension'}")
    if not content:
        raise ValueError("Uploaded artifact is empty")
    if len(content) > MAX_ARTIFACT_BYTES:
        raise ValueError(f"Artifact exceeds the {MAX_ARTIFACT_BYTES // (1024 * 1024)} MB limit")

    upload_dir = INPUT_DIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    artifact_id = uuid.uuid4().hex
    destination = upload_dir / f"{artifact_id}_{safe_name}"
    destination.write_bytes(content)
    return {
        "id": artifact_id,
        "filename": safe_name,
        "path": str(destination.resolve()),
        "media_type": media_type or "application/octet-stream",
    }


def validate_artifact_reference(reference: dict[str, Any]) -> dict[str, str]:
    """Allow the API to accept only files already staged under workspace/input."""
    path = Path(str(reference.get("path", ""))).resolve()
    input_root = INPUT_DIR.resolve()
    if input_root not in path.parents or not path.is_file():
        raise ValueError("Artifact path must be an existing file under workspace/input")
    return {
        "id": str(reference.get("id") or path.stem),
        "filename": str(reference.get("filename") or path.name),
        "path": str(path),
        "media_type": str(reference.get("media_type") or "application/octet-stream"),
    }
