#!/usr/bin/env python3
"""Verify OS, Python, GTK, mpv and yt-dlp availability."""

from __future__ import annotations

import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print(f"Python: {sys.version.split()[0]}")

    errors: list[str] = []

    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk  # noqa: F401

        print("GTK 3 / PyGObject: OK")
    except Exception as error:  # noqa: BLE001
        errors.append(f"GTK 3 / PyGObject: {error}")
        print(f"GTK 3 / PyGObject: FAIL ({error})")

    from khad_media_player.dependencies import check_dependencies

    status = check_dependencies()
    for name in ("mpv", "yt-dlp"):
        path = status.get(name)
        if path:
            print(f"{name}: {path}")
        else:
            message = status.get(f"{name}_error", "not found")
            errors.append(f"{name}: {message}")
            print(f"{name}: FAIL ({message})")

    from khad_media_player.player.embedded_backend import embedded_prerequisites

    embed_ok, embed_reason = embedded_prerequisites()
    if embed_ok:
        print("Embedded libmpv (optional): OK")
    else:
        print(f"Embedded libmpv (optional): unavailable ({embed_reason})")
        print("  Install with: pip install 'khad-media-player[embed]' and system libmpv")
        print("  Fallback: external mpv window (KHAD_RENDER_MODE=external)")

    if errors:
        print("\nActionable next steps:")
        print("- Linux: install python3-gi, gir1.2-gtk-3.0, mpv, yt-dlp via your package manager")
        print("- macOS: brew install pygobject3 gtk+3 mpv yt-dlp")
        print("- Or set KHAD_MPV_PATH / KHAD_YTDLP_PATH to explicit executables")
        return 1

    print("\nAll required dependencies look available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
