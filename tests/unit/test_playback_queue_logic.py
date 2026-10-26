"""Playback queue-preserving logic with a fake backend."""

from __future__ import annotations

from typing import Any

from khad_media_player.player.playback_service import PlaybackService


class FakeBackend:
    def __init__(self) -> None:
        self.calls: list[tuple[Any, ...]] = []
        self.idle = True
        self.playlist_count = 0

    def command(self, *args: Any) -> dict[str, Any]:
        self.calls.append(args)
        if args == ("get_property", "idle-active"):
            return {"error": "success", "data": self.idle}
        if args and args[0] == "loadfile" and len(args) > 2 and args[2] in {
            "append-play",
            "insert-next-play",
            "append",
        }:
            self.playlist_count += 1
            self.idle = False
            return {"error": "success"}
        if args == ("get_property", "playlist-count"):
            return {"error": "success", "data": self.playlist_count}
        if args[0] == "playlist-move":
            return {"error": "success"}
        if args == ("playlist-next", "force"):
            return {"error": "success"}
        return {"error": "success"}


def test_play_preserving_queue_when_idle_moves_to_front() -> None:
    service = PlaybackService.__new__(PlaybackService)
    fake = FakeBackend()
    service.on_history = None
    service._backend = fake  # type: ignore[attr-defined]

    original_command = fake.command

    def command_with_existing_queue(*args):
        result = original_command(*args)
        if args and args[0] == "loadfile" and len(args) > 2 and args[2] == "append-play":
            fake.playlist_count = 3
        if args == ("get_property", "playlist-count"):
            return {"error": "success", "data": fake.playlist_count}
        return result

    fake.command = command_with_existing_queue  # type: ignore[method-assign]
    result = PlaybackService.play_preserving_queue(service, "https://example.com/v")
    assert result.get("error") == "success"
    assert ("playlist-move", 2, 0) in fake.calls


def test_play_preserving_queue_when_busy_uses_insert_next() -> None:
    service = PlaybackService.__new__(PlaybackService)
    fake = FakeBackend()
    fake.idle = False
    service.on_history = None
    service._backend = fake  # type: ignore[attr-defined]
    result = PlaybackService.play_preserving_queue(service, "https://example.com/v")
    assert result.get("error") == "success"
    assert ("loadfile", "https://example.com/v", "insert-next-play") in fake.calls
    assert ("playlist-next", "force") in fake.calls
