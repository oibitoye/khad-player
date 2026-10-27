"""Queue tab must tolerate a missing Gtk selection during refresh."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

pytest.importorskip("gi")

from khad_media_player.ui.queue import QueueTab


def test_refresh_queue_when_selection_is_none() -> None:
    service = SimpleNamespace(display_rows=lambda: [(" ", 1, "Track A")])
    tab = QueueTab.__new__(QueueTab)
    tab.queue_service = service
    tab.queue_status = MagicMock()
    tab.queue_store = MagicMock()
    tab.queue_view = MagicMock()
    tab.queue_view.get_selection.return_value = None

    assert tab.refresh_queue() is True
    tab.queue_store.clear.assert_called_once()
    tab.queue_store.append.assert_called_once_with([" ", 1, "Track A"])
    tab.queue_status.set_text.assert_called_once_with("1 queued")
