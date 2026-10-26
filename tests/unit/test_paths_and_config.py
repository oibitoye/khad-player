"""Path and configuration unit tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from khad_media_player.config import (
    ENV_RENDER_PROFILE,
    mpv_startup_args,
    resolve_mpv_profile,
)
from khad_media_player.dependencies import DependencyError, find_executable
from khad_media_player.paths import ipc_socket_path


def test_mpv_profile_includes_ipc_and_not_linux_only_on_override(monkeypatch) -> None:
    monkeypatch.setenv(ENV_RENDER_PROFILE, "macos-standard")
    profile = resolve_mpv_profile()
    args = mpv_startup_args("/tmp/test.sock", profile)
    assert any(a.startswith("--input-ipc-server=") for a in args)
    assert "--gpu-context=wayland" not in args
    assert "--hwdec=vaapi" not in args


def test_linux_wayland_profile_keeps_legacy_flags(monkeypatch) -> None:
    monkeypatch.setenv(ENV_RENDER_PROFILE, "linux-wayland")
    profile = resolve_mpv_profile()
    assert "--hwdec=vaapi" in profile.options
    assert "--gpu-context=wayland" in profile.options


def test_ipc_socket_under_runtime_dir() -> None:
    socket_path = ipc_socket_path()
    assert socket_path.name == "mpv.sock"
    assert socket_path.parent.exists()


def test_find_executable_env_override(tmp_path: Path, monkeypatch) -> None:
    fake = tmp_path / "fake-mpv"
    fake.write_text("#!/bin/sh\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.setenv("KHAD_MPV_PATH", str(fake))
    assert find_executable("mpv", "KHAD_MPV_PATH") == fake


def test_find_executable_missing(monkeypatch) -> None:
    monkeypatch.delenv("KHAD_MPV_PATH", raising=False)
    monkeypatch.setenv("PATH", "")
    with pytest.raises(DependencyError):
        find_executable("mpv-definitely-missing-xyz", "KHAD_MPV_PATH")
