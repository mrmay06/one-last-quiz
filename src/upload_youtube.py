"""YouTube Data API v3 upload via OAuth refresh token."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from src import config

log = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


class YouTubePublisher:
    name = "youtube"

    def _client(self):
        # Don't pass scopes — the refresh token already encodes what was granted.
        # Passing scopes causes Google to re-validate scope on refresh, which breaks
        # if the token was generated with different/fewer scopes than listed here.
        creds = Credentials(
            token=None,
            refresh_token=config.YOUTUBE_REFRESH_TOKEN,
            client_id=config.YOUTUBE_CLIENT_ID,
            client_secret=config.YOUTUBE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )
        creds.refresh(Request())
        return build("youtube", "v3", credentials=creds, cache_discovery=False)

    def publish(self, video_path: Path, metadata: dict[str, Any]) -> str:
        title = metadata["youtube_title"]
        if "#shorts" not in title.lower():
            title = f"{title} #shorts"
        description = (
            f"{metadata['youtube_description']}\n\n"
            "#shorts #riddle #brainteaser #puzzle"
        )
        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": metadata.get("tags", []),
                "categoryId": "24",
            },
            "status": {
                "privacyStatus": metadata.get("privacy", "public"),
                "selfDeclaredMadeForKids": False,
            },
        }
        media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
        client = self._client()
        log.info("YouTube upload starting: %s", title)
        request = client.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                log.info("YouTube upload progress: %d%%", int(status.progress() * 100))
        video_id = response["id"]
        url = f"https://youtube.com/shorts/{video_id}"
        log.info("YouTube upload complete: %s", url)
        return url

    def set_thumbnail(self, video_id: str, thumbnail_path: Path) -> None:
        client = self._client()
        media = MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
        try:
            client.thumbnails().set(videoId=video_id, media_body=media).execute()
            log.info("Thumbnail set for video %s", video_id)
        except Exception as exc:
            log.warning("Thumbnail upload failed (channel may not be eligible yet): %s", exc)

    def post_pinned_comment(self, video_id: str, comment_text: str) -> None:
        client = self._client()
        body = (
            "🔒 ANSWER (spoiler — read at your own risk) ↓\n\n"
            "‎ \n‎ \n‎ \n"
            f"{comment_text}"
        )
        thread = client.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {"snippet": {"textOriginal": body}},
                }
            },
        ).execute()
        comment_id = thread["snippet"]["topLevelComment"]["id"]
        log.info("Pinned-comment posted (ID %s) — pin manually in Studio if needed", comment_id)
