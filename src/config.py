"""Central configuration. Reads env vars, exposes constants."""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
ROOT = Path(__file__).resolve().parent.parent
TMP_DIR = ROOT / "tmp"
DATA_DIR = ROOT / "data"
ASSETS_DIR = ROOT / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
PROMPTS_DIR = ROOT / "prompts"
REMOTION_DIR = ROOT / "remotion"

USED_PUZZLES_FILE = DATA_DIR / "used_puzzles.json"
LAST_TEMPLATE_FILE = DATA_DIR / "last_template.txt"
ERRORS_LOG = DATA_DIR / "errors.log"

# --- API keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")

# YouTube
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")

# Facebook (Phase 2 — disabled by default)
FACEBOOK_ENABLED = os.getenv("FACEBOOK_ENABLED", "false").lower() == "true"
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")

# --- Models ---
GEMINI_TEXT_MODEL = "gemini-2.5-flash"
GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"
GEMINI_TTS_MODEL = "gemini-2.5-flash-preview-tts"

# Locked default voice — first match from priority list per voice_style.md
DEFAULT_VOICE = "Charon"

# --- Pipeline ---
TEMPLATE_CYCLE = ["atmospheric", "imessage", "iq"]
RECENT_HASH_WINDOW = 30  # how many recent puzzles Gemini sees to avoid duplicates
PUZZLE_HASH_LEN = 16  # SHA256 prefix length

# Validation thresholds
MIN_IMAGE_BYTES = 50_000
MIN_VOICE_SECONDS = 2.0

# Retries
SCRIPT_GEN_RETRIES = 3
POLLINATIONS_RETRIES = 1
VOICE_RETRIES = 1
DUPLICATE_RETRIES = 3

# Render
RENDER_CONCURRENCY = int(os.getenv("RENDER_CONCURRENCY", "1"))

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def setup_logging() -> None:
    """Configure root logger. Call once at entry point."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
