"""Platform abstraction interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class PlatformAdapter(ABC):
    @abstractmethod
    def data_dir(self) -> Path:
        raise NotImplementedError

    @abstractmethod
    def config_dir(self) -> Path:
        raise NotImplementedError

    @abstractmethod
    def cache_dir(self) -> Path:
        raise NotImplementedError

    @abstractmethod
    def runtime_dir(self) -> Path:
        raise NotImplementedError

    @abstractmethod
    def default_mpv_profile(self) -> str:
        raise NotImplementedError
