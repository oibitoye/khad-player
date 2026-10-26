"""Now Playing tab (extracted from legacy do_activate / play_url / control)."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from khad_media_player.player.playback_service import PlaybackService


class NowPlayingTab:
    def __init__(self, playback: PlaybackService) -> None:
        self.playback = playback
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.widget.set_border_width(20)

        self.url = Gtk.Entry()
        self.url.set_placeholder_text("Paste media URL")
        self.widget.pack_start(self.url, False, False, 0)

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        actions = [
            ("Play URL", self.play_url),
            ("Previous", lambda b: self.control(("playlist-prev", "weak"))),
            ("Pause / Resume", lambda b: self.control(("cycle", "pause"))),
            ("Next", lambda b: self.control(("playlist-next", "weak"))),
        ]
        for name, callback in actions:
            btn = Gtk.Button(label=name)
            btn.connect("clicked", callback)
            buttons.pack_start(btn, True, True, 0)
        self.widget.pack_start(buttons, False, False, 0)

        seek_buttons = Gtk.Box(spacing=8)
        for label, seconds in [
            ("Back 30s", -30),
            ("Back 10s", -10),
            ("Forward 10s", 10),
            ("Forward 30s", 30),
        ]:
            button = Gtk.Button(label=label)
            button.connect(
                "clicked",
                lambda _b, n=seconds: self.control(("seek", n, "relative")),
            )
            seek_buttons.pack_start(button, True, True, 0)
        self.widget.pack_start(seek_buttons, False, False, 0)

        self.status = Gtk.Label(label="Player starting...")
        self.widget.pack_start(self.status, False, False, 0)

    def set_url(self, url: str) -> None:
        self.url.set_text(url)

    def play_url(self, _button=None) -> None:
        url = self.url.get_text().strip()
        if not url:
            self.status.set_text("Enter a media URL first")
            return
        result = self.playback.play_url(url)
        if result.get("error") == "success":
            self.status.set_text("Loading media...")
        else:
            self.status.set_text("Player not ready")

    def control(self, action: tuple) -> None:
        result = self.playback.control(*action)
        if result.get("error") != "success":
            self.status.set_text("Player not ready")

    def set_status(self, text: str) -> None:
        self.status.set_text(text)
