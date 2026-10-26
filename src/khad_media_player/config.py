"""Application configuration and mpv renderer profiles."""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field

APP_NAME = "Khad Media Player"
APP_ID = "io.khad.MediaPlayer"
LEGACY_APP_ID = "io.yoga.MediaPlayer"

HISTORY_LIMIT = 100
M3U_DISPLAY_LIMIT = 100
SEARCH_RESULT_COUNT = 6
YTDL_FORMAT = (
    "bestvideo[height<=480][vcodec^=avc1]+bestaudio/best[height<=480]"
)

ENV_MPV_PATH = "KHAD_MPV_PATH"
ENV_YTDLP_PATH = "KHAD_YTDLP_PATH"
ENV_RENDER_PROFILE = "KHAD_MPV_PROFILE"
ENV_RENDER_MODE = "KHAD_RENDER_MODE"  # auto | embedded | external


@dataclass(frozen=True)
class MpvProfile:
    """Platform-aware mpv CLI options (excluding executable and IPC)."""

    name: str
    options: Sequence[str] = field(default_factory=tuple)


COMMON_MPV_OPTIONS: Sequence[str] = (
    "--idle=yes",
    "--fullscreen=no",
    "--autofit=800x450",
    "--keepaspect=yes",
    "--video-align-x=0",
    "--video-align-y=0",
    "--video-zoom=0",
    "--force-window=no",
    "--prefetch-playlist",
    "--ytdl-raw-options=yes-playlist=",
    f"--ytdl-format={YTDL_FORMAT}",
    "--no-terminal",
)

PROFILES: dict[str, MpvProfile] = {
    "linux-wayland": MpvProfile(
        name="linux-wayland",
        options=(
            "--vo=gpu",
            "--gpu-api=opengl",
            "--gpu-context=wayland",
            "--hwdec=vaapi",
        ),
    ),
    "linux-x11": MpvProfile(
        name="linux-x11",
        options=(
            "--vo=gpu",
            "--gpu-api=opengl",
            "--gpu-context=x11egl",
            "--hwdec=auto-safe",
        ),
    ),
    "linux-standard": MpvProfile(
        name="linux-standard",
        options=(
            "--vo=gpu",
            "--hwdec=auto-safe",
        ),
    ),
    "macos-standard": MpvProfile(
        name="macos-standard",
        # External-window baseline; libmpv render API is Phase F (embedded).
        options=(
            "--vo=gpu",
            "--hwdec=auto-safe",
        ),
    ),
    "low-resource": MpvProfile(
        name="low-resource",
        options=(
            "--vo=gpu",
            "--hwdec=no",
            "--profile=fast",
        ),
    ),
}


def detect_session_type() -> str:
    """Return a coarse session hint for Linux display servers."""
    session = (
        os.environ.get("XDG_SESSION_TYPE")
        or os.environ.get("WAYLAND_DISPLAY")
        or ""
    ).lower()
    if "wayland" in session or os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"
    if os.environ.get("DISPLAY"):
        return "x11"
    return "unknown"


def default_profile_name() -> str:
    override = os.environ.get(ENV_RENDER_PROFILE, "").strip()
    if override:
        return override
    if sys.platform == "darwin":
        return "macos-standard"
    if sys.platform.startswith("linux"):
        session = detect_session_type()
        if session == "wayland":
            return "linux-wayland"
        if session == "x11":
            return "linux-x11"
        return "linux-standard"
    return "low-resource"


def resolve_mpv_profile(name: str | None = None) -> MpvProfile:
    profile_name = name or default_profile_name()
    if profile_name not in PROFILES:
        profile_name = default_profile_name()
        if profile_name not in PROFILES:
            profile_name = "low-resource"
    return PROFILES[profile_name]


def mpv_startup_args(ipc_socket: str, profile: MpvProfile | None = None) -> list[str]:
    """Build mpv arguments excluding the executable path."""
    selected = profile or resolve_mpv_profile()
    args = list(COMMON_MPV_OPTIONS)
    args.extend(selected.options)
    args.append(f"--input-ipc-server={ipc_socket}")
    return args
