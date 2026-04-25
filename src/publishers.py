"""Publisher interface — uniform across YouTube, Facebook, future platforms."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class Publisher(Protocol):
    """Every platform implements this."""

    name: str

    def publish(self, video_path: Path, metadata: dict[str, Any]) -> str:
        """Upload the video. Returns the platform's video URL or ID."""
        ...
