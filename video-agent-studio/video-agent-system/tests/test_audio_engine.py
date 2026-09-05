import os
import tempfile
from pathlib import Path
import pytest

from src.core.audio_engine import generate_tts, TTS_PROVIDERS


def test_generate_tts_basic():
    """Test generating TTS audio with default settings."""
    text = "Hello, this is a test of the video agent text to speech tool."
    result = generate_tts(text=text, model_name="gtts", voice="en", return_bytes=True)

    assert result["status"] == "success"
    assert os.path.exists(result["output_path"])
    assert result["file_size_bytes"] > 0
    assert result["format"] == "mp3"
    assert result["audio_bytes_b64"] is not None


def test_generate_tts_custom_output_path():
    """Test generating TTS to a specific output path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target_path = str(Path(tmpdir) / "custom_speech.mp3")
        text = "Testing custom output destination."
        result = generate_tts(text=text, output_path=target_path)

        assert result["status"] == "success"
        assert result["output_path"] == str(Path(target_path).resolve())
        assert os.path.exists(target_path)


def test_generate_tts_empty_text_error():
    """Test error handling for empty text input."""
    with pytest.raises(ValueError, match="Text input for TTS cannot be empty"):
        generate_tts(text="")


def test_generate_tts_unsupported_engine_error():
    """Test error handling for invalid engine name."""
    with pytest.raises(ValueError, match="Unsupported TTS engine"):
        generate_tts(text="Sample text", model_name="invalid_engine")
