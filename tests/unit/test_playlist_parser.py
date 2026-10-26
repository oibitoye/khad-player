"""Unit tests for M3U playlist parsing and filtering."""

from __future__ import annotations

from pathlib import Path

import pytest

from khad_media_player.services.playlist_parser import (
    filter_entries,
    looks_like_hls_manifest,
    parse_m3u_file,
    parse_m3u_text,
    resolve_relative_url,
)


SAMPLE_IPTV = """#EXTM3U
#EXTINF:-1 group-title="News",BBC News
http://example.com/bbc
#EXTINF:-1 group-title="Sports",Sports One
http://example.com/sports
#EXTINF:-1,Ungrouped Channel
http://example.com/other
"""


def test_parse_iptv_groups_and_titles() -> None:
    parsed = parse_m3u_text(SAMPLE_IPTV, source="sample")
    assert len(parsed.entries) == 3
    assert parsed.entries[0].name == "BBC News"
    assert parsed.entries[0].group == "News"
    assert "News" in parsed.groups
    assert "Ungrouped" in parsed.groups


def test_filter_by_query_and_group() -> None:
    parsed = parse_m3u_text(SAMPLE_IPTV)
    matches, total = filter_entries(parsed.entries, query="bbc", group="All Channels")
    assert total == 1
    assert matches[0].name == "BBC News"
    sports, sports_total = filter_entries(parsed.entries, group="Sports")
    assert sports_total == 1
    assert sports[0].group == "Sports"


def test_filter_display_limit() -> None:
    entries = parse_m3u_text(SAMPLE_IPTV).entries
    matches, total = filter_entries(entries, limit=1)
    assert total == 3
    assert len(matches) == 1


def test_utf8_bom_file(tmp_path: Path) -> None:
    path = tmp_path / "channels.m3u"
    path.write_bytes(b"\xef\xbb\xbf" + SAMPLE_IPTV.encode("utf-8"))
    parsed = parse_m3u_file(path)
    assert len(parsed.entries) == 3


def test_hls_manifest_not_treated_as_channel_list() -> None:
    hls = """#EXTM3U
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
segment0.ts
#EXTINF:10.0,
segment1.ts
"""
    assert looks_like_hls_manifest(hls) is True
    parsed = parse_m3u_text(hls)
    assert parsed.entries == []


def test_resolve_relative_url(tmp_path: Path) -> None:
    playlist = tmp_path / "list.m3u"
    playlist.write_text("#EXTM3U\n", encoding="utf-8")
    resolved = resolve_relative_url("media/a.mp4", playlist)
    assert resolved.endswith("media/a.mp4")
    assert resolve_relative_url("https://example.com/a", playlist) == "https://example.com/a"


def test_large_synthetic_playlist(tmp_path: Path) -> None:
    """Synthetic scale test — at least 11,356 entries (work packet requirement)."""
    count = 11356
    path = tmp_path / "large.m3u"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("#EXTM3U\n")
        for index in range(count):
            group = f"Group{index % 50}"
            handle.write(f'#EXTINF:-1 group-title="{group}",Channel {index}\n')
            handle.write(f"http://example.com/stream/{index}\n")
    parsed = parse_m3u_file(path)
    assert len(parsed.entries) == count
    matches, total = filter_entries(parsed.entries, query="channel 100", limit=100)
    assert total >= 1
    assert len(matches) <= 100
