"""Prevent screen lock / idle sleep while media is actively playing."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _inhibit_flags() -> Any:
    from gi.repository import Gtk

    return Gtk.ApplicationInhibitFlags.IDLE | Gtk.ApplicationInhibitFlags.SUSPEND


class IdleInhibitor:
    """Hold a Gtk.Application inhibit cookie while playback is active.

    Uses IDLE + SUSPEND flags so the session does not blank or suspend
    mid-video. Harmless no-op if the desktop rejects inhibit.
    """

    def __init__(self, application: Any, window: Any) -> None:
        self._application = application
        self._window = window
        self._cookie: int | None = None

    @property
    def active(self) -> bool:
        return self._cookie is not None

    def set_playing(self, playing: bool) -> None:
        if playing:
            self.inhibit()
        else:
            self.release()

    def inhibit(self) -> None:
        if self._cookie is not None:
            return
        try:
            flags = _inhibit_flags()
            cookie = self._application.inhibit(
                self._window,
                flags,
                "Playing media",
            )
        except Exception as error:  # noqa: BLE001 — desktop may lack inhibit
            logger.debug("Idle inhibit unavailable: %s", error)
            return
        # Gtk returns 0 when inhibit fails.
        if cookie:
            self._cookie = int(cookie)
            logger.debug("Idle inhibit acquired (cookie=%s)", self._cookie)

    def release(self) -> None:
        if self._cookie is None:
            return
        cookie = self._cookie
        self._cookie = None
        try:
            self._application.uninhibit(cookie)
            logger.debug("Idle inhibit released (cookie=%s)", cookie)
        except Exception as error:  # noqa: BLE001
            logger.debug("Idle uninhibit failed: %s", error)
