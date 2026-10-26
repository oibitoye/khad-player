"""Now Playing tab (extracted from legacy do_activate / play_url / control)."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from khad_media_player.player.playback_service import PlaybackService


class NowPlayingTab:
    def __init__(self, playback: PlaybackService) -> None:
        self.playback = playback
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.widget.set_border_width(12)

        video = playback.video_widget()
        if video is not None:
            frame = Gtk.Frame(label="Video")
            frame.add(video)
            self.widget.pack_start(frame, True, True, 0)
            mode_hint = "Embedded playback (libmpv)"
        else:
            mode_hint = "External mpv window"
            placeholder = Gtk.Label(
                label="Video plays in the separate mpv window.\n"
                "Set KHAD_RENDER_MODE=embedded when libmpv is available."
            )
            placeholder.set_line_wrap(True)
            placeholder.set_justify(Gtk.Justification.CENTER)
            self.widget.pack_start(placeholder, True, True, 0)

        controls = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        controls.set_border_width(8)

        self.url = Gtk.Entry()
        self.url.set_placeholder_text("Paste media URL")
        controls.pack_start(self.url, False, False, 0)

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
        controls.pack_start(buttons, False, False, 0)

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
        controls.pack_start(seek_buttons, False, False, 0)

        self.status = Gtk.Label(label="Player starting...")
        controls.pack_start(self.status, False, False, 0)

        self.mode_label = Gtk.Label(label=mode_hint)
        self.mode_label.set_opacity(0.7)
        controls.pack_start(self.mode_label, False, False, 0)

        self.widget.pack_start(controls, False, False, 0)

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
            detail = result.get("error", "unknown")
            self.status.set_text(
                "Player not ready" if detail == "Player not ready" else f"Playback failed: {detail}"
            )

    def control(self, action: tuple) -> None:
        result = self.playback.control(*action)
        if result.get("error") != "success":
            self.status.set_text("Player not ready")

    def set_status(self, text: str) -> None:
        self.status.set_text(text)
