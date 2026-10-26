"""Recently opened media persistence (extracted from legacy history logic)."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from khad_media_player.config import HISTORY_LIMIT
from khad_media_player.models.media import HistoryEntry
from khad_media_player.paths import (
    history_path,
    legacy_history_path,
    legacy_titles_path,
    titles_cache_path,
)
from khad_media_player.services.title_cache import TitleCache


class HistoryService:
    def __init__(
        self,
        path: Path | None = None,
        title_cache: TitleCache | None = None,
        migrate_legacy: bool | None = None,
    ) -> None:
        self.path = path or history_path()
        self.title_cache = title_cache or TitleCache()
        # Only auto-migrate when using the real default data location.
        should_migrate = (
            migrate_legacy
            if migrate_legacy is not None
            else path is None
        )
        if should_migrate:
            self._maybe_migrate_legacy()

    def _maybe_migrate_legacy(self) -> None:
        """One-time copy of Yoga data into Khad dirs without altering Yoga files."""
        if self.path.exists():
            return
        legacy = legacy_history_path()
        if legacy.is_file():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(legacy, self.path)
        titles = titles_cache_path()
        legacy_titles = legacy_titles_path()
        if not titles.exists() and legacy_titles.is_file():
            titles.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(legacy_titles, titles)

    def load(self) -> list[HistoryEntry]:
        try:
            records = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []
        if not isinstance(records, list):
            return []
        entries: list[HistoryEntry] = []
        for item in records:
            entry = HistoryEntry.from_dict(item)
            if entry is not None:
                entries.append(entry)
        return entries

    def save(self, entries: list[HistoryEntry]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {"url": e.url, "opened": e.opened, **({"title": e.title} if e.title else {})}
            for e in entries[:HISTORY_LIMIT]
        ]
        temporary = self.path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)

    def add(self, url: str) -> None:
        history = [e for e in self.load() if e.url != url]
        history.insert(
            0,
            HistoryEntry(
                url=url,
                opened=datetime.now(timezone.utc).isoformat(),
            ),
        )
        self.save(history)

    def delete(self, url: str) -> None:
        self.save([e for e in self.load() if e.url != url])

    def display_rows(self) -> list[tuple[str, str, str]]:
        titles = self.title_cache.load()
        rows: list[tuple[str, str, str]] = []
        for item in self.load():
            title = titles.get(item.url) or item.title or item.url
            opened = item.opened[:16].replace("T", " ")
            rows.append((opened, title, item.url))
        return rows
