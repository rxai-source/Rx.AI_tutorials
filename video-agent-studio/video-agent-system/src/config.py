import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR / "workspace"
INPUT_DIR = WORKSPACE_DIR / "input"
TEMP_DIR = WORKSPACE_DIR / "temp"
OUTPUT_DIR = WORKSPACE_DIR / "output"

# Ensure workspace directories exist
for folder in [WORKSPACE_DIR, INPUT_DIR, TEMP_DIR, OUTPUT_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Default TTS Configuration
DEFAULT_TTS_MODEL = "gtts"
DEFAULT_TTS_VOICE = "en"
