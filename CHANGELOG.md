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

### Changed

- Application identity: **Khad Media Player** (`io.khad.MediaPlayer`)
- History and title cache stored under Khad data directories (one-time import from Yoga data when present)

### Notes

- External mpv window remains the default playback mode
- Embedded libmpv rendering is deferred (Phase F)
- Yoga tablet video-freeze issue remains unresolved
