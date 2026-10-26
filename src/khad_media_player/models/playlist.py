"""Playlist / IPTV channel models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlaylistEntry:
    name: str
    group: str
    url: str


@dataclass(frozen=True)
class ParsedPlaylist:
    entries: list[PlaylistEntry]
    source: str = ""

    @property
    def groups(self) -> list[str]:
        return sorted({entry.group for entry in self.entries}, key=str.casefold)
