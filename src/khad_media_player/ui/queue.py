"""Queue tab (extracted from legacy queue_* methods)."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from khad_media_player.services.queue_service import QueueService


class QueueTab:
    def __init__(self, queue_service: QueueService, parent_window=None) -> None:
        self.queue_service = queue_service
        self.parent_window = parent_window

        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.widget.set_border_width(12)

        self.queue_status = Gtk.Label(label="Queue loading...")
        self.widget.pack_start(self.queue_status, False, False, 0)

        self.queue_store = Gtk.ListStore(str, int, str)
        self.queue_view = Gtk.TreeView(model=self.queue_store)
        for index, heading in enumerate(["", "#", "Track"]):
            renderer = Gtk.CellRendererText()
            if index == 2:
                renderer.set_property("ellipsize", 3)
            column = Gtk.TreeViewColumn(heading, renderer, text=index)
            self.queue_view.append_column(column)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.queue_view)
        self.widget.pack_start(scroll, True, True, 0)

        queue_actions = Gtk.Box(spacing=8)
        for label, callback in [
            ("Play Selected", self.play_selected_queue),
            ("Play Queue", self.play_queue),
            ("Remove", self.remove_selected_queue),
            ("Clear Queue", self.clear_queue),
        ]:
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            queue_actions.pack_start(button, True, True, 0)
        self.widget.pack_start(queue_actions, False, False, 0)

        refresh_button = Gtk.Button(label="Refresh Queue")
        refresh_button.connect("clicked", self.refresh_queue)
        self.widget.pack_start(refresh_button, False, False, 0)

    def play_selected_queue(self, _button=None) -> None:
        model, selected = self.queue_view.get_selection().get_selected()
        if selected is None:
            self.queue_status.set_text("Select a track first")
            return
        index = model[selected][1] - 1
        result = self.queue_service.play_index(index)
        if result.get("error") == "success":
            self.queue_status.set_text("Starting selected track...")
        else:
            self.queue_status.set_text(
                "Could not select track: " + result.get("error", "unknown")
            )

    def play_queue(self, _button=None) -> None:
        result = self.queue_service.play_from_start()
        if result.get("error") == "empty":
            self.queue_status.set_text("Queue is empty")
        elif result.get("error") == "success":
            self.queue_status.set_text("Starting queue...")
        else:
            self.queue_status.set_text(
                "Could not start queue: " + result.get("error", "unknown")
            )

    def remove_selected_queue(self, _button=None) -> None:
        model, selected = self.queue_view.get_selection().get_selected()
        if selected is None:
            self.queue_status.set_text("Select a track first")
            return
        index = model[selected][1] - 1
        result = self.queue_service.remove_index(index)
        if result.get("error") == "success":
            self.refresh_queue()
        else:
            self.queue_status.set_text(
                "Remove failed: " + result.get("error", "unknown")
            )

    def clear_queue(self, _button=None) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Clear the entire queue?",
        )
        response = dialog.run()
        dialog.destroy()
        if response != Gtk.ResponseType.YES:
            return
        result = self.queue_service.clear()
        if result.get("error") == "success":
            self.refresh_queue()
        else:
            self.queue_status.set_text(
                "Clear failed: " + result.get("error", "unknown")
            )

    def refresh_queue(self, _button=None) -> bool:
        selection = self.queue_view.get_selection()
        model, selected = selection.get_selected()
        selected_index = model[selected][1] - 1 if selected is not None else None

        rows = self.queue_service.display_rows()
        self.queue_store.clear()
        for row in rows:
            self.queue_store.append(list(row))

        if selected_index is not None and selected_index < len(rows):
            selection.select_path(Gtk.TreePath.new_from_indices([selected_index]))

        self.queue_status.set_text(f"{len(rows)} queued")
        return True
