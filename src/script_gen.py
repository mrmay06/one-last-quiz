"""Gemini 2.5 Flash → puzzle JSON."""
from __future__ import annotations

import json
import logging
import re
from typing import Any

import google.generativeai as genai

from src import config
from src.puzzle_store import recent_hashes
from src.utils import retry

log = logging.getLogger(__name__)


def _load_system_prompt() -> str:
    return (config.PROMPTS_DIR / "script_system.md").read_text()


def _strip_fences(text: str) -> str:
    """Gemini sometimes wraps JSON in ```json fences despite instructions."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


@retry(attempts=config.SCRIPT_GEN_RETRIES, base_delay=2.0, exceptions=(json.JSONDecodeError, ValueError))
def _generate_once(template: str, used: list[str]) -> dict[str, Any]:
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=config.GEMINI_TEXT_MODEL,
        system_instruction=_load_system_prompt(),
    )
    user_prompt = (
        f"Template type: {template}\n"
        f"Recently used puzzle hashes (avoid semantic duplicates): {used}\n\n"
        f"Generate ONE puzzle as a JSON object now."
    )
    resp = model.generate_content(
        user_prompt,
        generation_config={"temperature": 0.9, "response_mime_type": "application/json"},
    )
    raw = _strip_fences(resp.text or "")
    if not raw:
        raise ValueError("empty response from Gemini")
    data = json.loads(raw)
    _validate(data, template)
    return data


def _validate(data: dict[str, Any], template: str) -> None:
    required = {"template", "hook", "puzzle_text", "answer", "voiceover_script", "youtube_title", "youtube_description", "tags"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"missing keys: {missing}")
    if len(data["youtube_title"]) > 70:
        raise ValueError(f"youtube_title too long ({len(data['youtube_title'])} chars)")
    words = len(data["voiceover_script"].split())
    if words < 40 or words > 110:
        raise ValueError(f"voiceover_script word count out of range: {words}")
    if template == "imessage" and not data.get("messages"):
        raise ValueError("imessage template requires messages[]")
    if template == "iq" and not data.get("iq_data"):
        raise ValueError("iq template requires iq_data{}")
    if template == "atmospheric" and not data.get("image_prompts"):
        raise ValueError("atmospheric template requires image_prompts[]")


def generate(template: str) -> dict[str, Any]:
    """Generate a puzzle JSON for the given template, avoiding recent duplicates."""
    used = recent_hashes()
    log.info("Generating script: template=%s, %d recent hashes excluded", template, len(used))
    data = _generate_once(template, used)
    log.info("Script generated: title=%s", data["youtube_title"])
    return data


if __name__ == "__main__":
    config.setup_logging()
    out = generate("atmospheric")
    print(json.dumps(out, indent=2))
