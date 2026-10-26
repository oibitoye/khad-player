"""Open tab with conditional M3U browser (extracted from legacy open/m3u methods)."""

from __future__ import annotations

from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from khad_media_player.config import M3U_DISPLAY_LIMIT
from khad_media_player.models.playlist import PlaylistEntry
from khad_media_player.player.playback_service import PlaybackService
from khad_media_player.services.playlist_parser import filter_entries, parse_m3u_file


class OpenMediaTab:
    def __init__(
        self,
        playback: PlaybackService,
        parent_window=None,
        on_navigate_playing=None,
        on_queue_changed=None,
    ) -> None:
        self.playback = playback
        self.parent_window = parent_window
        self.on_navigate_playing = on_navigate_playing
        self.on_queue_changed = on_queue_changed
        self.m3u_entries: list[PlaylistEntry] = []

        open_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        open_box.set_border_width(12)

        self.open_entry = Gtk.Entry()
        self.open_entry.set_placeholder_text("Media URL, stream URL or local file")
        open_box.pack_start(self.open_entry, False, False, 0)

        browse_button = Gtk.Button(label="Browse Files")
        browse_button.connect("clicked", self.browse_media)
        open_box.pack_start(browse_button, False, False, 0)

        open_actions = Gtk.Box(spacing=8)
        self.open_play_button = Gtk.Button(label="Play Now")
        self.open_play_button.connect("clicked", self.play_open_media)
        open_actions.pack_start(self.open_play_button, True, True, 0)
        self.open_queue_button = Gtk.Button(label="Add to Queue")
        self.open_queue_button.connect("clicked", self.queue_open_media)
        open_actions.pack_start(self.open_queue_button, True, True, 0)
        open_box.pack_start(open_actions, False, False, 0)

        self.open_status = Gtk.Label(
            label="Supports media files, URLs, M3U and M3U8 channel lists"
        )
        self.open_status.set_line_wrap(True)
        open_box.pack_start(self.open_status, False, False, 0)

        self.m3u_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.m3u_panel.set_border_width(6)
        self.m3u_panel.set_no_show_all(True)

        self.m3u_search = Gtk.SearchEntry()
        self.m3u_search.set_placeholder_text("Search channels")
        self.m3u_search.connect("search-changed", self.filter_m3u_browser)
        self.m3u_panel.pack_start(self.m3u_search, False, False, 0)

        self.m3u_group = Gtk.ComboBoxText()
        self.m3u_group.append_text("All Channels")
        self.m3u_group.set_active(0)
        self.m3u_group.connect("changed", self.filter_m3u_browser)
        self.m3u_panel.pack_start(self.m3u_group, False, False, 0)

        self.m3u_count = Gtk.Label(label="Choose an M3U file to browse channels")
        self.m3u_panel.pack_start(self.m3u_count, False, False, 0)

        self.m3u_store = Gtk.ListStore(str, str, str)
        self.m3u_view = Gtk.TreeView(model=self.m3u_store)
        for index, heading in enumerate(["Channel", "Group"]):
            renderer = Gtk.CellRendererText()
            renderer.set_property("ellipsize", 3)
            column = Gtk.TreeViewColumn(heading, renderer, text=index)
            column.set_resizable(True)
            if index == 0:
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
                column.set_fixed_width(300)
                column.set_min_width(150)
            self.m3u_view.append_column(column)
        self.m3u_view.get_selection().connect("changed", self.select_m3u_channel)

        m3u_scroll = Gtk.ScrolledWindow()
        m3u_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        m3u_scroll.add(self.m3u_view)
        self.m3u_panel.pack_start(m3u_scroll, True, True, 0)

        self.widget = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=8, homogeneous=True
        )
        self.widget.pack_start(open_box, True, True, 0)
        self.widget.pack_start(self.m3u_panel, True, True, 0)

    def get_open_media(self) -> str | None:
        url = self.open_entry.get_text().strip()
        if not url:
            self.open_status.set_text("Select a file or enter a URL")
            return None
        if url.lower().split("?", 1)[0].endswith(".m3u"):
            self.open_status.set_text("Select a channel from the playlist first")
            return None
        return url

    def play_open_media(self, _button=None) -> None:
        url = self.get_open_media()
        if not url:
            return
        result = self.playback.play_url(url)
        if result.get("error") == "success":
            if self.on_navigate_playing:
                self.on_navigate_playing(url)
            self.open_status.set_text("Loading selected media...")
        else:
            self.open_status.set_text(
                "Playback failed: " + result.get("error", "unknown")
            )

    def queue_open_media(self, _button=None) -> None:
        url = self.get_open_media()
        if not url:
            return
        result = self.playback.queue_url(url)
        if result.get("error") == "success":
            self.open_status.set_text("Added to playback queue")
            if self.on_queue_changed:
                self.on_queue_changed()
        else:
            self.open_status.set_text(
                "Queue failed: " + result.get("error", "unknown")
            )

    def browse_media(self, _button=None) -> None:
        dialog = Gtk.FileChooserDialog(
            title="Select Media or Playlist",
            transient_for=self.parent_window,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL, "Open", Gtk.ResponseType.OK
        )
        dialog.set_default_size(700, 500)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            if filename:
                self.open_entry.set_text(filename)
                self.open_status.set_text("Selected: " + Path(filename).name)
                if filename.lower().endswith((".m3u", ".m3u8")):
                    self.load_m3u_browser(filename)
                else:
                    self.m3u_panel.hide()
                    self.m3u_panel.set_no_show_all(True)
                    self.m3u_entries = []
        dialog.destroy()

    def load_m3u_browser(self, filename: str) -> None:
        try:
            parsed = parse_m3u_file(filename)
        except OSError as error:
            self.open_status.set_text(str(error))
            return

        self.m3u_entries = list(parsed.entries)
        if self.m3u_entries:
            self.m3u_panel.set_no_show_all(False)
            self.m3u_panel.show_all()
        else:
            self.m3u_panel.hide()
            self.m3u_panel.set_no_show_all(True)

        self.m3u_group.remove_all()
        self.m3u_group.append_text("All Channels")
        for group in parsed.groups:
            self.m3u_group.append_text(group)
        self.m3u_group.set_active(0)
        self.filter_m3u_browser()
        self.open_status.set_text(
            f"Loaded {len(self.m3u_entries)} channels from {Path(filename).name}"
        )

    def filter_m3u_browser(self, *_args) -> None:
        query = self.m3u_search.get_text()
        group = self.m3u_group.get_active_text()
        matches, total = filter_entries(
            self.m3u_entries, query=query, group=group, limit=M3U_DISPLAY_LIMIT
        )
        self.m3u_store.clear()
        for entry in matches:
            self.m3u_store.append([entry.name, entry.group, entry.url])
        self.m3u_count.set_text(
            f"{total} matching channels"
            + (" (showing first 100)" if total > M3U_DISPLAY_LIMIT else "")
        )

    def select_m3u_channel(self, selection) -> None:
        model, iterator = selection.get_selected()
        if iterator is not None:
            name = model[iterator][0]
            url = model[iterator][2]
            self.open_entry.set_text(url)
            self.open_status.set_text("Selected: " + name)
