"""Atomic image preparation and overlay functions for video canvases."""

from pathlib import Path
from typing import Any

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

from src.core.media_utils import ensure_nonempty_output, workspace_path

ASPECT_RATIO_DIMENSIONS = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
    "4:3": (1440, 1080),
    "21:9": (2560, 1080),
}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def format_image_aspect_ratio(image_path: str, output_path: str, aspect_ratio: str) -> dict[str, Any]:
    """Fit an image into a standard video canvas using letterbox padding."""
    if aspect_ratio not in ASPECT_RATIO_DIMENSIONS:
        raise ValueError(f"Unsupported aspect ratio: {aspect_ratio}. Use one of {sorted(ASPECT_RATIO_DIMENSIONS)}")
    source = workspace_path(image_path, must_exist=True)
    destination = workspace_path(output_path, output=True)
    if destination.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError("Image output must use .jpg, .jpeg, .png, or .webp")
    width, height = ASPECT_RATIO_DIMENSIONS[aspect_ratio]
    try:
        with Image.open(source) as image:
            fitted = ImageOps.contain(image.convert("RGB"), (width, height), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (width, height), "black")
            canvas.paste(fitted, ((width - fitted.width) // 2, (height - fitted.height) // 2))
            canvas.save(destination, quality=95)
    except OSError as exc:
        raise ValueError(f"Invalid image: {source}") from exc
    return {"status": "success", **ensure_nonempty_output(destination), "width": width, "height": height, "aspect_ratio": aspect_ratio}


def _get_font(font_size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    candidate_fonts = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for font_path in candidate_fonts:
        if Path(font_path).exists():
            try:
                return ImageFont.truetype(font_path, font_size)
            except Exception:
                pass
    try:
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def add_text_overlay(
    image_path: str,
    output_path: str,
    text: str,
    position: str = "bottom",
    font_size: int = 64,
    color: str = "white",
    background: bool = True,
) -> dict[str, Any]:
    """Add a predictable caption/title overlay to a still image."""
    if not text.strip():
        raise ValueError("Overlay text cannot be empty")
    position_lower = position.lower().strip()
    if position_lower not in {"top", "center", "bottom", "lower_third"}:
        raise ValueError("position must be top, center, bottom, or lower_third")
    source = workspace_path(image_path, must_exist=True)
    destination = workspace_path(output_path, output=True)
    try:
        with Image.open(source) as image:
            canvas = image.convert("RGBA")
            draw = ImageDraw.Draw(canvas)
            font = _get_font(font_size)
            bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (canvas.width - text_width) // 2
            if position_lower == "top":
                y = 40
            elif position_lower == "center":
                y = (canvas.height - text_height) // 2
            elif position_lower == "lower_third":
                y = int(canvas.height * 0.72)
            else:  # bottom
                y = canvas.height - text_height - 40
            if background:
                draw.rounded_rectangle((x - 24, y - 16, x + text_width + 24, y + text_height + 16), radius=12, fill=(0, 0, 0, 160))
            draw.multiline_text((x, y), text, font=font, fill=ImageColor.getrgb(color), align="center")
            canvas.convert("RGB").save(destination, quality=95)
    except OSError as exc:
        raise ValueError(f"Could not apply overlay to image: {source}") from exc
    return {"status": "success", **ensure_nonempty_output(destination), "text": text, "position": position_lower}

