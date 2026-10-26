"""M3U / M3U8 channel playlist parsing (extracted from legacy load_m3u_browser)."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from khad_media_player.models.playlist import ParsedPlaylist, PlaylistEntry

EXTINF_GROUP = re.compile(r'group-title="([^"]*)"')


def looks_like_hls_manifest(text: str) -> bool:
    """True when content is an HLS media/master playlist, not an IPTV channel list."""
    upper_lines = [line.strip().upper() for line in text.splitlines() if line.strip()]
    if not upper_lines:
        return False
    if upper_lines[0] != "#EXTM3U":
        return False
    hls_markers = (
        "#EXT-X-TARGETDURATION",
        "#EXT-X-MEDIA-SEQUENCE",
        "#EXT-X-STREAM-INF",
        "#EXT-X-KEY",
        "#EXTINF:",
    )
    # Channel lists typically use #EXTINF with commas and http URLs without HLS tags.
    has_hls = any(any(line.startswith(m) for m in hls_markers[0:4]) for line in upper_lines)
    has_extinf = any(line.startswith("#EXTINF:") for line in upper_lines)
    if has_hls and has_extinf:
        # Distinguishing: HLS EXTINF rarely includes group-title / long titles with commas
        # the way IPTV lists do. Prefer HLS if transport tags present.
        return True
    if has_hls:
        return True
    return False


def is_direct_stream_url(url: str) -> bool:
    lowered = url.lower().split("?", 1)[0]
    return lowered.endswith(".m3u8")


def parse_m3u_text(text: str, source: str = "") -> ParsedPlaylist:
    if looks_like_hls_manifest(text):
        # Pure HLS transport/master playlists are not IPTV channel lists.
        iptv_signal = "group-title=" in text
        for line in text.splitlines():
            if line.startswith("#EXTINF:") and "," in line:
                title = line.split(",", 1)[1].strip()
                if title:
                    iptv_signal = True
                    break
        if not iptv_signal:
            return ParsedPlaylist(entries=[], source=source)

    entries: list[PlaylistEntry] = []
    name = ""
    group = "Ungrouped"

    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("#EXTINF:"):
            name = line.split(",", 1)[-1].strip()
            match = EXTINF_GROUP.search(line)
            group = (
                match.group(1).strip()
                if match and match.group(1).strip()
                else "Ungrouped"
            )
        elif line and not line.startswith("#"):
            entries.append(PlaylistEntry(name=name or line, group=group, url=line))
            name = ""
            group = "Ungrouped"

    return ParsedPlaylist(entries=entries, source=source)


def parse_m3u_file(path: Path | str) -> ParsedPlaylist:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8-sig", errors="replace")
    return parse_m3u_text(text, source=str(file_path))


def resolve_relative_url(entry_url: str, playlist_path: Path) -> str:
    parsed = urlparse(entry_url)
    if parsed.scheme in ("http", "https", "file") or entry_url.startswith("/"):
        return entry_url
    return str((playlist_path.parent / entry_url).resolve())


def filter_entries(
    entries: list[PlaylistEntry],
    query: str = "",
    group: str | None = None,
    limit: int | None = None,
) -> tuple[list[PlaylistEntry], int]:
    needle = query.strip().casefold()
    matches: list[PlaylistEntry] = []
    total = 0
    for entry in entries:
        if needle and needle not in entry.name.casefold():
            continue
        if group and group != "All Channels" and entry.group != group:
            continue
        total += 1
        if limit is None or len(matches) < limit:
            matches.append(entry)
    return matches, total
