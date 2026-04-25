"""Random BG music picker from local library."""
from __future__ import annotations

import logging
import random
import shutil
from pathlib import Path

from src import config
from src.utils import ensure_tmp

log = logging.getLogger(__name__)


def pick_track() -> Path:
    """Copy a random mp3 from assets/music/ to tmp/bg_music.mp3 and return path."""
    tracks = list(config.MUSIC_DIR.glob("*.mp3"))
    if not tracks:
        raise FileNotFoundError(
            f"No .mp3 tracks in {config.MUSIC_DIR}. "
            "Add Pixabay tracks to assets/music/ before running."
        )
    chosen = random.choice(tracks)
    out = ensure_tmp() / "bg_music.mp3"
    shutil.copy2(chosen, out)
    log.info("BG music picked: %s", chosen.name)
    return out
