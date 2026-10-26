"""Gtk.Application entry — extracted from legacy MediaPlayer lifecycle."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk

from khad_media_player.config import APP_ID
from khad_media_player.player.playback_service import PlaybackService
from khad_media_player.services.history_service import HistoryService
from khad_media_player.services.queue_service import QueueService
from khad_media_player.services.title_cache import TitleCache
from khad_media_player.services.youtube_search import YouTubeSearchService
from khad_media_player.ui.main_window import MainWindow


class KhadMediaPlayerApp(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self._main: MainWindow | None = None
        self.title_cache = TitleCache()
        self.history = HistoryService(title_cache=self.title_cache)
        self.playback = PlaybackService(on_history=self.history.add)
        self.search_service = YouTubeSearchService(title_cache=self.title_cache)
        self.queue_service = QueueService(self.playback, title_cache=self.title_cache)

    def do_activate(self) -> None:  # noqa: N802 — GObject override
        if self._main is not None:
            self._main.present()
            return
        self.playback.start()
        self._main = MainWindow(
            application=self,
            playback=self.playback,
            history=self.history,
            title_cache=self.title_cache,
            search_service=self.search_service,
            queue_service=self.queue_service,
        )
        self._main.present()

    def do_shutdown(self) -> None:  # noqa: N802 — GObject override
        if self._main is not None:
            self._main.cancel_background()
        self.playback.shutdown()
        Gtk.Application.do_shutdown(self)


def run(argv: list[str] | None = None) -> int:
    app = KhadMediaPlayerApp()
    return app.run(argv)
