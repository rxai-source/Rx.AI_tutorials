from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import json

try:
    import yaml  # PyYAML (optional)
    _HAS_YAML = True
except Exception:
    _HAS_YAML = False

from pydantic import BaseModel


class Persona(BaseModel):
    id: str
    display_name: Optional[str]
    role: str
    tools: Optional[List[str]] = []
    description: Optional[str] = None


class RoomStage(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    lead_agent: str
    ui_layout: str
    stage_tools: Optional[List[str]] = []


class RoomTemplate(BaseModel):
    id: str
    template_type: Optional[str] = None
    title: Optional[str]
    description: Optional[str] = None
    personas: List[Persona]
    stages: List[RoomStage]


def _parse_text(path: Path, text: str) -> dict:
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        if not _HAS_YAML:
            raise RuntimeError("PyYAML is required to load YAML templates. Install with `pip install pyyaml`.")
        return yaml.safe_load(text)
    if suffix == ".json":
        return json.loads(text)
    # fallback: try YAML if available, else JSON
    if _HAS_YAML:
        return yaml.safe_load(text)
    return json.loads(text)


def load_template(path: str | Path) -> RoomTemplate:
    """Load a single template file (YAML or JSON) and validate it.

    Raises RuntimeError if PyYAML is needed but not installed.
    """
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    data = _parse_text(p, raw)
    return RoomTemplate.parse_obj(data)


def load_templates_from_dir(directory: str | Path) -> List[RoomTemplate]:
    p = Path(directory)
    templates: List[RoomTemplate] = []
    if not p.exists():
        return templates
    for f in sorted(p.iterdir()):
        if f.is_file() and f.suffix.lower() in (".yaml", ".yml", ".json"):
            templates.append(load_template(f))
    return templates


__all__ = ["Persona", "RoomTemplate", "load_template", "load_templates_from_dir"]
