"""Main pipeline. Run via: python -m src.orchestrator [--skip-upload]"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

from src import (
    captions as captions_mod,
    config,
    image_gen,
    music_picker,
    puzzle_store,
    script_gen,
    thumbnail as thumb_mod,
    video_render,
    voice_gen,
)
from src.publishers import Publisher
from src.upload_facebook import FacebookPublisher
from src.upload_youtube import YouTubePublisher
from src.utils import ensure_tmp, log_error

log = logging.getLogger(__name__)


def _rel(p: Path) -> str:
    """Path remotion serves at: /public/<rel>."""
    return "/public/" + p.relative_to(config.REMOTION_PUBLIC).as_posix()


def _compute_durations(voice_seconds: float) -> dict[str, int]:
    """Decide video length and key frame timings from voice length."""
    fps = config.FPS
    voice_frames = int(round(voice_seconds * fps))
    buffer_frames = int(round(config.RENDER_BUFFER_SECONDS * fps))
    total = voice_frames + buffer_frames
    total = max(int(config.MIN_VIDEO_SECONDS * fps), min(int(config.MAX_VIDEO_SECONDS * fps), total))
    return {
        "totalFrames": total,
        "hookDurationFrames": min(int(2.5 * fps), total // 4),
        "cliffhangerStartFrame": total - buffer_frames,
    }


def _build_image_cuts(prompts: list[dict[str, Any]], images: list[Path], total_frames: int) -> list[dict[str, Any]]:
    """Convert image prompts (with cut_at_second) into frame-cut timing."""
    cuts: list[dict[str, Any]] = []
    if not prompts or not images:
        return cuts
    for i, prompt in enumerate(prompts[: len(images)]):
        cut_sec = prompt.get("cut_at_second", 0) if isinstance(prompt, dict) else 0
        cut_frame = max(0, min(total_frames - 30, int(cut_sec * config.FPS)))
        cuts.append({"src": _rel(images[i]), "cutAtFrame": cut_frame})
    cuts.sort(key=lambda cut: cut["cutAtFrame"])
    if cuts and cuts[0]["cutAtFrame"] != 0:
        cuts[0]["cutAtFrame"] = 0
    return cuts


def _build_props(
    script: dict[str, Any],
    images: list[Path],
    voice: Path,
    music: Path,
    word_timings: list[dict[str, Any]],
    durations: dict[str, int],
) -> dict[str, Any]:
    return {
        "voiceoverPath": _rel(voice),
        "bgMusicPath": _rel(music),
        "hook": script["hook"],
        "cta": script["cta"],
        "captions": word_timings,
        "totalFrames": durations["totalFrames"],
        "hookDurationFrames": durations["hookDurationFrames"],
        "cliffhangerStartFrame": durations["cliffhangerStartFrame"],
        "imageCuts": _build_image_cuts(script.get("image_prompts", []), images, durations["totalFrames"]),
    }


def _publishers() -> list[Publisher]:
    pubs: list[Publisher] = []
    if config.YOUTUBE_REFRESH_TOKEN:
        pubs.append(YouTubePublisher())
    if config.FACEBOOK_ENABLED:
        pubs.append(FacebookPublisher())
    return pubs


def run(skip_upload: bool = False) -> None:
    config.setup_logging()
    ensure_tmp()

    template = puzzle_store.next_template()
    if template != "atmospheric":
        raise RuntimeError(f"Unsupported template in V2: {template}")
    log.info("=== Pipeline start: template=%s ===", template)

    script = script_gen.generate(template)

    images: list[Path] = []
    image_prompts = script.get("image_prompts") or []
    if image_prompts:
        prompts_only = [p["prompt"] if isinstance(p, dict) else p for p in image_prompts]
        images = image_gen.generate_images(prompts_only)

    voice, voice_duration = voice_gen.generate_voice(script["voiceover_script"])
    word_timings = captions_mod.align(voice)
    music = music_picker.pick_track()
    durations = _compute_durations(voice_duration)
    props = _build_props(script, images, voice, music, word_timings, durations)
    video = video_render.render(template, props)

    first_image = images[0] if images else None
    thumb = thumb_mod.generate(script["hook"], first_image)

    video_id: str | None = None
    if not skip_upload:
        for pub in _publishers():
            try:
                url = pub.publish(video, {**script, "privacy": "public"})
                log.info("[%s] %s", pub.name, url)
                pub_video_id = url.rsplit("/", 1)[-1]
                if pub.name == "youtube":
                    video_id = pub_video_id
                # Thumbnail: FB only (YT channel not eligible yet)
                if pub.name == "facebook" and hasattr(pub, "set_thumbnail"):
                    try:
                        pub.set_thumbnail(pub_video_id, thumb)
                    except Exception as exc:
                        log.warning("[%s] Thumbnail set failed: %s", pub.name, exc)
                # Answer comment on every platform
                if hasattr(pub, "post_comment"):
                    try:
                        pub.post_comment(pub_video_id, script.get("pinned_comment", script["answer"]))
                    except Exception as exc:
                        log.warning("[%s] Comment failed: %s", pub.name, exc)
            except Exception as exc:
                log_error(f"{pub.name} upload failed: {exc}")
                log.exception("[%s] upload failed", pub.name)
    else:
        log.info("--skip-upload set; skipping publishers")

    puzzle_store.append(
        script["puzzle_text"],
        script["youtube_title"],
        video_id=video_id,
        riddle_id=script.get("riddle_id"),
    )
    puzzle_store.commit_template(template)

    if config.REMOTION_RUN_DIR.exists():
        for f in config.REMOTION_RUN_DIR.iterdir():
            if f.is_file():
                f.unlink()
    if not skip_upload and config.TMP_DIR.exists():
        for f in config.TMP_DIR.iterdir():
            if f.is_file():
                f.unlink()

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
