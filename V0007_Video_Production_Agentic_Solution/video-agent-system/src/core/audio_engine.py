import asyncio
import base64
import hashlib
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from src.config import DEFAULT_TTS_MODEL, DEFAULT_TTS_VOICE, OUTPUT_DIR

logger = logging.getLogger(__name__)


def _edge_tts_provider(text: str, output_file: str, voice: str) -> str:
    """TTS synthesis using Microsoft Edge TTS (high quality, reliable)."""
    try:
        import edge_tts
    except ImportError:
        raise ImportError(
            "edge-tts package is not installed. Run 'pip install edge-tts' to use edge-tts."
        )

    # Use specified voice or default to clear neural voice
    voice_name = voice if voice and "-" in voice else "en-US-AvaNeural"

    async def _async_generate():
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(output_file)

    asyncio.run(_async_generate())
    return output_file


def _gtts_provider(text: str, output_file: str, voice: str) -> str:
    """TTS synthesis using gTTS (Google Text-to-Speech) with automatic fallback."""
    try:
        from gtts import gTTS
    except ImportError:
        raise ImportError(
            "gTTS package is not installed. Run 'pip install gTTS' to use the gTTS engine."
        )

    lang = voice if voice and len(voice) <= 5 and "-" not in voice else "en"
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(output_file)
        return output_file
    except Exception as e:
        logger.warning(f"gTTS API failed ({e}). Falling back to edge-tts/pyttsx3...")
        # Graceful fallback to edge-tts if installed, otherwise pyttsx3
        try:
            return _edge_tts_provider(text, output_file, voice)
        except Exception:
            return _pyttsx3_provider(text, output_file, voice)


def _pyttsx3_provider(text: str, output_file: str, voice: str) -> str:
    """Offline TTS synthesis using pyttsx3."""
    try:
        import pyttsx3
    except ImportError:
        raise ImportError(
            "pyttsx3 package is not installed. Run 'pip install pyttsx3' to use pyttsx3."
        )

    engine = pyttsx3.init()
    if voice:
        voices = engine.getProperty("voices")
        for v in voices:
            if voice.lower() in v.id.lower() or voice.lower() in v.name.lower():
                engine.setProperty("voice", v.id)
                break
    engine.save_to_file(text, output_file)
    engine.runAndWait()
    return output_file


# Registry of available TTS engines for easy extension
TTS_PROVIDERS = {
    "gtts": _gtts_provider,
    "google": _gtts_provider,
    "edge-tts": _edge_tts_provider,
    "edgetts": _edge_tts_provider,
    "edge": _edge_tts_provider,
    "pyttsx3": _pyttsx3_provider,
}


def generate_tts(
    text: str,
    output_path: Optional[str] = None,
    model_name: Optional[str] = None,
    voice: Optional[str] = None,
    return_bytes: bool = False,
) -> Dict[str, Any]:
    """
    Generates text-to-speech audio from text and saves it to output_path.

    Args:
        text (str): The text content to convert to speech.
        output_path (str, optional): Destination file path for saved audio. 
                                     Defaults to workspace/output directory.
        model_name (str, optional): TTS engine model ('edge-tts', 'gtts', 'pyttsx3'). 
                                    Defaults to 'gtts' (with fallback).
        voice (str, optional): Voice or language identifier (e.g. 'en', 'en-US-AvaNeural'). 
                               Defaults to 'en'.
        return_bytes (bool): If True, returns base64 encoded audio stream in response.

    Returns:
        Dict[str, Any]: Dictionary containing status, output file path, metadata, 
                        and optional audio bytes stream.
    """
    if not text or not text.strip():
        raise ValueError("Text input for TTS cannot be empty.")

    engine_name = (model_name or DEFAULT_TTS_MODEL).lower()
    voice_code = voice or DEFAULT_TTS_VOICE

    if engine_name not in TTS_PROVIDERS:
        supported = ", ".join(TTS_PROVIDERS.keys())
        raise ValueError(
            f"Unsupported TTS engine: '{engine_name}'. Supported engines: [{supported}]"
        )

    # Determine destination file path
    if output_path:
        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
        timestamp = int(time.time())
        file_ext = "wav" if engine_name == "pyttsx3" else "mp3"
        filename = f"tts_{timestamp}_{text_hash}.{file_ext}"
        out_file = OUTPUT_DIR / filename

    # Execute TTS provider
    provider_fn = TTS_PROVIDERS[engine_name]
    generated_file = provider_fn(text=text, output_file=str(out_file), voice=voice_code)

    file_size = os.path.getsize(generated_file) if os.path.exists(generated_file) else 0

    audio_b64 = None
    if return_bytes and os.path.exists(generated_file):
        with open(generated_file, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")

    return {
        "status": "success",
        "text": text,
        "output_path": str(out_file),
        "model_name": engine_name,
        "voice": voice_code,
        "format": out_file.suffix.lstrip(".").lower(),
        "file_size_bytes": file_size,
        "audio_bytes_b64": audio_b64,
    }
