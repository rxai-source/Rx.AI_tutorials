import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    from fastmcp import FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

from src.core.audio_engine import generate_tts as core_generate_tts

# Initialize FastMCP server instance named "media_tools"
mcp = FastMCP("media_tools")


@mcp.tool()
def generate_tts(
    text: str,
    output_path: Optional[str] = None,
    model_name: Optional[str] = "gtts",
    voice: Optional[str] = "en",
    return_bytes: bool = False,
) -> Dict[str, Any]:
    """
    Generates speech audio from text using specified TTS engine and saves it to output path.

    Args:
        text (str): The text content to convert to speech.
        output_path (str, optional): Destination file path for saved audio file.
        model_name (str, optional): TTS engine backend ('gtts', 'pyttsx3'). Default: 'gtts'.
        voice (str, optional): Language or voice identifier (e.g. 'en', 'es'). Default: 'en'.
        return_bytes (bool): Whether to include base64 audio stream data in response.

    Returns:
        dict: Standardized payload containing output file path, metadata, and status.
    """
    return core_generate_tts(
        text=text,
        output_path=output_path,
        model_name=model_name,
        voice=voice,
        return_bytes=return_bytes,
    )


if __name__ == "__main__":
    # Run FastMCP server
    mcp.run()
