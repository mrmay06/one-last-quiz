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
REMOTION_PUBLIC = REMOTION_DIR / "public"
REMOTION_RUN_DIR = REMOTION_PUBLIC / "run"  # Generated assets land here so Remotion can serve them

USED_PUZZLES_FILE = DATA_DIR / "used_puzzles.json"
LAST_TEMPLATE_FILE = DATA_DIR / "last_template.txt"
ERRORS_LOG = DATA_DIR / "errors.log"

# --- API keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# YouTube
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")

# Facebook (optional)
FACEBOOK_ENABLED = os.getenv("FACEBOOK_ENABLED", "false").lower() == "true"
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")

# --- Models ---
OPENAI_TEXT_MODEL = "gpt-4o"
GEMINI_TTS_MODEL = "gemini-2.5-flash-preview-tts"
DEFAULT_VOICE = "Fenrir"

# Lower value = more natural human delivery.
VOICE_SPEED = 1.05

# --- Pipeline ---
# V2 intentionally ships a single atmospheric template.
TEMPLATE_CYCLE = ["atmospheric"]
PUZZLE_HASH_LEN = 16  # SHA256 prefix length

# Validation thresholds
MIN_IMAGE_BYTES = 50_000
MIN_VOICE_SECONDS = 2.0

# Retries
SCRIPT_GEN_RETRIES = 3
POLLINATIONS_RETRIES = 1
VOICE_RETRIES = 1

# Render
FPS = 30
RENDER_BUFFER_SECONDS = 1.5  # extra after voice ends for cliffhanger to land
MIN_VIDEO_SECONDS = 15.0
MAX_VIDEO_SECONDS = 60.0  # safety rail only — not an editorial limit

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def setup_logging() -> None:
    """Configure root logger. Call once at entry point."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
