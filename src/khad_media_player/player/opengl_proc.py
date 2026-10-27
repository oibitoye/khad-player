"""Resolve OpenGL function addresses for the libmpv Render API."""

from __future__ import annotations

import ctypes
import sys
from functools import lru_cache

# Signature required by python-mpv (MpvGlGetProcAddressFn).
MpvGlGetProcAddressFn = ctypes.CFUNCTYPE(
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_char_p,
)

_GL_DRAW_FRAMEBUFFER_BINDING = 0x8CA6


@lru_cache(maxsize=1)
def _load_cdll(name: str) -> ctypes.CDLL | None:
    try:
        return ctypes.CDLL(name)
    except OSError:
        return None


def _candidate_libs() -> list[ctypes.CDLL]:
    names: list[str]
    if sys.platform == "darwin":
        names = [
            "/System/Library/Frameworks/OpenGL.framework/OpenGL",
            "OpenGL",
        ]
    elif sys.platform.startswith("linux"):
        # Prefer EGL (Wayland / Gtk.GLArea) before classic GLX.
        names = [
            "libEGL.so.1",
            "libEGL.so",
            "libGL.so.1",
            "libGL.so",
            "libGLX.so.0",
        ]
    else:
        names = ["opengl32.dll"]
    libs: list[ctypes.CDLL] = []
    seen: set[int] = set()
    for name in names:
        lib = _load_cdll(name)
        if lib is None:
            continue
        key = id(lib)
        if key in seen:
            continue
        seen.add(key)
        libs.append(lib)
    return libs


@lru_cache(maxsize=1)
def _opengl_lib() -> ctypes.CDLL | None:
    libs = _candidate_libs()
    return libs[0] if libs else None


def _lookup_proc_address(name_bytes: bytes) -> int:
    for lib in _candidate_libs():
        if hasattr(lib, "eglGetProcAddress"):
            lib.eglGetProcAddress.restype = ctypes.c_void_p
            lib.eglGetProcAddress.argtypes = [ctypes.c_char_p]
            addr = lib.eglGetProcAddress(name_bytes)
            if addr:
                return int(addr)

        if hasattr(lib, "glXGetProcAddress"):
            lib.glXGetProcAddress.restype = ctypes.c_void_p
            lib.glXGetProcAddress.argtypes = [ctypes.c_char_p]
            addr = lib.glXGetProcAddress(name_bytes)
            if addr:
                return int(addr)

        if hasattr(lib, "glXGetProcAddressARB"):
            lib.glXGetProcAddressARB.restype = ctypes.c_void_p
            lib.glXGetProcAddressARB.argtypes = [ctypes.c_char_p]
            addr = lib.glXGetProcAddressARB(name_bytes)
            if addr:
                return int(addr)

        symbol = name_bytes.decode("utf-8", errors="replace")
        try:
            value = ctypes.cast(getattr(lib, symbol), ctypes.c_void_p).value
            if value:
                return int(value)
        except AttributeError:
            continue
    return 0


def _get_opengl_proc_address_impl(_ctx: object, name: bytes | None) -> int:
    """ctypes-facing lookup used by libmpv via python-mpv."""
    if not name:
        return 0
    name_bytes = name if isinstance(name, bytes) else bytes(name)
    return _lookup_proc_address(name_bytes)


# Keep a process-lifetime reference so the callback is not garbage-collected.
OPEN_GL_GET_PROC_ADDRESS = MpvGlGetProcAddressFn(_get_opengl_proc_address_impl)


def get_opengl_proc_address_callback():
    """Return the CFUNCTYPE instance python-mpv expects."""
    return OPEN_GL_GET_PROC_ADDRESS


def current_draw_framebuffer() -> int:
    """Return GL_DRAW_FRAMEBUFFER_BINDING for the current context."""
    lib = _opengl_lib()
    if lib is None or not hasattr(lib, "glGetIntegerv"):
        # Try every candidate — binding may live on libGL while EGL was first.
        for candidate in _candidate_libs():
            if hasattr(candidate, "glGetIntegerv"):
                lib = candidate
                break
        else:
            return 0
    value = ctypes.c_int(0)
    lib.glGetIntegerv.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_int)]
    lib.glGetIntegerv.restype = None
    try:
        lib.glGetIntegerv(_GL_DRAW_FRAMEBUFFER_BINDING, ctypes.byref(value))
    except Exception:  # noqa: BLE001
        return 0
    return int(value.value)


def opengl_available() -> bool:
    return _opengl_lib() is not None
