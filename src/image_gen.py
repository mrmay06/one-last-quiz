"""Pollinations image generation. No fallback (per project spec).

Pollinations free tier caps native output at ~576×1024 portrait. We request a
generation, then upscale locally to 1080×1920 with Lanczos so Remotion gets a
true vertical-format asset. Since these are atmospheric backgrounds (with Ken
Burns + dark overlay), Lanczos upscaling is visually fine.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path
from urllib.parse import quote

import requests
from PIL import Image

from src import config
from src.utils import ensure_run_dir, retry

log = logging.getLogger(__name__)

POLLINATIONS_BASE = "https://gen.pollinations.ai/image"
TARGET_W, TARGET_H = 1080, 1920


def _validate_and_upscale(raw: bytes, out_path: Path) -> None:
    """Validate the response is a real image, then upscale + save as PNG."""
    if len(raw) < 10_000:
        raise ValueError(f"image too small ({len(raw)} bytes) — likely an error placeholder")
    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except Exception as exc:
        raise ValueError(f"invalid image: {exc}") from exc

    img = img.convert("RGB")
    if img.size != (TARGET_W, TARGET_H):
        log.info("Upscaling %s → %dx%d", img.size, TARGET_W, TARGET_H)
        img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    img.save(out_path, format="PNG", optimize=True)

    if out_path.stat().st_size < config.MIN_IMAGE_BYTES:
        raise ValueError(f"final image suspiciously small: {out_path.stat().st_size} bytes")


@retry(attempts=config.POLLINATIONS_RETRIES + 1, base_delay=2.0, exceptions=(requests.RequestException, ValueError))
def _pollinations(prompt: str, out_path: Path, seed: int) -> None:
    url = (
        f"{POLLINATIONS_BASE}/{quote(prompt)}"
        f"?width={TARGET_W}&height={TARGET_H}&model=klein&seed={seed}&enhance=false&nologo=true"
    )
    if config.POLLINATIONS_API_KEY:
        url += f"&key={config.POLLINATIONS_API_KEY}"
    headers = {}
    if config.POLLINATIONS_API_KEY:
        headers["Authorization"] = f"Bearer {config.POLLINATIONS_API_KEY}"
    log.info("Pollinations: %s", prompt[:60])
    resp = requests.get(url, headers=headers, timeout=180)
    resp.raise_for_status()
    if not resp.headers.get("content-type", "").startswith("image"):
        raise ValueError(f"non-image response: {resp.headers.get('content-type')}")
    _validate_and_upscale(resp.content, out_path)


def _pexels_fallback(prompt: str, out_path: Path) -> None:
    """Fallback to Pexels stock photo API if Pollinations fails.
    Since Pexels expects keywords, we take the first 3 meaningful words of the prompt.
    """
    if not config.PEXELS_API_KEY:
        raise ValueError("Pexels fallback failed: PEXELS_API_KEY not set")

    # Simple heuristic to get keywords from the start of the cinematic prompt
    words = [w for w in prompt.split() if len(w) > 3][:3]
    query = " ".join(words).replace(",", "").replace(".", "")
    if not query:
        query = "mystery"

    url = f"https://api.pexels.com/v1/search?query={quote(query)}&orientation=portrait&per_page=1"
    headers = {"Authorization": config.PEXELS_API_KEY}
    
    log.info("Pexels fallback search: '%s'", query)
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    if not data.get("photos"):
        log.warning("Pexels returned no photos for '%s', falling back to 'dark background'", query)
        url = f"https://api.pexels.com/v1/search?query=dark%20background&orientation=portrait&per_page=1"
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("photos"):
            raise ValueError("Pexels ultimate fallback failed (no photos)")

    photo_url = data["photos"][0]["src"]["portrait"]
    log.info("Pexels downloading: %s", photo_url)
    
    img_resp = requests.get(photo_url, timeout=60)
    img_resp.raise_for_status()
    _validate_and_upscale(img_resp.content, out_path)


def generate_images(prompts: list[str]) -> list[Path]:
    """Generate one image per prompt. Writes to remotion/public/run/.
    Returns list of paths *relative* to the public dir (e.g. 'run/image_1.png')
    so Remotion's static server can resolve them.
    """
    run_dir = ensure_run_dir()
    paths: list[Path] = []
    for i, prompt in enumerate(prompts, start=1):
        out = run_dir / f"image_{i}.png"
        seed = (hash(prompt) & 0x7FFFFFFF) % 10_000_000
        try:
            _pollinations(prompt, out, seed)
        except Exception as exc:
            log.warning("Pollinations failed (%s). Falling back to Pexels...", exc)
            if config.PEXELS_API_KEY:
                _pexels_fallback(prompt, out)
            else:
                raise
        paths.append(out)
    return paths
