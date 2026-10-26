"""Queue operations against the mpv playlist (extracted from legacy queue methods)."""

from __future__ import annotations

from typing import Any

from khad_media_player.player.playback_service import PlaybackService
from khad_media_player.services.title_cache import TitleCache


class QueueService:
    def __init__(
        self,
        playback: PlaybackService,
        title_cache: TitleCache | None = None,
    ) -> None:
        self.playback = playback
        self.title_cache = title_cache or TitleCache()

    def entries(self) -> list[dict[str, Any]]:
        return self.playback.get_playlist()

    def display_rows(self) -> list[tuple[str, int, str]]:
        titles = self.title_cache.load()
        rows: list[tuple[str, int, str]] = []
        for index, item in enumerate(self.entries()):
            url = item.get("filename") or ""
            title = titles.get(url) or item.get("title") or url or "Unknown"
            marker = "▶" if item.get("current") else ""
            rows.append((marker, index + 1, title))
        return rows

    def play_index(self, index: int) -> dict[str, Any]:
        result = self.playback.command("set_property", "playlist-pos", index)
        if result.get("error") == "success":
            self.playback.command("set_property", "pause", False)
        return result

    def play_from_start(self) -> dict[str, Any]:
        count = self.playback.command("get_property", "playlist-count")
        if count.get("error") != "success" or not count.get("data"):
            return {"error": "empty"}
        return self.play_index(0)

    def remove_index(self, index: int) -> dict[str, Any]:
        return self.playback.command("playlist-remove", index)

    def clear(self) -> dict[str, Any]:
        return self.playback.command("playlist-clear")
