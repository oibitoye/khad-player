"""Lifecycle management for an owned external mpv process."""

from __future__ import annotations

import subprocess
from pathlib import Path

from khad_media_player.config import MpvProfile, mpv_startup_args, resolve_mpv_profile
from khad_media_player.dependencies import find_mpv
from khad_media_player.player.mpv_ipc import MpvIpcClient


class MpvProcess:
    """Start and stop the mpv instance owned by this application."""

    def __init__(
        self,
        socket_path: Path,
        profile: MpvProfile | None = None,
        executable: Path | None = None,
    ) -> None:
        self.socket_path = Path(socket_path)
        self.profile = profile or resolve_mpv_profile()
        self.executable = executable
        self.process: subprocess.Popen[bytes] | None = None
        self.ipc = MpvIpcClient(self.socket_path)

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def ensure_started(self) -> None:
        if self.is_running():
            return

        if self.socket_path.exists():
            if self.ipc.is_ready():
                return
            try:
                self.socket_path.unlink(missing_ok=True)
            except OSError:
                pass

        mpv_path = self.executable or find_mpv()
        args = [str(mpv_path), *mpv_startup_args(str(self.socket_path), self.profile)]
        self.process = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def terminate(self) -> None:
        """Terminate only the process started by this instance."""
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None
        if self.socket_path.exists() and not self.ipc.is_ready():
            try:
                self.socket_path.unlink(missing_ok=True)
            except OSError:
                pass
