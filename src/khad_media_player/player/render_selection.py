"""Choose embedded vs external playback with safe fallback."""

from __future__ import annotations

import logging
import os

from khad_media_player.config import ENV_RENDER_MODE
from khad_media_player.player.backend import PlaybackBackend, RenderMode
from khad_media_player.player.embedded_backend import (
    EmbeddedBackend,
    embedded_prerequisites,
)
from khad_media_player.player.external_backend import ExternalBackend

logger = logging.getLogger(__name__)


def requested_render_mode() -> str:
    """Return auto | embedded | external from the environment."""
    value = os.environ.get(ENV_RENDER_MODE, "auto").strip().lower()
    if value in {"auto", "embedded", "external"}:
        return value
    return "auto"


def create_backend(preferred: RenderMode | None = None) -> tuple[PlaybackBackend, RenderMode, str]:
    """
    Create the best available backend.

    Returns (backend, active_mode, note).
    """
    request = preferred.value if preferred else requested_render_mode()
    if request == "external":
        return ExternalBackend(), RenderMode.EXTERNAL, "Forced external mode"

    if request in {"auto", "embedded"}:
        ok, reason = embedded_prerequisites()
        if not ok:
            if request == "embedded":
                logger.warning(
                    "Embedded requested but unavailable (%s); falling back to external",
                    reason,
                )
            return (
                ExternalBackend(),
                RenderMode.EXTERNAL,
                f"Fallback to external: {reason}",
            )
        backend = EmbeddedBackend()
        backend.start()
        if backend.is_ready():
            return (
                backend,
                RenderMode.EMBEDDED,
                "Using embedded libmpv Render API",
            )
        logger.warning(
            "Embedded libmpv failed to start (%s); falling back to external",
            backend.init_error,
        )
        return (
            ExternalBackend(),
            RenderMode.EXTERNAL,
            f"Fallback to external: {backend.init_error or 'start failed'}",
        )

    return ExternalBackend(), RenderMode.EXTERNAL, "Default external mode"
