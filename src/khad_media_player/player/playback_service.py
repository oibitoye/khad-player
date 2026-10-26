"""Playback operations shared by UI tabs and future render modes."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Callable

from khad_media_player.config import resolve_mpv_profile
from khad_media_player.paths import ipc_socket_path
from khad_media_player.player.mpv_process import MpvProcess


class RenderMode(str, Enum):
    """Preferred UX is embedded (Phase F); external is the working baseline."""

    EXTERNAL = "external"
    EMBEDDED = "embedded"


class PlaybackService:
    """Control playback without depending on a specific render surface."""

    def __init__(
        self,
        socket_path: Path | None = None,
        render_mode: RenderMode = RenderMode.EXTERNAL,
        on_history: Callable[[str], None] | None = None,
    ) -> None:
        self.socket_path = socket_path or ipc_socket_path()
        self.render_mode = render_mode
        self.on_history = on_history
        self._external = MpvProcess(
            self.socket_path,
            profile=resolve_mpv_profile(),
        )

    @property
    def process(self) -> MpvProcess:
        return self._external

    def start(self) -> None:
        # Embedded mode reuses process/IPC until Phase F lands a libmpv widget.
        self._external.ensure_started()

    def shutdown(self) -> None:
        self._external.terminate()

    def command(self, *args: Any) -> dict[str, Any]:
        return self._external.ipc.command(*args)

    def is_ready(self) -> bool:
        return self._external.ipc.is_ready()

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

            total = count.get("data", 0)
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
        return data if isinstance(data, list) else []
