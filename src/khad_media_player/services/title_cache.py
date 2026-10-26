"""Persistent URL → title cache (extracted from legacy titles.json logic)."""

from __future__ import annotations

import json
from pathlib import Path

from khad_media_player.paths import titles_cache_path


class TitleCache:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or titles_cache_path()

    def load(self) -> dict[str, str]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {}
            return {str(k): str(v) for k, v in data.items()}
        except (OSError, ValueError):
            return {}

    def save(self, cache: dict[str, str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.path)

    def get(self, url: str) -> str | None:
        return self.load().get(url)

    def update_many(self, entries: list[tuple[str, str, float | None]]) -> None:
        """Update cache from search tuples: (video_id, title, duration)."""
        cache = self.load()
        for video_id, title, _duration in entries:
            if video_id and title:
                url = "https://www.youtube.com/watch?v=" + video_id
                cache[url] = title
        self.save(cache)

    def resolve(self, url: str, fallback: str | None = None) -> str:
        return self.get(url) or fallback or url
