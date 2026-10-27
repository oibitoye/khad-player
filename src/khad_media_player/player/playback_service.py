"""Playback operations shared by UI tabs across render modes."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from khad_media_player.player.backend import PlaybackBackend, RenderMode
from khad_media_player.player.external_backend import ExternalBackend
from khad_media_player.player.render_selection import create_backend

# Re-export for existing imports
__all__ = ["PlaybackService", "RenderMode"]


class PlaybackService:
    """Control playback without depending on a particular render surface."""

    def __init__(
        self,
        socket_path: Path | None = None,
        render_mode: RenderMode | None = None,
        on_history: Callable[[str], None] | None = None,
    ) -> None:
        self.on_history = on_history
        self._preferred = render_mode
        self._socket_path = socket_path
        self._backend: PlaybackBackend | None = None
        self.render_mode = RenderMode.EXTERNAL
        self.mode_note = ""
        self._video_widget = None

    @property
    def backend(self) -> PlaybackBackend:
        if self._backend is None:
            self.start()
        assert self._backend is not None
        return self._backend

    @property
    def process(self) -> Any:
        """Legacy access used by UI readiness checks for external mode."""
        backend = self.backend
        if isinstance(backend, ExternalBackend):
            return backend.process
        return None

    def start(self) -> None:
        if self._backend is not None:
            return
        backend, mode, note = create_backend(self._preferred)
        if isinstance(backend, ExternalBackend) and self._socket_path is not None:
            backend = ExternalBackend(self._socket_path)
        self._backend = backend
        self.render_mode = mode
        self.mode_note = note
        if isinstance(self._backend, ExternalBackend):
            self._backend.start()
        if self.render_mode == RenderMode.EMBEDDED:
            self._video_widget = self._backend.create_video_widget()

    def video_widget(self):
        return self._video_widget

    def is_embedded(self) -> bool:
        return self.render_mode == RenderMode.EMBEDDED

    def shutdown(self) -> None:
        if self._backend is not None:
            self._backend.shutdown()
            self._backend = None
        self._video_widget = None

    def command(self, *args: Any) -> dict[str, Any]:
        return self.backend.command(*args)

    def is_ready(self) -> bool:
        return self.backend.is_ready()

    def failed_to_start(self) -> bool:
        return self.backend.failed_to_start()

    def play_preserving_queue(self, url: str) -> dict[str, Any]:
        """Play URL without clearing existing playlist items (legacy behaviour)."""
        state = self.command("get_property", "idle-active")
        if state.get("error") != "success":
            return state

        if state.get("data") is True:
            result = self.command("loadfile", url, "append-play")
            if result.get("error") != "success":
                return result

            count = self.command("get_property", "playlist-count")
            if count.get("error") != "success":
                return count

            total = count.get("data", 0) or 0
            if total > 1:
                moved = self.command("playlist-move", total - 1, 0)
                if moved.get("error") != "success":
                    return moved

            return result

        result = self.command("loadfile", url, "insert-next-play")
        if result.get("error") != "success":
            return result

        return self.command("playlist-next", "force")

    def play_url(self, url: str) -> dict[str, Any]:
        result = self.play_preserving_queue(url)
        if result.get("error") == "success" and self.on_history:
            self.on_history(url)
        return result

    def queue_url(self, url: str) -> dict[str, Any]:
        return self.command("loadfile", url, "append")

    def control(self, *action: Any) -> dict[str, Any]:
        return self.command(*action)

    def toggle_mpv_fullscreen(self) -> dict[str, Any]:
        """Toggle fullscreen on the external mpv window (no-op for embedded)."""
        if self.is_embedded():
            return {"error": "embedded-uses-gtk-window"}
        return self.command("cycle", "fullscreen")

    def playback_state_label(self) -> str | None:
        result = self.command("get_property", "idle-active")
        if result.get("error") != "success":
            return None
        if result.get("data") is True:
            return "Stopped"
        paused = self.command("get_property", "pause")
        return "Paused" if paused.get("data") is True else "Playing"

    def get_playlist(self) -> list[dict[str, Any]]:
        result = self.command("get_property", "playlist")
        if result.get("error") != "success":
            return []
        data = result.get("data") or []
        if isinstance(data, list):
            # python-mpv may return MPV playlist objects — normalise to dicts
            normalised: list[dict[str, Any]] = []
            for item in data:
                if isinstance(item, dict):
                    normalised.append(item)
                else:
                    normalised.append(
                        {
                            "filename": getattr(item, "filename", None)
                            or getattr(item, "url", "")
                            or str(item),
                            "title": getattr(item, "title", None),
                            "current": bool(getattr(item, "current", False)),
                        }
                    )
            return normalised
        return []
