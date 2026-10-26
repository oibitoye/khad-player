"""GTK OpenGL surface for libmpv Render API frames."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

if TYPE_CHECKING:
    from khad_media_player.player.embedded_backend import EmbeddedBackend

logger = logging.getLogger(__name__)


class VideoArea(Gtk.GLArea):
    """Draws mpv frames into the main window when embedded mode is active."""

    def __init__(self, backend: EmbeddedBackend) -> None:
        super().__init__()
        self._backend = backend
        self._render_ready = False
        self.set_auto_render(True)
        self.set_has_depth_buffer(False)
        self.set_has_stencil_buffer(False)
        self.set_required_version(3, 0)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_size_request(320, 180)
        self.connect("realize", self._on_realize)
        self.connect("render", self._on_render)
        self.connect("unrealize", self._on_unrealize)

    def _on_realize(self, *_args) -> None:
        try:
            self.make_current()
            if self.get_error() is not None:
                logger.warning("GLArea realize error: %s", self.get_error())
                return
            ok = self._backend.attach_render_context(self._request_render)
            self._render_ready = ok
            if not ok:
                logger.warning(
                    "libmpv render context not attached: %s",
                    self._backend.init_error,
                )
        except Exception as error:  # noqa: BLE001
            logger.warning("VideoArea realize failed: %s", error)
            self._render_ready = False

    def _request_render(self) -> None:
        GLib.idle_add(self.queue_render)

    def _on_render(self, _area, _context) -> bool:
        if not self._render_ready:
            return False
        scale = self.get_scale_factor()
        width = max(1, int(self.get_allocated_width() * scale))
        height = max(1, int(self.get_allocated_height() * scale))
        self._backend.render_frame(width, height, fbo=0)
        return True

    def _on_unrealize(self, *_args) -> None:
        self._render_ready = False
