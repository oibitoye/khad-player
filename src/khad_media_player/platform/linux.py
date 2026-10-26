"""Linux platform adapter."""

from __future__ import annotations

from pathlib import Path

from khad_media_player import paths
from khad_media_player.config import default_profile_name
from khad_media_player.platform.base import PlatformAdapter


class LinuxPlatform(PlatformAdapter):
    def data_dir(self) -> Path:
        return paths.data_dir()

    def config_dir(self) -> Path:
        return paths.config_dir()

    def cache_dir(self) -> Path:
        return paths.cache_dir()

    def runtime_dir(self) -> Path:
        return paths.runtime_dir()

    def default_mpv_profile(self) -> str:
        return default_profile_name()
