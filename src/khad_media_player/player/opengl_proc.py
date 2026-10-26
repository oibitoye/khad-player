"""Resolve OpenGL function addresses for the libmpv Render API."""

from __future__ import annotations

import ctypes
import sys
from functools import lru_cache


@lru_cache(maxsize=1)
def _opengl_lib() -> ctypes.CDLL | None:
    names: list[str]
    if sys.platform == "darwin":
        names = [
            "/System/Library/Frameworks/OpenGL.framework/OpenGL",
            "OpenGL",
        ]
    elif sys.platform.startswith("linux"):
        names = ["libGL.so.1", "libGL.so", "libEGL.so.1", "libEGL.so"]
    else:
        names = ["opengl32.dll"]
    for name in names:
        try:
            return ctypes.CDLL(name)
        except OSError:
            continue
    return None


def get_opengl_proc_address(_ctx: object, name: bytes | str) -> int:
    """Return a function pointer for libmpv's get_proc_address callback."""
    if isinstance(name, bytes):
        symbol = name.decode("utf-8", errors="replace")
        name_bytes = name
    else:
        symbol = name
        name_bytes = name.encode("utf-8")

    lib = _opengl_lib()
    if lib is None:
        return 0

    # EGL
    if hasattr(lib, "eglGetProcAddress"):
        lib.eglGetProcAddress.restype = ctypes.c_void_p
        lib.eglGetProcAddress.argtypes = [ctypes.c_char_p]
        addr = lib.eglGetProcAddress(name_bytes)
        if addr:
            return addr

    # GLX
    if hasattr(lib, "glXGetProcAddress"):
        lib.glXGetProcAddress.restype = ctypes.c_void_p
        lib.glXGetProcAddress.argtypes = [ctypes.c_char_p]
        addr = lib.glXGetProcAddress(name_bytes)
        if addr:
            return addr
    if hasattr(lib, "glXGetProcAddressARB"):
        lib.glXGetProcAddressARB.restype = ctypes.c_void_p
        lib.glXGetProcAddressARB.argtypes = [ctypes.c_char_p]
        addr = lib.glXGetProcAddressARB(name_bytes)
        if addr:
            return addr

    # Direct symbol lookup (common on macOS)
    try:
        return ctypes.cast(getattr(lib, symbol), ctypes.c_void_p).value or 0
    except AttributeError:
        return 0


def opengl_available() -> bool:
    return _opengl_lib() is not None
