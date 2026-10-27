"""Fullscreen toggle routes embedded vs external correctly."""

from __future__ import annotations

from khad_media_player.player.backend import RenderMode
from khad_media_player.player.playback_service import PlaybackService


def test_toggle_mpv_fullscreen_external_cycles() -> None:
    service = PlaybackService.__new__(PlaybackService)
    service.render_mode = RenderMode.EXTERNAL
    calls: list[tuple] = []

    def command(*args):
        calls.append(args)
        return {"error": "success"}

    service.command = command  # type: ignore[method-assign]
    result = service.toggle_mpv_fullscreen()
    assert result == {"error": "success"}
    assert calls == [("cycle", "fullscreen")]


def test_toggle_mpv_fullscreen_embedded_skips_ipc() -> None:
    service = PlaybackService.__new__(PlaybackService)
    service.render_mode = RenderMode.EMBEDDED

    def command(*_args):
        raise AssertionError("embedded must not use mpv fullscreen IPC")

    service.command = command  # type: ignore[method-assign]
    result = service.toggle_mpv_fullscreen()
    assert result == {"error": "embedded-uses-gtk-window"}
