"""Main pipeline. Run via: python -m src.orchestrator [--skip-upload]"""
from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path
from typing import Any

from src import (
    config,
    image_gen,
    music_picker,
    puzzle_store,
    script_gen,
    video_render,
    voice_gen,
)
from src.publishers import Publisher
from src.upload_facebook import FacebookPublisher
from src.upload_youtube import YouTubePublisher
from src.utils import ensure_tmp, log_error, retry

log = logging.getLogger(__name__)


def _build_props(template: str, script: dict[str, Any], images: list[Path], voice: Path, music: Path) -> dict[str, Any]:
    """Shape the props that Remotion expects per template."""
    base = {
        "voiceoverPath": str(voice.resolve()),
        "bgMusicPath": str(music.resolve()),
        "hook": script["hook"],
        "youtubeTitle": script["youtube_title"],
    }
    if template == "atmospheric":
        base.update(
            {
                "imageUrl": str(images[0].resolve()) if images else "",
                "puzzleText": script["puzzle_text"],
                "answer": script["answer"],
            }
        )
    elif template == "imessage":
        base.update(
            {
                "imageUrl": str(images[0].resolve()) if images else "",
                "contactName": script.get("contact_name", "Unknown"),
                "messages": script.get("messages", []),
                "answer": script["answer"],
            }
        )
    elif template == "iq":
        base.update(
            {
                "iqData": script["iq_data"],
                "answer": script["answer"],
            }
        )
    return base


def _publishers() -> list[Publisher]:
    pubs: list[Publisher] = [YouTubePublisher()]
    if config.FACEBOOK_ENABLED:
        pubs.append(FacebookPublisher())
    return pubs


@retry(attempts=config.DUPLICATE_RETRIES, base_delay=1.0, exceptions=(ValueError,))
def _generate_unique_script(template: str) -> dict[str, Any]:
    script = script_gen.generate(template)
    if puzzle_store.is_duplicate(script["puzzle_text"]):
        raise ValueError("duplicate puzzle generated; retrying")
    return script


def run(skip_upload: bool = False) -> None:
    config.setup_logging()
    ensure_tmp()

    # Step 1: pick template
    template = puzzle_store.next_template()
    log.info("=== Pipeline start: template=%s ===", template)

    # Step 2: generate script
    script = _generate_unique_script(template)

    # Step 3: images (atmospheric/imessage only)
    images: list[Path] = []
    if template in ("atmospheric", "imessage"):
        prompts = script.get("image_prompts") or []
        if prompts:
            images = image_gen.generate_images(prompts)

    # Step 4: voice
    voice = voice_gen.generate_voice(script["voiceover_script"])

    # Step 5: music
    music = music_picker.pick_track()

    # Step 6: render
    props = _build_props(template, script, images, voice, music)
    video = video_render.render(template, props)

    # Step 7: upload to enabled publishers
    video_id: str | None = None
    if not skip_upload:
        for pub in _publishers():
            try:
                url = pub.publish(video, {**script, "privacy": "public"})
                log.info("[%s] %s", pub.name, url)
                if pub.name == "youtube":
                    video_id = url.rsplit("/", 1)[-1]
            except Exception as exc:
                log_error(f"{pub.name} upload failed: {exc}")
                log.exception("[%s] upload failed", pub.name)
    else:
        log.info("--skip-upload set; skipping publishers")

    # Step 8: log puzzle
    puzzle_store.append(script["puzzle_text"], script["youtube_title"], video_id)
    puzzle_store.commit_template(template)

    # Step 9: cleanup
    if config.TMP_DIR.exists():
        for f in config.TMP_DIR.iterdir():
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                shutil.rmtree(f)

    log.info("=== Pipeline complete ===")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-upload", action="store_true")
    args = parser.parse_args()
    try:
        run(skip_upload=args.skip_upload)
    except Exception as exc:
        log_error(f"pipeline aborted: {exc}")
        logging.exception("pipeline aborted")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
