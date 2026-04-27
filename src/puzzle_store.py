"""Read/write used puzzle hashes + template rotation state."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src import config
from src.utils import puzzle_hash, read_json, write_json


def load_used() -> list[dict[str, Any]]:
    data = read_json(config.USED_PUZZLES_FILE, default={"puzzles": []})
    return data.get("puzzles", [])


def append(text: str, title: str, video_id: str | None = None, riddle_id: str | None = None) -> str:
    h = puzzle_hash(text)
    used = load_used()
    used.append(
        {
            "hash": h,
            "title": title,
            "video_id": video_id,
            "riddle_id": riddle_id,
            "date": datetime.now(timezone.utc).isoformat(),
        }
    )
    write_json(config.USED_PUZZLES_FILE, {"puzzles": used})
    return h


def next_template() -> str:
    """Rotate through TEMPLATE_CYCLE based on data/last_template.txt."""
    cycle = config.TEMPLATE_CYCLE
    last = config.LAST_TEMPLATE_FILE.read_text().strip() if config.LAST_TEMPLATE_FILE.exists() else ""
    if last in cycle:
        idx = (cycle.index(last) + 1) % len(cycle)
    else:
        idx = 0
    return cycle[idx]


def commit_template(template: str) -> None:
    config.LAST_TEMPLATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.LAST_TEMPLATE_FILE.write_text(template)
