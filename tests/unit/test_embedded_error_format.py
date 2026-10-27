"""Embedded backend should surface short mpv errors to the UI."""

from __future__ import annotations

from khad_media_player.player.embedded_backend import _format_mpv_error


def test_format_mpv_error_uses_first_string_arg() -> None:
    err = Exception("Invalid value for mpv parameter", -4, object())
    assert _format_mpv_error(err) == "Invalid value for mpv parameter"


def test_format_mpv_error_falls_back_to_str() -> None:
    assert _format_mpv_error(RuntimeError("boom")) == "boom"
