"""Executable discovery for mpv and yt-dlp."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from khad_media_player.config import ENV_MPV_PATH, ENV_YTDLP_PATH


@dataclass(frozen=True)
class ResolvedExecutable:
    name: str
    path: Path


class DependencyError(RuntimeError):
    """Raised when a required external tool cannot be found."""


def _candidate_from_env(env_var: str) -> Path | None:
    value = os.environ.get(env_var, "").strip()
    if not value:
        return None
    path = Path(value).expanduser()
    if path.is_file() and os.access(path, os.X_OK):
        return path
    raise DependencyError(
        f"{env_var} is set to '{value}' but it is not an executable file"
    )


def find_executable(name: str, env_var: str | None = None) -> Path:
    if env_var:
        env_path = _candidate_from_env(env_var)
        if env_path is not None:
            return env_path
    found = shutil.which(name)
    if found:
        return Path(found)
    raise DependencyError(
        f"Could not find '{name}' on PATH"
        + (f" (override with {env_var})" if env_var else "")
    )


def find_mpv() -> Path:
    return find_executable("mpv", ENV_MPV_PATH)


def find_ytdlp() -> Path:
    return find_executable("yt-dlp", ENV_YTDLP_PATH)


def check_dependencies() -> dict[str, str | None]:
    """Return a status map for installer / diagnostics scripts."""
    status: dict[str, str | None] = {}
    for label, resolver in (("mpv", find_mpv), ("yt-dlp", find_ytdlp)):
        try:
            status[label] = str(resolver())
        except DependencyError as error:
            status[label] = None
            status[f"{label}_error"] = str(error)
    return status
