"""Script generation via OpenAI GPT-4o for the atmospheric template.

GPT-4o rewrites a bank riddle into Shorts copy plus a matching image plan.
It does NOT invent puzzles. Puzzle content comes from `data/riddle_bank.json`.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from openai import OpenAI

from src import config, riddle_bank
from src.utils import retry

log = logging.getLogger(__name__)

_FORBIDDEN = {
    "stretched", "endless", "pristine", "barren", "motionless",
    "gracefully", "shimmering", "cascading", "desolate", "eerily",
    "silent witness", "replay from", "watch from second",
}


def _load_system_prompt() -> str:
    return (config.PROMPTS_DIR / "script_system.md").read_text()


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


@retry(attempts=config.SCRIPT_GEN_RETRIES, base_delay=2.0, exceptions=(json.JSONDecodeError, ValueError))
def _generate_once(template: str, riddle: dict[str, Any]) -> dict[str, Any]:
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    user_msg = (
        f"Template: {template}\n"
        f"Source riddle:\n{json.dumps(riddle, indent=2)}\n\n"
        "Rewrite this riddle into a Shorts script. Follow ALL the rules in the system prompt — "
        "especially: fixed order (hook, riddle/setup, outro/CTA), start the voiceover with a stop-scroll hook "
        "(matches `hook` field verbatim), no forbidden words, short sentences, no answer reveal, "
        "and a riddle-specific 3-4 image plan."
    )
    resp = client.chat.completions.create(
        model=config.OPENAI_TEXT_MODEL,
        messages=[
            {"role": "system", "content": _load_system_prompt()},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.5,
        response_format={"type": "json_object"},
    )
    raw = _strip_fences(resp.choices[0].message.content or "")
    if not raw:
        raise ValueError("empty response from GPT")
    data = json.loads(raw)
    _validate(data, template, riddle)
    return data


def _validate(data: dict[str, Any], template: str, riddle: dict[str, Any]) -> None:
    required = {
        "template", "hook", "puzzle_text", "answer", "voiceover_script",
        "cta", "pinned_comment", "youtube_title", "youtube_description", "tags",
        "image_prompts", "facebook_caption", "facebook_hashtags",
    }
    missing = required - data.keys()
    if missing:
        raise ValueError(f"missing keys: {missing}")
    if template != "atmospheric":
        raise ValueError(f"unsupported template: {template}")
    if data.get("template") != "atmospheric":
        raise ValueError(f"model returned unexpected template: {data.get('template')}")
    if len(data["youtube_title"]) > 70:
        raise ValueError(f"youtube_title too long ({len(data['youtube_title'])} chars)")

    voice = data["voiceover_script"].strip()
    words = len(voice.split())
    if words > 110:
        raise ValueError(f"voiceover word count {words} exceeds max")

    voice_lower = voice.lower()
    hits = [w for w in _FORBIDDEN if w in voice_lower]
    if hits:
        raise ValueError(f"forbidden words present: {hits}")

    def extract_words(text: str) -> set[str]:
        return {w.strip(".,!?\"'()") for w in text.lower().split() if len(w) > 3}

    question_words = extract_words(riddle["question"])
    answer_words = extract_words(riddle["answer"])
    
    unique_answer_words = answer_words - question_words

    spoiler_hits = sum(1 for w in unique_answer_words if w in voice_lower)
    if unique_answer_words and spoiler_hits >= max(2, len(unique_answer_words) // 2):
        raise ValueError(
            f"voiceover leaks answer ({spoiler_hits}/{len(unique_answer_words)} unique answer words)"
        )

    prompts = data["image_prompts"]
    if not isinstance(prompts, list) or len(prompts) < 3 or len(prompts) > 4:
        raise ValueError("script requires 3-4 image_prompts")
    first_prompt = prompts[0] if prompts else {}
    if isinstance(first_prompt, dict) and first_prompt.get("cut_at_second") != 0:
        raise ValueError("first image prompt must start at cut_at_second=0")

    tags = data.get("tags", [])
    if len(tags) < 20:
        raise ValueError(f"tags too few ({len(tags)}), need at least 20")


def generate(template: str) -> dict[str, Any]:
    """Pick a riddle from the bank and rewrite it into an atmospheric Shorts script."""
    riddle = riddle_bank.pick(template)
    log.info("Script: rewriting riddle %s for template=%s", riddle["id"], template)
    data = _generate_once(template, riddle)
    data["riddle_id"] = riddle["id"]
    log.info(
        "Script ready: %d-word voice, title=%s",
        len(data["voiceover_script"].split()), data["youtube_title"],
    )
    return data


if __name__ == "__main__":
    config.setup_logging()
    out = generate("atmospheric")
    print(json.dumps(out, indent=2))
