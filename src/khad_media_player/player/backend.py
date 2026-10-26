"""Playback backend interface shared by external and embedded modes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class RenderMode(str, Enum):
    """Preferred UX is embedded; external is the working baseline/fallback."""

    EXTERNAL = "external"
    EMBEDDED = "embedded"


class PlaybackBackend(ABC):
    """Normalised control surface; UI must not depend on render mode."""

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def command(self, *args: Any) -> dict[str, Any]:
        """Return a dict shaped like mpv JSON IPC: {error, data?}."""
        raise NotImplementedError

    @abstractmethod
    def is_ready(self) -> bool:
        raise NotImplementedError

    def create_video_widget(self):  # noqa: ANN201 — optional GTK widget
        """Return a GTK widget for in-window video, or None."""
        return None

    def failed_to_start(self) -> bool:
        return False
