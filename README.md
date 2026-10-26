# Khad Media Player

Cross-platform desktop media player built with **Python 3**, **GTK 3**, and **mpv**.

Khad Media Player is a modular refactor of the Yoga Media Player prototype. It preserves the accepted five-tab workflow while improving portability, packaging, and testability.

## Features

- **Now Playing** — URL playback, pause/resume, previous/next, seek ±10s / ±30s
- **Search** — YouTube search via `yt-dlp`
- **Queue** — mpv playlist mirror with play/remove/clear
- **Open** — local files, URLs, and IPTV M3U channel browsing
- **History** — recent media with replay and queue actions

Playback prefers **embedded** libmpv Render API video in the main window when `python-mpv`/libmpv are available (`pip install '.[embed]'`), and falls back to an **external** mpv window otherwise. Override with `KHAD_RENDER_MODE=external|embedded|auto` (see `docs/CONFIGURATION.md`).

## Platform status

| Platform | Status |
|---|---|
| Linux (Debian 12 reference) | Source-compatible; verify with `scripts/check_dependencies.py` |
| Linux ARM64 | Source-compatible; runtime **NOT TESTED** in this workspace |
| Intel macOS | Source install documented; runtime **NOT TESTED** here |
| Apple Silicon macOS | Source install documented; runtime **NOT TESTED** here |
| Distributable `.app` | Not included in v0.1.0 |

## Requirements

- Python 3.10+
- GTK 3 + PyGObject
- mpv
- yt-dlp

These native tools are **not** installed by `pip`.

## Quick start

```bash
# Check dependencies
python3 scripts/check_dependencies.py

# Install (editable)
python3 -m pip install --user -e .

# Run
khad-media-player
# or
python3 -m khad_media_player
```

See `docs/INSTALL_LINUX.md` and `docs/INSTALL_MACOS.md`.

## Architecture

Application logic lives under `src/khad_media_player/`. The original prototype is preserved at `legacy/app.py`.

```text
UI tabs → application → playback / search / queue / history / playlist services → mpv IPC
```

## Licence

Licence file pending founder confirmation. Third-party notices: `NOTICE.md`.

## Contributing

See `CONTRIBUTING.md` and `docs/DEVELOPMENT.md`.
