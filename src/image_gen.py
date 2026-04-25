"""Pollinations primary, Gemini Image fallback."""
from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import quote

import requests
from PIL import Image

from src import config
from src.utils import ensure_tmp, retry

log = logging.getLogger(__name__)

POLLINATIONS_BASE = "https://gen.pollinations.ai/image"


def _validate_image(path: Path) -> None:
    if not path.exists() or path.stat().st_size < config.MIN_IMAGE_BYTES:
        raise ValueError(f"image too small: {path} ({path.stat().st_size if path.exists() else 0} bytes)")
    try:
        with Image.open(path) as img:
            img.verify()
    except Exception as exc:
        raise ValueError(f"invalid image at {path}: {exc}") from exc


@retry(attempts=config.POLLINATIONS_RETRIES + 1, base_delay=2.0, exceptions=(requests.RequestException, ValueError))
def _pollinations(prompt: str, out_path: Path, seed: int) -> None:
    url = (
        f"{POLLINATIONS_BASE}/{quote(prompt)}"
        f"?width=1080&height=1920&model=flux&seed={seed}&enhance=false"
    )
    if config.POLLINATIONS_API_KEY:
        url += f"&key={config.POLLINATIONS_API_KEY}"
    log.info("Pollinations: %s", prompt[:60])
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    _validate_image(out_path)


def _gemini_fallback(prompt: str, out_path: Path) -> None:
    """Use Gemini Image API when Pollinations fails."""
    import google.generativeai as genai

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.GEMINI_IMAGE_MODEL)
    log.info("Gemini Image fallback: %s", prompt[:60])
    resp = model.generate_content(prompt)
    # Gemini image responses include inline_data parts
    for part in resp.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
            out_path.write_bytes(part.inline_data.data)
            _validate_image(out_path)
            return
    raise RuntimeError("Gemini returned no image data")


def generate_images(prompts: list[str]) -> list[Path]:
    """Generate one image per prompt. Returns list of file paths."""
    tmp = ensure_tmp()
    paths: list[Path] = []
    for i, prompt in enumerate(prompts, start=1):
        out = tmp / f"image_{i}.png"
        seed = (hash(prompt) & 0x7FFFFFFF) % 10_000_000
        try:
            _pollinations(prompt, out, seed)
        except Exception as exc:
            log.warning("Pollinations failed for prompt %d: %s — falling back to Gemini", i, exc)
            _gemini_fallback(prompt, out)
        paths.append(out)
    return paths
