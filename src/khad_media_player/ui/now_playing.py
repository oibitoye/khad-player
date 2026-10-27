"""Now Playing tab (extracted from legacy do_activate / play_url / control)."""

from __future__ import annotations

from collections.abc import Callable

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from khad_media_player.player.playback_service import PlaybackService

# Side rails stay usable on tablets; video column takes the remaining width.
_SIDE_WIDTH = 200


class NowPlayingTab:
    def __init__(
        self,
        playback: PlaybackService,
        on_toggle_fullscreen: Callable[[], None] | None = None,
    ) -> None:
        self.playback = playback
        self._on_toggle_fullscreen = on_toggle_fullscreen
        self._chrome_visible = True

        video = playback.video_widget()
        embedded = video is not None
        if embedded:
            mode_hint = "Embedded — Fullscreen fills video only (F11 / Esc)"
        else:
            mode_hint = "External mpv — Fullscreen / F11, or press f in mpv"

        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.widget.set_border_width(10)

        # Top strip: URL + Play (full width)
        self._top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.url = Gtk.Entry()
        self.url.set_placeholder_text("Paste media URL")
        self.url.set_hexpand(True)
        self._top.pack_start(self.url, True, True, 0)
        play_btn = Gtk.Button(label="Play URL")
        play_btn.connect("clicked", self.play_url)
        self._top.pack_start(play_btn, False, False, 0)
        self.widget.pack_start(self._top, False, False, 0)

        # Three columns: controls | video | controls
        columns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        columns.set_homogeneous(False)

        self._left = self._side_rail()
        self._left.pack_start(self._section_label("Transport"), False, False, 0)
        for label, action in [
            ("Previous", ("playlist-prev", "weak")),
            ("Pause / Resume", ("cycle", "pause")),
            ("Next", ("playlist-next", "weak")),
        ]:
            self._left.pack_start(self._action_button(label, action), False, False, 0)
        self._left.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 4
        )
        self._left.pack_start(self._section_label("Seek back"), False, False, 0)
        for label, seconds in [("Back 30s", -30), ("Back 10s", -10)]:
            self._left.pack_start(self._seek_button(label, seconds), False, False, 0)
        self._left.pack_end(Gtk.Label(), True, True, 0)
        columns.pack_start(self._left, False, False, 0)

        center = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        center.set_hexpand(True)
        center.set_vexpand(True)
        self._video_frame: Gtk.Frame | None = None
        if embedded:
            frame = Gtk.Frame()
            frame.set_shadow_type(Gtk.ShadowType.IN)
            frame.set_hexpand(True)
            frame.set_vexpand(True)
            video.set_hexpand(True)
            video.set_vexpand(True)
            video.set_size_request(480, 270)
            frame.add(video)
            self._video_frame = frame
            center.pack_start(frame, True, True, 0)
        else:
            placeholder = Gtk.Label(
                label="Video plays in the separate mpv window.\n"
                "Use Fullscreen (or F11), or press f while mpv is focused."
            )
            placeholder.set_line_wrap(True)
            placeholder.set_justify(Gtk.Justification.CENTER)
            placeholder.set_vexpand(True)
            placeholder.set_valign(Gtk.Align.CENTER)
            center.pack_start(placeholder, True, True, 0)
        columns.pack_start(center, True, True, 0)

        self._right = self._side_rail()
        self._right.pack_start(self._section_label("Seek forward"), False, False, 0)
        for label, seconds in [("Forward 10s", 10), ("Forward 30s", 30)]:
            self._right.pack_start(self._seek_button(label, seconds), False, False, 0)
        self._right.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 4
        )
        self._right.pack_start(self._section_label("Display"), False, False, 0)
        fs_btn = Gtk.Button(label="Fullscreen")
        fs_btn.connect("clicked", self.toggle_fullscreen)
        self._right.pack_start(fs_btn, False, False, 0)
        self.status = Gtk.Label(label="Player starting...")
        self.status.set_line_wrap(True)
        self.status.set_xalign(0.0)
        self.status.set_max_width_chars(24)
        self._right.pack_start(self.status, False, False, 0)
        self.mode_label = Gtk.Label(label=mode_hint)
        self.mode_label.set_opacity(0.7)
        self.mode_label.set_line_wrap(True)
        self.mode_label.set_xalign(0.0)
        self.mode_label.set_max_width_chars(24)
        self._right.pack_start(self.mode_label, False, False, 0)
        self._right.pack_end(Gtk.Label(), True, True, 0)
        columns.pack_start(self._right, False, False, 0)

        self.widget.pack_start(columns, True, True, 0)

    def set_chrome_visible(self, visible: bool) -> None:
        """Show/hide side rails and URL strip so video can fill the window."""
        self._chrome_visible = visible
        for part in (self._top, self._left, self._right):
            if visible:
                part.show_all()
            else:
                part.hide()
        if visible:
            self.widget.set_border_width(10)
            if self._video_frame is not None:
                self._video_frame.set_shadow_type(Gtk.ShadowType.IN)
        else:
            self.widget.set_border_width(0)
            if self._video_frame is not None:
                self._video_frame.set_shadow_type(Gtk.ShadowType.NONE)

    def _side_rail(self) -> Gtk.Box:
        rail = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        rail.set_size_request(_SIDE_WIDTH, -1)
        rail.set_valign(Gtk.Align.FILL)
        return rail

    @staticmethod
    def _section_label(text: str) -> Gtk.Label:
        label = Gtk.Label(label=text)
        label.set_xalign(0.0)
        label.set_opacity(0.65)
        return label

    def _action_button(self, label: str, action: tuple) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.connect("clicked", lambda _b, a=action: self.control(a))
        return button

    def _seek_button(self, label: str, seconds: int) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.connect(
            "clicked",
            lambda _b, n=seconds: self.control(("seek", n, "relative")),
        )
        return button

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

    def toggle_fullscreen(self, _button=None) -> None:
        if self._on_toggle_fullscreen is not None:
            self._on_toggle_fullscreen()
            return
        result = self.playback.toggle_mpv_fullscreen()
        if result.get("error") == "success":
            self.status.set_text("Toggled fullscreen")
        elif result.get("error") != "embedded-uses-gtk-window":
            self.status.set_text("Player not ready")

    def set_status(self, text: str) -> None:
        self.status.set_text(text)
