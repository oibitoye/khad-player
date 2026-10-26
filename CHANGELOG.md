# Changelog

## Unreleased

### Added

- Modular `khad_media_player` package extracted from the Yoga Media Player prototype
- Cross-platform paths (XDG on Linux; Application Support / Caches on macOS)
- Executable discovery for `mpv` and `yt-dlp` (`KHAD_MPV_PATH`, `KHAD_YTDLP_PATH`)
- Platform-aware mpv renderer profiles (Wayland/X11/macOS/low-resource)
- Unit and optional mpv integration tests
- Linux desktop launcher and install scripts
- Documentation set under `docs/`
- **Phase F:** embedded playback via libmpv Render API + `Gtk.GLArea`, with automatic fallback to external mpv (`KHAD_RENDER_MODE`)
- Optional extra: `pip install '.[embed]'` (python-mpv)

### Changed

- Application identity: **Khad Media Player** (`io.khad.MediaPlayer`)
- History and title cache stored under Khad data directories (one-time import from Yoga data when present)
- Now Playing shows an in-window video surface when embedded mode is active

### Notes

- External mpv window remains the safe fallback and behavioural baseline
- Embedded mode is preferred when prerequisites succeed; per-platform support is **NOT TESTED** until runtime evidence exists
- Yoga tablet video-freeze issue remains unresolved; do not stress-test unstable video on Yoga without approval
