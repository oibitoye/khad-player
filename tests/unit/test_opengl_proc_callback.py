"""OpenGL proc-address helper must expose a ctypes CFUNCTYPE for python-mpv."""

from __future__ import annotations

import ctypes
import types

from khad_media_player.player.opengl_proc import (
    MpvGlGetProcAddressFn,
    OPEN_GL_GET_PROC_ADDRESS,
    get_opengl_proc_address_callback,
)


def test_get_proc_address_is_cfunction_type() -> None:
    callback = get_opengl_proc_address_callback()
    assert callback is OPEN_GL_GET_PROC_ADDRESS
    assert callable(callback)
    assert not isinstance(callback, types.FunctionType)
    assert type(callback).__name__ == "CFunctionType"
    result = callback(None, b"")
    assert result in (0, None) or isinstance(result, int)


def test_callback_type_matches_python_mpv_signature() -> None:
    assert MpvGlGetProcAddressFn.restype is ctypes.c_void_p
    assert list(MpvGlGetProcAddressFn.argtypes) == [
        ctypes.c_void_p,
        ctypes.c_char_p,
    ]
