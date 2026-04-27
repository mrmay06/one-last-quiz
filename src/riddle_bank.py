"""Riddle bank: pick an unused riddle, mark it used, alert when running low.

Bank is `data/riddle_bank.json`. Used IDs live in `data/used_puzzles.json` under
the existing `puzzles` list (we add `riddle_id` to each entry).

The bank is the canonical source of puzzle CONTENT. GPT-4o is responsible for
turning a bank riddle into Shorts script copy — never inventing puzzles.
"""
from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import Any

from src import config
from src.utils import read_json

log = logging.getLogger(__name__)

LOW_WATER_MARK = 20  # warn when fewer than N unused riddles remain

BANK_FILE = config.DATA_DIR / "riddle_bank.json"
IMPORTS_DIR = config.DATA_DIR / "riddle_bank_imports"


def _load_bank() -> list[dict[str, Any]]:
    """Load the main bank + any user-scraped imports from riddle_bank_imports/."""
    main = read_json(BANK_FILE, default={"riddles": []}).get("riddles", [])
    extra: list[dict[str, Any]] = []
    if IMPORTS_DIR.exists():
        for f in sorted(IMPORTS_DIR.glob("*.json")):
            data = read_json(f, default=[])
            if isinstance(data, list):
                extra.extend(data)
            elif isinstance(data, dict) and "riddles" in data:
                extra.extend(data["riddles"])
    # Dedupe by id; main wins
    seen = {r["id"] for r in main if "id" in r}
    for r in extra:
        if r.get("id") and r["id"] not in seen:
            main.append(r)
            seen.add(r["id"])
        elif not r.get("id"):
            # Auto-assign id for imported riddles missing one
            new_id = f"imp_{len(main):04d}"
            r["id"] = new_id
            main.append(r)
            seen.add(new_id)
    return main


def _used_riddle_ids() -> set[str]:
    log_data = read_json(config.USED_PUZZLES_FILE, default={"puzzles": []})
    return {p.get("riddle_id") for p in log_data.get("puzzles", []) if p.get("riddle_id")}


def stats() -> dict[str, int]:
    bank = _load_bank()
    used = _used_riddle_ids()
    return {"total": len(bank), "used": len(used), "available": len(bank) - len(used)}


def pick(template: str) -> dict[str, Any]:
    """Pick a random unused riddle compatible with `template`."""
    bank = _load_bank()
    used = _used_riddle_ids()
    candidates = [
        r for r in bank
        if r["id"] not in used and template in r.get("compatible_templates", [])
    ]
    if not candidates:
        # Fall back to ALL bank riddles compatible with template (re-use is OK if exhausted)
        log.warning("No unused riddles for template=%s, allowing reuse", template)
        candidates = [r for r in bank if template in r.get("compatible_templates", [])]
    if not candidates:
        raise RuntimeError(f"No riddles in bank compatible with template={template!r}")
    chosen = random.choice(candidates)
    s = stats()
    log.info(
        "Riddle bank: picked %s (%s) — %d/%d available",
        chosen["id"], chosen["type"], s["available"], s["total"],
    )
    if s["available"] < LOW_WATER_MARK:
        log.warning(
            "Riddle bank running low (%d unused). Time to add more — "
            "run scripts/refill_bank.py or drop a JSON into data/riddle_bank_imports/",
            s["available"],
        )
    return chosen


if __name__ == "__main__":
    config.setup_logging()
    print("Bank stats:", stats())
    for t in config.TEMPLATE_CYCLE:
        print(f"\nSample for {t}:")
        try:
            r = pick(t)
            print(f"  {r['id']} [{r['type']}]: {r['question'][:80]}...")
        except RuntimeError as e:
            print(f"  ERROR: {e}")
