"""Cross-platform filesystem locations for data, config, cache, and IPC."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from khad_media_player.config import APP_NAME

LEGACY_DATA_DIR_NAME = "yoga-media-player"
DATA_DIR_NAME = "khad-media-player"


def _xdg_home(env_var: str, default_subdir: str) -> Path:
    override = os.environ.get(env_var)
    if override:
        return Path(override).expanduser()
    return Path.home() / default_subdir


def data_dir() -> Path:
    if sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        path = _xdg_home("XDG_DATA_HOME", ".local/share") / DATA_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_dir() -> Path:
    if sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        path = _xdg_home("XDG_CONFIG_HOME", ".config") / DATA_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def cache_dir() -> Path:
    if sys.platform == "darwin":
        path = Path.home() / "Library" / "Caches" / APP_NAME
    else:
        path = _xdg_home("XDG_CACHE_HOME", ".cache") / DATA_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def runtime_dir() -> Path:
    """Private per-user directory for the mpv IPC socket."""
    if sys.platform == "darwin":
        path = Path(tempfile.gettempdir()) / f"khad-media-player-{os.getuid()}"
    else:
        xdg_runtime = os.environ.get("XDG_RUNTIME_DIR")
        if xdg_runtime:
            path = Path(xdg_runtime) / "khad-media-player"
        else:
            path = Path(tempfile.gettempdir()) / f"khad-media-player-{os.getuid()}"
    path.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path, 0o700)
    except OSError:
        pass
    return path


def ipc_socket_path() -> Path:
    return runtime_dir() / "mpv.sock"


def history_path() -> Path:
    return data_dir() / "history.json"


def titles_cache_path() -> Path:
    return data_dir() / "titles.json"


def legacy_data_dir() -> Path:
    return Path.home() / ".local" / "share" / LEGACY_DATA_DIR_NAME


def legacy_history_path() -> Path:
    return legacy_data_dir() / "history.json"


def legacy_titles_path() -> Path:
    return legacy_data_dir() / "titles.json"
