"""Optional mpv integration — skips when mpv is unavailable."""

from __future__ import annotations

import shutil
import time
from pathlib import Path

import pytest

from khad_media_player.config import resolve_mpv_profile
from khad_media_player.player.mpv_process import MpvProcess


pytestmark = pytest.mark.skipif(
    shutil.which("mpv") is None, reason="mpv not installed"
)


def test_mpv_ipc_ready_and_shutdown(tmp_path: Path) -> None:
    socket_path = tmp_path / "test-mpv.sock"
    process = MpvProcess(socket_path, profile=resolve_mpv_profile("low-resource"))
    process.ensure_started()
    ready = False
    for _ in range(40):
        if process.ipc.is_ready():
            ready = True
            break
        time.sleep(0.1)
    assert ready, "mpv IPC did not become ready"
    version = process.ipc.command("get_property", "mpv-version")
    assert version.get("error") == "success"
    process.terminate()
    assert process.process is None or process.process.poll() is not None
