"""Facebook Reels publisher via Graph API.

Wired up but disabled by default. Enable by setting:
  FACEBOOK_ENABLED=true
  FACEBOOK_PAGE_ID=...
  FACEBOOK_PAGE_ACCESS_TOKEN=...

Uses the Reels resumable upload flow:
  1. POST /{page-id}/video_reels?upload_phase=start  → video_id, upload_url
  2. POST upload_url with Authorization + file_url or binary  → upload
  3. POST /{page-id}/video_reels?upload_phase=finish&video_id=...&video_state=PUBLISHED
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import requests

from src import config

log = logging.getLogger(__name__)

GRAPH = "https://graph.facebook.com/v20.0"
RUPLOAD = "https://rupload.facebook.com/video-upload/v20.0"


class FacebookPublisher:
    name = "facebook"

    def publish(self, video_path: Path, metadata: dict[str, Any]) -> str:
        if not config.FACEBOOK_ENABLED:
            raise RuntimeError("Facebook publishing is disabled (FACEBOOK_ENABLED=false)")
        if not (config.FACEBOOK_PAGE_ID and config.FACEBOOK_PAGE_ACCESS_TOKEN):
            raise RuntimeError("FACEBOOK_PAGE_ID / FACEBOOK_PAGE_ACCESS_TOKEN not set")

        token = config.FACEBOOK_PAGE_ACCESS_TOKEN
        page_id = config.FACEBOOK_PAGE_ID

        # Phase 1: start
        start = requests.post(
            f"{GRAPH}/{page_id}/video_reels",
            params={"upload_phase": "start", "access_token": token},
            timeout=30,
        )
        start.raise_for_status()
        sd = start.json()
        video_id = sd["video_id"]
        log.info("FB Reels: started upload, video_id=%s", video_id)

        # Phase 2: upload binary to rupload endpoint
        size = video_path.stat().st_size
        with video_path.open("rb") as f:
            up = requests.post(
                f"{RUPLOAD}/{video_id}",
                headers={
                    "Authorization": f"OAuth {token}",
                    "offset": "0",
                    "file_size": str(size),
                },
                data=f,
                timeout=300,
            )
        up.raise_for_status()
        log.info("FB Reels: binary uploaded (%d bytes)", size)

        # Phase 3: finish + publish
        caption = metadata.get("facebook_caption", metadata["youtube_title"])
        hashtags = " ".join(metadata.get("facebook_hashtags", []))
        description = f"{caption}\n\n{hashtags}".strip()
        finish = requests.post(
            f"{GRAPH}/{page_id}/video_reels",
            params={
                "upload_phase": "finish",
                "video_id": video_id,
                "video_state": "PUBLISHED",
                "description": description,
                "access_token": token,
            },
            timeout=60,
        )
        finish.raise_for_status()
        url = f"https://www.facebook.com/reel/{video_id}"
        log.info("FB Reels: published %s", url)
        return url

    def set_thumbnail(self, video_id: str, thumbnail_path: Path) -> None:
        """Upload a custom thumbnail image to the Facebook video."""
        if not (config.FACEBOOK_PAGE_ID and config.FACEBOOK_PAGE_ACCESS_TOKEN):
            return
        token = config.FACEBOOK_PAGE_ACCESS_TOKEN
        with thumbnail_path.open("rb") as f:
            resp = requests.post(
                f"{GRAPH}/{video_id}/thumbnails",
                params={"access_token": token, "is_preferred": "true"},
                files={"source": (thumbnail_path.name, f, "image/jpeg")},
                timeout=60,
            )
        try:
            resp.raise_for_status()
            log.info("FB Reels: thumbnail set for video %s", video_id)
        except requests.RequestException as exc:
            log.warning("FB Reels: thumbnail upload failed: %s", exc)

    def post_comment(self, video_id: str, comment_text: str) -> None:
        if not (config.FACEBOOK_PAGE_ID and config.FACEBOOK_PAGE_ACCESS_TOKEN):
            return
        token = config.FACEBOOK_PAGE_ACCESS_TOKEN
        body = f"🔒 ANSWER (spoiler below)\n\n{comment_text}"
        resp = requests.post(
            f"{GRAPH}/{video_id}/comments",
            params={"access_token": token, "message": body},
            timeout=30,
        )
        try:
            resp.raise_for_status()
            comment_id = resp.json().get("id", "unknown")
            log.info("FB Reels: answer comment posted (ID %s)", comment_id)
        except requests.RequestException as exc:
            log.warning("FB Reels: comment post failed: %s", exc)
