"""Main application window assembling the five tabs."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk

from khad_media_player.config import APP_NAME
from khad_media_player.player.playback_service import PlaybackService
from khad_media_player.services.history_service import HistoryService
from khad_media_player.services.queue_service import QueueService
from khad_media_player.services.title_cache import TitleCache
from khad_media_player.services.youtube_search import YouTubeSearchService
from khad_media_player.ui.history import HistoryTab
from khad_media_player.ui.now_playing import NowPlayingTab
from khad_media_player.ui.open_media import OpenMediaTab
from khad_media_player.ui.queue import QueueTab
from khad_media_player.ui.search import SearchTab


class MainWindow:
    def __init__(
        self,
        application: Gtk.Application,
        playback: PlaybackService,
        history: HistoryService,
        title_cache: TitleCache,
        search_service: YouTubeSearchService,
        queue_service: QueueService,
    ) -> None:
        self.application = application
        self.playback = playback
        self._gtk_fullscreen = False

        self.window = Gtk.ApplicationWindow(application=application)
        self.window.set_title(APP_NAME)
        size = (960, 720) if playback.is_embedded() else (800, 600)
        self.window.set_default_size(*size)
        self.window.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.window.connect("key-press-event", self._on_key_press)

        header = Gtk.HeaderBar()
        header.set_title(APP_NAME)
        header.set_subtitle(
            "Embedded" if playback.is_embedded() else "External mpv"
        )
        hide = Gtk.Button(label="Hide")
        hide.connect("clicked", lambda _b: self.window.hide())
        header.pack_end(hide)
        close = Gtk.Button(label="Close")
        close.connect("clicked", lambda _b: application.quit())
        header.pack_end(close)
        self.window.set_titlebar(header)

        self.notebook = Gtk.Notebook()

        self.now_playing = NowPlayingTab(
            playback,
            on_toggle_fullscreen=self.toggle_fullscreen,
        )
        self.notebook.append_page(self.now_playing.widget, Gtk.Label(label="Now Playing"))

        self.search = SearchTab(
            playback,
            search_service,
            on_navigate_playing=self._go_playing,
        )
        self.notebook.append_page(self.search.widget, Gtk.Label(label="Search"))

        self.queue = QueueTab(queue_service, parent_window=self.window)
        self.notebook.append_page(self.queue.widget, Gtk.Label(label="Queue"))

        self.open_media = OpenMediaTab(
            playback,
            parent_window=self.window,
            on_navigate_playing=self._go_playing,
            on_queue_changed=self.queue.refresh_queue,
        )
        self.notebook.append_page(self.open_media.widget, Gtk.Label(label="Open"))

        self.history = HistoryTab(
            history,
            playback,
            on_navigate_playing=self._go_playing,
            on_queue_changed=self.queue.refresh_queue,
            status_target=self.now_playing.status,
        )
        self.notebook.append_page(self.history.widget, Gtk.Label(label="History"))

        self.window.add(self.notebook)

        self.queue.refresh_queue()
        self.history.refresh_history()
        GLib.timeout_add_seconds(3, self.queue.refresh_queue)
        GLib.timeout_add(500, self.check_player)
        GLib.timeout_add_seconds(2, self.update_playback_status)

    def _go_playing(self, url: str) -> None:
        self.now_playing.set_url(url)
        self.notebook.set_current_page(0)

    def toggle_fullscreen(self, _button=None) -> None:
        """Fullscreen the GTK window (embedded) or the external mpv window."""
        if self.playback.is_embedded():
            if self._gtk_fullscreen:
                self.window.unfullscreen()
                self._gtk_fullscreen = False
                self.now_playing.set_status("Windowed")
            else:
                self.window.fullscreen()
                self._gtk_fullscreen = True
                self.now_playing.set_status("Fullscreen")
            return

        result = self.playback.toggle_mpv_fullscreen()
        if result.get("error") == "success":
            self.now_playing.set_status("Toggled mpv fullscreen")
        else:
            self.now_playing.set_status("Player not ready")

    def _on_key_press(self, _widget, event) -> bool:
        keyval = event.keyval
        if keyval == Gdk.KEY_F11:
            self.toggle_fullscreen()
            return True
        if keyval == Gdk.KEY_Escape and self._gtk_fullscreen:
            self.toggle_fullscreen()
            return True
        return False

    def present(self) -> None:
        self.window.show_all()
        self.window.present()

    def check_player(self) -> bool:
        if self.playback.is_ready():
            if self.now_playing.status.get_text() == "Player starting...":
                note = self.playback.mode_note
                self.now_playing.set_status(
                    f"Player ready ({'embedded' if self.playback.is_embedded() else 'external'})"
                )
                if note:
                    self.now_playing.mode_label.set_text(note)
            return False
        if self.playback.failed_to_start():
            self.now_playing.set_status("mpv failed to start")
            return False
        process = self.playback.process
        if (
            process is not None
            and process.process is not None
            and process.process.poll() is not None
        ):
            self.now_playing.set_status("mpv failed to start")
            return False
        return True

    def update_playback_status(self) -> bool:
        state = self.playback.playback_state_label()
        if state is None:
            return True
        self.now_playing.set_status(state)
        self.search.set_status(state)
        return True

    def cancel_background(self) -> None:
        self.search.cancel_pending()
