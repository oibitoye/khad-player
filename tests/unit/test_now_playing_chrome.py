"""Now Playing chrome visibility for video-only fullscreen."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

pytest.importorskip("gi")

from khad_media_player.ui.now_playing import NowPlayingTab


def test_set_chrome_visible_toggles_rails() -> None:
    playback = MagicMock()
    playback.video_widget.return_value = None
    tab = NowPlayingTab(playback)
    assert tab._chrome_visible is True

    tab.set_chrome_visible(False)
    assert tab._chrome_visible is False
    assert tab.widget.get_border_width() == 0

    tab.set_chrome_visible(True)
    assert tab._chrome_visible is True
    assert tab.widget.get_border_width() == 10
