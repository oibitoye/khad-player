"""Select the platform adapter for the current OS."""

from __future__ import annotations

import sys

from khad_media_player.platform.base import PlatformAdapter
from khad_media_player.platform.linux import LinuxPlatform
from khad_media_player.platform.macos import MacOSPlatform


def get_platform() -> PlatformAdapter:
    if sys.platform == "darwin":
        return MacOSPlatform()
    return LinuxPlatform()


__all__ = ["PlatformAdapter", "get_platform", "LinuxPlatform", "MacOSPlatform"]
