"""Render mode selection and fallback."""

from __future__ import annotations

from khad_media_player.player.backend import RenderMode
from khad_media_player.player.external_backend import ExternalBackend
from khad_media_player.player.render_selection import create_backend, requested_render_mode


def test_forced_external(monkeypatch) -> None:
    monkeypatch.setenv("KHAD_RENDER_MODE", "external")
    assert requested_render_mode() == "external"
    backend, mode, note = create_backend()
    assert isinstance(backend, ExternalBackend)
    assert mode == RenderMode.EXTERNAL
    assert "external" in note.lower()


def test_embedded_falls_back_when_unavailable(monkeypatch) -> None:
    monkeypatch.setenv("KHAD_RENDER_MODE", "embedded")
    monkeypatch.setattr(
        "khad_media_player.player.render_selection.embedded_prerequisites",
        lambda: (False, "python-mpv missing"),
    )
    backend, mode, note = create_backend()
    assert isinstance(backend, ExternalBackend)
    assert mode == RenderMode.EXTERNAL
    assert "python-mpv missing" in note


def test_auto_uses_external_when_prereqs_fail(monkeypatch) -> None:
    monkeypatch.setenv("KHAD_RENDER_MODE", "auto")
    monkeypatch.setattr(
        "khad_media_player.player.render_selection.embedded_prerequisites",
        lambda: (False, "no opengl"),
    )
    backend, mode, _note = create_backend()
    assert isinstance(backend, ExternalBackend)
    assert mode == RenderMode.EXTERNAL
