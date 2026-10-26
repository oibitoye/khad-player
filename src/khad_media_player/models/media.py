"""Media item models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MediaItem:
    url: str
    title: str = ""
    duration: float | None = None
    video_id: str = ""

    @property
    def youtube_url(self) -> str:
        if self.video_id:
            return f"https://www.youtube.com/watch?v={self.video_id}"
        return self.url

    def display_title(self) -> str:
        if not self.title:
            return self.url or "Untitled"
        if isinstance(self.duration, (int, float)):
            minutes = int(self.duration) // 60
            seconds = int(self.duration) % 60
            return f"{self.title} ({minutes}:{seconds:02d})"
        return self.title


@dataclass(frozen=True)
class HistoryEntry:
    url: str
    opened: str
    title: str = ""

    @classmethod
    def from_dict(cls, item: dict[str, Any]) -> HistoryEntry | None:
        if not isinstance(item, dict) or not item.get("url"):
            return None
        return cls(
            url=str(item["url"]),
            opened=str(item.get("opened", "")),
            title=str(item.get("title", "")),
        )
