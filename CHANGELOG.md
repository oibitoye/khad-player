# Changelog

## Unreleased

## 0.1.0a2 — 2026-10-26 (tag: v0.1.0-alpha.2)

Preview packaging cut including Debian `.deb` builder and experimental Flatpak (host-mpv). Still not production-ready.

### Added since 0.1.0a1

- `scripts/build_deb.sh` + CI `.deb` artifact
- Experimental Flatpak host-mpv bridge (`packaging/flatpak/`)

## 0.1.0a1 — 2026-10-26 (tag: v0.1.0-alpha.1)

First public **preview** packaging cut. Not production-ready.

### Added

- Contribution pipeline: issue/PR templates, CODEOWNERS, Dependabot, hardened CI/release workflows, CODE_OF_CONDUCT, SECURITY policy, branch-protection and release docs
- Modular `khad_media_player` package extracted from the Yoga Media Player prototype
- Cross-platform paths (XDG on Linux; Application Support / Caches on macOS)
- Executable discovery for `mpv` and `yt-dlp` (`KHAD_MPV_PATH`, `KHAD_YTDLP_PATH`)
- Platform-aware mpv renderer profiles (Wayland/X11/macOS/low-resource)
- Unit and optional mpv integration tests
- Linux desktop launcher and install scripts
- Documentation set under `docs/`
- Embedded playback via libmpv Render API + `Gtk.GLArea`, with automatic fallback to external mpv (`KHAD_RENDER_MODE`)
- Optional extra: `pip install '.[embed]'` (python-mpv)
- Wheel install verification script and release checksum generation
- Debian `.deb` builder (`scripts/build_deb.sh`) and CI artifact
- Experimental Flatpak (host-mpv bridge): `packaging/flatpak/`, `scripts/build_flatpak.sh`
- [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md) for alpha consumers

### Changed

- Application identity: **Khad Media Player** (`io.khad.MediaPlayer`)
- History and title cache stored under Khad data directories (one-time import from Yoga data when present)
- Now Playing shows an in-window video surface when embedded mode is active
- Package version set to `0.1.0a1` for the alpha preview tag

### Notes

- External mpv window remains the safe fallback and behavioural baseline
- Embedded mode is preferred when prerequisites succeed; per-platform support is **NOT TESTED** until runtime evidence exists
- Yoga tablet video-freeze issue remains unresolved; do not stress-test unstable video on Yoga without approval
- No licence file yet; no macOS `.app`; no PyPI/Homebrew publish in this alpha
