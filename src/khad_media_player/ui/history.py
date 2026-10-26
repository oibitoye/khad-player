"""History tab (extracted from legacy history_* methods)."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk

from khad_media_player.player.playback_service import PlaybackService
from khad_media_player.services.history_service import HistoryService


class HistoryTab:
    def __init__(
        self,
        history: HistoryService,
        playback: PlaybackService,
        on_navigate_playing=None,
        on_queue_changed=None,
        status_target=None,
    ) -> None:
        self.history = history
        self.playback = playback
        self.on_navigate_playing = on_navigate_playing
        self.on_queue_changed = on_queue_changed
        self.status_target = status_target

        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.widget.set_border_width(12)

        self.history_store = Gtk.ListStore(str, str, str)
        self.history_view = Gtk.TreeView(model=self.history_store)
        self.history_view.set_headers_visible(True)
        for index, heading in enumerate(["Opened", "Title"]):
            renderer = Gtk.CellRendererText()
            renderer.set_property("ellipsize", 3)
            column = Gtk.TreeViewColumn(heading, renderer, text=index)
            column.set_resizable(True)
            self.history_view.append_column(column)
        self.history_view.connect(
            "row-activated", lambda *_args: self.replay_history(None)
        )

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.history_view)
        self.widget.pack_start(scroll, True, True, 0)

        history_buttons = Gtk.Box(spacing=8)
        for label, callback in [
            ("Replay", self.replay_history),
            ("Add to Queue", self.queue_history),
            ("Copy URL", self.copy_history),
            ("Delete", self.delete_history),
            ("Refresh", self.refresh_history),
        ]:
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            history_buttons.pack_start(button, True, True, 0)
        self.widget.pack_start(history_buttons, False, False, 0)

    def _set_status(self, text: str) -> None:
        if self.status_target is not None:
            self.status_target.set_text(text)

    def refresh_history(self, _button=None) -> None:
        self.history_store.clear()
        for opened, title, url in self.history.display_rows():
            self.history_store.append([opened, title, url])

    def selected_history_url(self) -> str | None:
        model, selected = self.history_view.get_selection().get_selected()
        return model[selected][2] if selected is not None else None

    def replay_history(self, _button=None) -> None:
        url = self.selected_history_url()
        if not url:
            self._set_status("Select a history entry first")
            return
        if self.on_navigate_playing:
            self.on_navigate_playing(url)
        result = self.playback.play_url(url)
        if result.get("error") == "success":
            self.refresh_history()
        else:
            self._set_status("Player not ready")

    def queue_history(self, _button=None) -> None:
        url = self.selected_history_url()
        if not url:
            return
        result = self.playback.queue_url(url)
        if result.get("error") == "success":
            if self.on_queue_changed:
                self.on_queue_changed()
            self._set_status("Added history item to queue")
        else:
            self._set_status("Queue failed: " + result.get("error", "unknown"))

    def copy_history(self, _button=None) -> None:
        url = self.selected_history_url()
        if url:
            Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(url, -1)

    def delete_history(self, _button=None) -> None:
        url = self.selected_history_url()
        if not url:
            return
        try:
            self.history.delete(url)
            self.refresh_history()
        except OSError as error:
            self._set_status(str(error))
