"""Generate an atmospheric YouTube thumbnail (1080x1920 JPEG) using Pillow."""
from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from src.utils import ensure_tmp

log = logging.getLogger(__name__)

W, H = 1080, 1920


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Load a system bold font. Falls back to Pillow default if unavailable."""
    candidates = [
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVu-Sans-Bold.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text so each line fits within max_width pixels."""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join([*current, word])
        bbox = font.getbbox(trial)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _add_dark_gradient(img: Image.Image, side: str = "bottom") -> Image.Image:
    """Add a dark gradient overlay for text legibility."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    if side == "bottom":
        for y in range(H):
            alpha = int(220 * max(0, (y - H * 0.45) / (H * 0.55)))
            draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    base = img.convert("RGBA")
    return Image.alpha_composite(base, overlay).convert("RGB")


def _atmospheric(image_path: Path) -> Image.Image:
    bg = Image.open(image_path).convert("RGB")
    bg = bg.resize((W, H), Image.LANCZOS)
    blurred = bg.filter(ImageFilter.GaussianBlur(radius=2))
    bg = Image.blend(bg, blurred, 0.3)
    bg = _add_dark_gradient(bg, side="bottom")
    return bg


def _fallback_backdrop() -> Image.Image:
    bg = Image.new("RGB", (W, H), (10, 10, 15))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([(W * 0.1, H * 0.55), (W * 0.9, H * 1.15)], fill=(229, 9, 20, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=80))
    return Image.alpha_composite(bg.convert("RGBA"), glow).convert("RGB")


def _draw_hook(img: Image.Image, hook: str) -> Image.Image:
    draw = ImageDraw.Draw(img)
    font = _font(140, bold=True)
    max_text_width = int(W * 0.85)

    while True:
        lines = _wrap(hook, font, max_text_width)
        if len(lines) <= 2 or font.size <= 70:
            break
        font = _font(font.size - 12, bold=True)

    line_h = font.size + 16
    block_h = line_h * len(lines)
    start_y = int(H * 0.62) - block_h // 2

    for i, line in enumerate(lines):
        bbox = font.getbbox(line)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w) // 2
        y = start_y + i * line_h
        for dx, dy in ((0, 4), (0, 6)):
            draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 220))
        draw.text((x, y), line, font=font, fill=(245, 245, 245))

    return img


def generate(hook: str, image_path: Path | None = None) -> Path:
    """Generate a thumbnail for the atmospheric channel. Returns path to JPEG."""
    img = _atmospheric(image_path) if image_path else _fallback_backdrop()
    img = _draw_hook(img, hook)

    out = ensure_tmp() / "thumbnail.jpg"
    img.save(out, "JPEG", quality=88, optimize=True)
    log.info("Thumbnail: %s (%d KB)", out, out.stat().st_size // 1024)
    return out
