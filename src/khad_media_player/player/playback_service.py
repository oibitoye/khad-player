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

    @staticmethod
    def _mpv_truthy(value: Any) -> bool:
        return value is True or value in (1, "yes", "true")

    def play_preserving_queue(self, url: str) -> dict[str, Any]:
        """Play URL without clearing existing playlist items (legacy behaviour)."""
        state = self.command("get_property", "idle-active")
        if state.get("error") != "success":
            return state

        if self._mpv_truthy(state.get("data")):
            result = self.command("loadfile", url, "append-play")
            if result.get("error") != "success":
                return result

            count = self.command("get_property", "playlist-count")
            if count.get("error") != "success":
                return count

            total = int(count.get("data", 0) or 0)
            if total > 1:
                moved = self.command("playlist-move", total - 1, 0)
                if moved.get("error") != "success":
                    return moved

            return result

        # Preferred on mpv >= 0.37 (insert-next-play starts playback itself).
        result = self.command("loadfile", url, "insert-next-play")
        if result.get("error") == "success":
            return result

        # Bookworm / libmpv 0.35: insert-next-play is invalid (-4).
        return self._play_next_preserving_queue_legacy(url)

    def _play_next_preserving_queue_legacy(self, url: str) -> dict[str, Any]:
        """Queue-preserving play-next for mpv builds without insert-next-play."""
        pos = self.command("get_property", "playlist-pos")
        count = self.command("get_property", "playlist-count")
        if count.get("error") != "success":
            return count

        old_count = int(count.get("data", 0) or 0)
        current = pos.get("data")
        try:
            current_index = int(current) if current is not None and current != -1 else -1
        except (TypeError, ValueError):
            current_index = -1

        result = self.command("loadfile", url, "append")
        if result.get("error") != "success":
            return result

        new_index = old_count
        target = current_index + 1 if current_index >= 0 else 0
        if new_index != target:
            moved = self.command("playlist-move", new_index, target)
            if moved.get("error") != "success":
                return moved

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

    def playback_state_label(self) -> str | None:
        result = self.command("get_property", "idle-active")
        if result.get("error") != "success":
            return None
        if self._mpv_truthy(result.get("data")):
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
