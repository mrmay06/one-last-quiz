"""One-time helper: get a YouTube OAuth refresh token.

Usage:
    1. Download `client_secret.json` from Google Cloud Console
       (OAuth 2.0 Client ID, Desktop app type).
    2. Place it next to this script.
    3. Run:  python scripts/get_refresh_token.py
    4. Browser opens → log in to the channel's Google account.
    5. Refresh token printed to terminal — copy it into GitHub Secrets
       as YOUTUBE_REFRESH_TOKEN.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",      # video upload
    "https://www.googleapis.com/auth/youtube.force-ssl",   # comments + thumbnails
]
SECRET_FILE = Path(__file__).parent / "client_secret.json"


def main() -> int:
    if not SECRET_FILE.exists():
        print(f"ERROR: {SECRET_FILE} not found.")
        print("Download OAuth 2.0 Client ID JSON from Google Cloud Console.")
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(str(SECRET_FILE), SCOPES)
    creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")

    print()
    print("=" * 60)
    print("COPY THESE INTO GITHUB SECRETS:")
    print("=" * 60)
    with SECRET_FILE.open() as f:
        secret = json.load(f)
    inner = secret.get("installed") or secret.get("web") or {}
    print(f"YOUTUBE_CLIENT_ID={inner.get('client_id', '')}")
    print(f"YOUTUBE_CLIENT_SECRET={inner.get('client_secret', '')}")
    print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
