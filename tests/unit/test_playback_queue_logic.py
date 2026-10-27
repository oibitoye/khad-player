"""Playback queue-preserving logic with a fake backend."""

from __future__ import annotations

from typing import Any

from khad_media_player.player.playback_service import PlaybackService


class FakeBackend:
    def __init__(self, *, support_insert_next_play: bool = True) -> None:
        self.calls: list[tuple[Any, ...]] = []
        self.idle = True
        self.playlist_count = 0
        self.playlist_pos = 0
        self.support_insert_next_play = support_insert_next_play

    def command(self, *args: Any) -> dict[str, Any]:
        self.calls.append(args)
        if args == ("get_property", "idle-active"):
            return {"error": "success", "data": self.idle}
        if args == ("get_property", "playlist-pos"):
            return {"error": "success", "data": self.playlist_pos}
        if args == ("get_property", "playlist-count"):
            return {"error": "success", "data": self.playlist_count}
        if args and args[0] == "loadfile" and len(args) > 2:
            flag = args[2]
            if flag == "insert-next-play" and not self.support_insert_next_play:
                return {"error": "Invalid value for mpv parameter"}
            if flag in {"append-play", "insert-next-play", "append"}:
                self.playlist_count += 1
                self.idle = False
                return {"error": "success"}
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
    # insert-next-play already starts playback — no playlist-next needed
    assert ("playlist-next", "force") not in fake.calls


def test_play_preserving_queue_falls_back_without_insert_next_play() -> None:
    service = PlaybackService.__new__(PlaybackService)
    fake = FakeBackend(support_insert_next_play=False)
    fake.idle = False
    fake.playlist_count = 2
    fake.playlist_pos = 0
    service.on_history = None
    service._backend = fake  # type: ignore[attr-defined]
    result = PlaybackService.play_preserving_queue(service, "https://example.com/v")
    assert result.get("error") == "success"
    assert ("loadfile", "https://example.com/v", "append") in fake.calls
    assert ("playlist-move", 2, 1) in fake.calls
    assert ("playlist-next", "force") in fake.calls


def test_mpv_truthy_accepts_yes_string() -> None:
    assert PlaybackService._mpv_truthy("yes") is True
    assert PlaybackService._mpv_truthy(False) is False
