#!/usr/bin/env python3
"""Check if a riddle has already been uploaded.

Usage:
    python scripts/check_riddle.py                    # show bank stats
    python scripts/check_riddle.py r0022              # check by riddle id
    python scripts/check_riddle.py "man dies field"   # fuzzy match by puzzle text
    python scripts/check_riddle.py --used             # list all used riddles
    python scripts/check_riddle.py --available 10     # show 10 unused riddle IDs
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make src importable when run from project root or scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import riddle_bank
from src.config import USED_PUZZLES_FILE
from src.utils import read_json


def show_stats() -> None:
    s = riddle_bank.stats()
    print(f"Bank: {s['total']} total · {s['used']} used · {s['available']} available")


def check_by_id(rid: str) -> None:
    bank = riddle_bank._load_bank()
    used = riddle_bank._used_riddle_ids()
    match = next((r for r in bank if r["id"] == rid), None)
    if not match:
        print(f"❌ Riddle '{rid}' not found in bank.")
        return
    print(f"📖 {match['id']} [{match['type']}]: {match['question'][:120]}")
    if rid in used:
        log = read_json(USED_PUZZLES_FILE, default={"puzzles": []}).get("puzzles", [])
        entry = next((p for p in log if p.get("riddle_id") == rid), {})
        print(f"  ✅ ALREADY USED — {entry.get('date', 'unknown date')}")
        if entry.get("video_id"):
            print(f"     YouTube: https://youtube.com/shorts/{entry['video_id']}")
    else:
        print("  🟢 NOT YET USED")


def fuzzy_search(query: str) -> None:
    bank = riddle_bank._load_bank()
    used = riddle_bank._used_riddle_ids()
    q = query.lower()
    matches = [r for r in bank if q in r["question"].lower() or q in r.get("answer", "").lower()]
    if not matches:
        print(f"No riddles match '{query}'.")
        return
    print(f"Found {len(matches)} match{'es' if len(matches) > 1 else ''}:\n")
    for r in matches:
        marker = "✅ USED" if r["id"] in used else "🟢 free"
        print(f"  {marker}  {r['id']} [{r['type']}]: {r['question'][:90]}...")


def list_used() -> None:
    log = read_json(USED_PUZZLES_FILE, default={"puzzles": []}).get("puzzles", [])
    used_riddles = [p for p in log if p.get("riddle_id")]
    if not used_riddles:
        print("No riddles used yet.")
        return
    print(f"{len(used_riddles)} riddles used:\n")
    for p in used_riddles[-30:]:
        print(f"  {p['riddle_id']} · {p['date'][:10]} · {p['title']}")


def list_available(n: int) -> None:
    bank = riddle_bank._load_bank()
    used = riddle_bank._used_riddle_ids()
    free = [r for r in bank if r["id"] not in used]
    print(f"{len(free)} unused riddles. Showing {min(n, len(free))}:\n")
    for r in free[:n]:
        templates = ",".join(r.get("compatible_templates", []))
        print(f"  {r['id']} [{r['type']}] ({templates}): {r['question'][:80]}...")


def main() -> int:
    parser = argparse.ArgumentParser(description="Riddle bank dedup checker")
    parser.add_argument("query", nargs="?", help="riddle id (e.g. r0022) or fuzzy text search")
    parser.add_argument("--used", action="store_true", help="list all used riddles")
    parser.add_argument("--available", type=int, metavar="N", help="list N unused riddles")
    args = parser.parse_args()

    show_stats()
    print()

    if args.used:
        list_used()
    elif args.available is not None:
        list_available(args.available)
    elif args.query:
        if args.query.startswith("r") and len(args.query) <= 8 and args.query[1:].isdigit():
            check_by_id(args.query)
        else:
            fuzzy_search(args.query)
    return 0


if __name__ == "__main__":
    sys.exit(main())
