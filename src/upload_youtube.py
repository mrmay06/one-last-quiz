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

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubePublisher:
    name = "youtube"

    def _client(self):
        creds = Credentials(
            token=None,
            refresh_token=config.YOUTUBE_REFRESH_TOKEN,
            client_id=config.YOUTUBE_CLIENT_ID,
            client_secret=config.YOUTUBE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=SCOPES,
        )
        creds.refresh(Request())
        return build("youtube", "v3", credentials=creds, cache_discovery=False)

    def publish(self, video_path: Path, metadata: dict[str, Any]) -> str:
        title = metadata["youtube_title"]
        # Ensure #shorts is in the title or description so YT classifies as Short
        if "#shorts" not in title.lower():
            title = f"{title} #shorts"
        description = (
            f"{metadata['youtube_description']}\n\n"
            "#shorts #riddle #iq #brainteaser"
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
