"""History and title cache persistence tests."""

from __future__ import annotations

import json
from pathlib import Path

from khad_media_player.services.history_service import HistoryService
from khad_media_player.services.title_cache import TitleCache


def test_history_add_dedupe_and_bound(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    cache = TitleCache(tmp_path / "titles.json")
    service = HistoryService(path=path, title_cache=cache)
    service.add("https://example.com/a")
    service.add("https://example.com/b")
    service.add("https://example.com/a")
    rows = service.display_rows()
    assert rows[0][2] == "https://example.com/a"
    assert len(rows) == 2


def test_history_atomic_write_and_corrupt_recovery(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    path.write_text("{not-json", encoding="utf-8")
    service = HistoryService(path=path, title_cache=TitleCache(tmp_path / "t.json"))
    assert service.load() == []
    service.add("https://example.com/x")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data[0]["url"] == "https://example.com/x"


def test_history_delete(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    service = HistoryService(path=path, title_cache=TitleCache(tmp_path / "t.json"))
    service.add("https://example.com/a")
    service.delete("https://example.com/a")
    assert service.load() == []


def test_title_cache_update(tmp_path: Path) -> None:
    cache = TitleCache(tmp_path / "titles.json")
    cache.update_many([("abc123", "Demo Video", 65.0)])
    assert cache.get("https://www.youtube.com/watch?v=abc123") == "Demo Video"
