"""Search tab (extracted from legacy search_* methods)."""

from __future__ import annotations

import threading

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from khad_media_player.models.media import MediaItem
from khad_media_player.player.playback_service import PlaybackService
from khad_media_player.services.youtube_search import YouTubeSearchService


class SearchTab:
    def __init__(
        self,
        playback: PlaybackService,
        search_service: YouTubeSearchService,
        on_navigate_playing=None,
    ) -> None:
        self.playback = playback
        self.search_service = search_service
        self.on_navigate_playing = on_navigate_playing

        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.widget.set_border_width(12)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search YouTube")
        self.search_entry.connect("activate", self.search_youtube)
        self.widget.pack_start(self.search_entry, False, False, 0)

        self.search_button = Gtk.Button(label="Search")
        self.search_button.connect("clicked", self.search_youtube)
        self.widget.pack_start(self.search_button, False, False, 0)

        self.search_status = Gtk.Label(label="Ready to search")
        self.widget.pack_start(self.search_status, False, False, 0)

        self.search_results = Gtk.ListStore(str, str)
        self.search_view = Gtk.TreeView(model=self.search_results)
        self.search_view.set_headers_visible(False)

        renderer = Gtk.CellRendererText()
        renderer.set_property("wrap-width", 500)
        renderer.set_property("wrap-mode", 2)
        column = Gtk.TreeViewColumn("Results", renderer, text=0)
        self.search_view.append_column(column)

        scroll = Gtk.ScrolledWindow()
        scroll.add(self.search_view)
        self.widget.pack_start(scroll, True, True, 0)

        search_actions = Gtk.Box(spacing=8)
        play_button = Gtk.Button(label="Play Now")
        play_button.connect("clicked", self.play_search_result)
        search_actions.pack_start(play_button, True, True, 0)
        queue_button = Gtk.Button(label="Add to Queue")
        queue_button.connect("clicked", self.queue_search_result)
        search_actions.pack_start(queue_button, True, True, 0)
        self.widget.pack_start(search_actions, False, False, 0)

    def search_youtube(self, _button=None) -> None:
        query = self.search_entry.get_text().strip()
        if not query:
            self.search_status.set_text("Enter a search term")
            return
        self.search_button.set_sensitive(False)
        self.search_status.set_text("Searching...")
        self.search_results.clear()
        self.search_service.reset()
        threading.Thread(
            target=self._search_worker,
            args=(query,),
            daemon=True,
        ).start()

    def _search_worker(self, query: str) -> None:
        try:
            entries, error = self.search_service.search(query)
        except Exception as error:  # noqa: BLE001 — surface to UI
            GLib.idle_add(self.show_search_results, [], str(error))
            return
        GLib.idle_add(self.show_search_results, entries, error)

    def show_search_results(self, entries: list[MediaItem], error: str) -> bool:
        for item in entries:
            if not item.video_id:
                continue
            self.search_results.append([item.display_title(), item.youtube_url])
        self.search_status.set_text(
            f"{len(self.search_results)} results" if entries else (error or "No results")
        )
        self.search_button.set_sensitive(True)
        return False

    def selected_search_url(self) -> str | None:
        model, selected = self.search_view.get_selection().get_selected()
        if selected is None:
            self.search_status.set_text("Select a video first")
            return None
        return model[selected][1]

    def play_search_result(self, _button=None) -> None:
        url = self.selected_search_url()
        if not url:
            return
        result = self.playback.play_url(url)
        if result.get("error") == "success":
            if self.on_navigate_playing:
                self.on_navigate_playing(url)
            self.search_status.set_text("Loading selected video...")
        else:
            self.search_status.set_text(
                "Playback failed: " + result.get("error", "unknown")
            )

    def queue_search_result(self, _button=None) -> None:
        url = self.selected_search_url()
        if not url:
            return
        result = self.playback.queue_url(url)
        if result.get("error") == "success":
            self.search_status.set_text("Added to playback queue")
        else:
            self.search_status.set_text(
                "Queue failed: " + result.get("error", "unknown")
            )

    def set_status(self, text: str) -> None:
        self.search_status.set_text(text)

    def cancel_pending(self) -> None:
        self.search_service.cancel()
