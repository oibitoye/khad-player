"""Embedded libmpv backend using the Render API (not window-handle embedding)."""

from __future__ import annotations

import logging
from typing import Any

from khad_media_player.config import YTDL_FORMAT
from khad_media_player.player.backend import PlaybackBackend
from khad_media_player.player.opengl_proc import (
    current_draw_framebuffer,
    get_opengl_proc_address_callback,
    opengl_available,
)

logger = logging.getLogger(__name__)


def _format_mpv_error(error: BaseException) -> str:
    """Turn python-mpv's tuple-like errors into a short UI message."""
    args = getattr(error, "args", ())
    if args and isinstance(args[0], str) and args[0].strip():
        return args[0]
    text = str(error).strip()
    return text or "Player not ready"


def libmpv_importable() -> bool:
    try:
        import mpv  # noqa: F401
    except Exception:
        return False
    return True


def embedded_prerequisites() -> tuple[bool, str]:
    if not libmpv_importable():
        return False, "python-mpv (module 'mpv') is not installed or libmpv is missing"
    if not opengl_available():
        return False, "OpenGL library not available for libmpv Render API"
    return True, ""


class EmbeddedBackend(PlaybackBackend):
    """In-process libmpv player; video is drawn via MpvRenderContext into Gtk.GLArea."""

    def __init__(self) -> None:
        self._mpv = None
        self._render_ctx = None
        self._ready = False
        self._init_error = ""
        self._update_callback = None

    def start(self) -> None:
        ok, reason = embedded_prerequisites()
        if not ok:
            self._init_error = reason
            logger.warning("Embedded backend unavailable: %s", reason)
            return
        try:
            import mpv

            self._mpv = mpv.MPV(
                vo="libmpv",
                idle="yes",
                force_window="no",
                keep_open="yes",
                osc="no",
                input_default_bindings="no",
                input_vo_keyboard="no",
                stop_screensaver=True,
                ytdl="yes",
                ytdl_format=YTDL_FORMAT,
                prefetch_playlist="yes",
            )
            self._ready = True
        except Exception as error:  # noqa: BLE001 — fall back at service layer
            self._init_error = str(error)
            self._mpv = None
            self._ready = False
            logger.warning("Failed to start embedded libmpv: %s", error)

    def attach_render_context(self, on_update) -> bool:
        """Create OpenGL render context after the GLArea is realized."""
        if self._mpv is None:
            return False
        if self._render_ctx is not None:
            return True
        try:
            import mpv

            self._update_callback = on_update
            # Must be a ctypes CFUNCTYPE, not a plain Python function.
            self._get_proc_address = get_opengl_proc_address_callback()
            self._render_ctx = mpv.MpvRenderContext(
                self._mpv,
                "opengl",
                opengl_init_params={"get_proc_address": self._get_proc_address},
            )
            self._render_ctx.update_cb = on_update
            return True
        except Exception as error:  # noqa: BLE001
            self._init_error = f"Render context failed: {error}"
            logger.warning(self._init_error)
            self._render_ctx = None
            return False

    def render_frame(self, width: int, height: int, fbo: int | None = None) -> bool:
        if self._render_ctx is None or width <= 0 or height <= 0:
            return False
        try:
            target_fbo = current_draw_framebuffer() if fbo is None else fbo
            if self._render_ctx.update():
                self._render_ctx.render(
                    flip_y=True,
                    opengl_fbo={"w": width, "h": height, "fbo": target_fbo},
                )
            return True
        except Exception as error:  # noqa: BLE001
            logger.debug("Render frame error: %s", error)
            return False

    def create_video_widget(self):
        from khad_media_player.ui.video_area import VideoArea

        return VideoArea(self)

    def shutdown(self) -> None:
        if self._render_ctx is not None:
            try:
                self._render_ctx.free()
            except Exception:  # noqa: BLE001
                pass
            self._render_ctx = None
        if self._mpv is not None:
            try:
                self._mpv.terminate()
            except Exception:  # noqa: BLE001
                pass
            self._mpv = None
        self._ready = False

    def command(self, *args: Any) -> dict[str, Any]:
        if self._mpv is None:
            return {"error": "Player not ready"}
        try:
            # python-mpv command returns property values or None
            name = str(args[0]) if args else ""
            if name == "get_property" and len(args) >= 2:
                prop = str(args[1]).replace("-", "_")
                # Prefer attribute access for common properties
                value = getattr(self._mpv, prop, None)
                if value is None:
                    value = self._mpv.command("get_property", args[1])
                return {"error": "success", "data": value}
            if name == "set_property" and len(args) >= 3:
                self._mpv.command("set_property", args[1], args[2])
                return {"error": "success"}
            result = self._mpv.command(*args)
            return {"error": "success", "data": result}
        except Exception as error:  # noqa: BLE001
            return {"error": _format_mpv_error(error)}

    def is_ready(self) -> bool:
        return self._ready and self._mpv is not None

    def failed_to_start(self) -> bool:
        return bool(self._init_error) and self._mpv is None

    @property
    def init_error(self) -> str:
        return self._init_error
