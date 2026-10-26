"""YouTube search via yt-dlp (extracted from legacy search_worker)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Callable

from khad_media_player.config import SEARCH_RESULT_COUNT
from khad_media_player.dependencies import find_ytdlp
from khad_media_player.models.media import MediaItem
from khad_media_player.services.title_cache import TitleCache


SearchCallback = Callable[[list[MediaItem], str], None]


class YouTubeSearchService:
    def __init__(
        self,
        ytdlp_path: Path | None = None,
        title_cache: TitleCache | None = None,
        result_count: int = SEARCH_RESULT_COUNT,
    ) -> None:
        self._ytdlp_path = ytdlp_path
        self.title_cache = title_cache or TitleCache()
        self.result_count = result_count
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def reset(self) -> None:
        self._cancelled = False

    def search(self, query: str) -> tuple[list[MediaItem], str]:
        ytdlp = self._ytdlp_path or find_ytdlp()
        try:
            result = subprocess.run(
                [
                    str(ytdlp),
                    "--flat-playlist",
                    "--dump-json",
                    "--no-warnings",
                    f"ytsearch{self.result_count}:{query}",
                ],
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            return [], str(error)

        if self._cancelled:
            return [], "Search cancelled"

        entries: list[MediaItem] = []
        for line in result.stdout.splitlines():
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            # Prefer video results; skip entries without an id.
            video_id = item.get("id") or ""
            if not video_id:
                continue
            entries.append(
                MediaItem(
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    title=item.get("title") or "Untitled",
                    duration=item.get("duration"),
                    video_id=str(video_id),
                )
            )

        error = (
            result.stderr.strip().splitlines()[-1]
            if result.returncode and result.stderr.strip()
            else ""
        )

        try:
            self.title_cache.update_many(
                [(e.video_id, e.title, e.duration) for e in entries]
            )
        except OSError:
            pass

        return entries, error
