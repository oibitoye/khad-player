"""External mpv window backend (legacy baseline / fallback)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from khad_media_player.config import resolve_mpv_profile
from khad_media_player.paths import ipc_socket_path
from khad_media_player.player.backend import PlaybackBackend
from khad_media_player.player.mpv_process import MpvProcess


class ExternalBackend(PlaybackBackend):
    def __init__(self, socket_path: Path | None = None) -> None:
        self.socket_path = socket_path or ipc_socket_path()
        self.process = MpvProcess(
            self.socket_path,
            profile=resolve_mpv_profile(),
        )

    def start(self) -> None:
        self.process.ensure_started()

    def shutdown(self) -> None:
        self.process.terminate()

    def command(self, *args: Any) -> dict[str, Any]:
        return self.process.ipc.command(*args)

    def is_ready(self) -> bool:
        return self.process.ipc.is_ready()

    def failed_to_start(self) -> bool:
        return (
            self.process.process is not None
            and self.process.process.poll() is not None
        )
