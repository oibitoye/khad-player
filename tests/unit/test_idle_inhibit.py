"""Idle inhibitor acquires and releases a Gtk inhibit cookie."""

from __future__ import annotations

from unittest.mock import MagicMock

from khad_media_player.services import idle_inhibit
from khad_media_player.services.idle_inhibit import IdleInhibitor


def test_inhibit_stores_cookie_when_application_accepts(monkeypatch) -> None:
    monkeypatch.setattr(idle_inhibit, "_inhibit_flags", lambda: 3)
    application = MagicMock()
    application.inhibit.return_value = 42
    inhibitor = IdleInhibitor(application, MagicMock())

    inhibitor.set_playing(True)
    assert inhibitor.active is True
    application.inhibit.assert_called_once()
    assert application.inhibit.call_args.args[2] == "Playing media"

    inhibitor.set_playing(True)  # idempotent
    assert application.inhibit.call_count == 1

    inhibitor.set_playing(False)
    assert inhibitor.active is False
    application.uninhibit.assert_called_once_with(42)


def test_inhibit_no_op_when_cookie_is_zero(monkeypatch) -> None:
    monkeypatch.setattr(idle_inhibit, "_inhibit_flags", lambda: 3)
    application = MagicMock()
    application.inhibit.return_value = 0
    inhibitor = IdleInhibitor(application, MagicMock())
    inhibitor.inhibit()
    assert inhibitor.active is False


def test_release_is_idempotent() -> None:
    application = MagicMock()
    inhibitor = IdleInhibitor(application, MagicMock())
    inhibitor._cookie = 7
    inhibitor.release()
    application.uninhibit.assert_called_once_with(7)
    inhibitor.release()
    assert application.uninhibit.call_count == 1
