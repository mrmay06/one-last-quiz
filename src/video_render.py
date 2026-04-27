"""Invoke Remotion to render the atmospheric MP4."""
from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from src import config
from src.utils import ensure_tmp

log = logging.getLogger(__name__)
ATMOSPHERIC_COMPOSITION = "AtmosphericPuzzle"


def render(template: str, props: dict[str, Any]) -> Path:
    """Render the video. Returns path to output mp4."""
    if template != "atmospheric":
        raise ValueError(f"Unsupported template: {template}")

    out = ensure_tmp() / "output.mp4"
    cmd = [
        "node",
        "render.mjs",
        ATMOSPHERIC_COMPOSITION,
        str(out.resolve()),
        json.dumps(props),
    ]
    log.info("Rendering: composition=%s", ATMOSPHERIC_COMPOSITION)
    result = subprocess.run(
        cmd,
        cwd=config.REMOTION_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log.error("Remotion stderr: %s", result.stderr)
        raise RuntimeError(f"Remotion render failed (exit {result.returncode})")
    if not out.exists():
        raise RuntimeError(f"Render reported success but {out} missing")
    log.info("Rendered: %s (%.1f MB)", out, out.stat().st_size / 1_048_576)
    return out
