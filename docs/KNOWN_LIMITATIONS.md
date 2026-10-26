# Known limitations — v0.1.0-alpha.1

This preview is **not** a production-ready cross-platform release.

## Licensing

No open-source licence file is published yet. Distribution beyond the founder’s private use requires an explicit licence decision.

## Platforms

See [COMPATIBILITY.md](COMPATIBILITY.md). Unverified cells remain **NOT TESTED**.

- Linux GUI/playback: requires manual verification on a real desktop
- macOS Intel / Apple Silicon GUI and playback: **NOT TESTED** in CI
- macOS `.app` bundles: **not published** in this alpha

## Playback

- External mpv window is the behavioural baseline and fallback
- Embedded libmpv Render API is preferred when prerequisites succeed, but per-platform stability is unverified
- Yoga tablet video-freeze issue remains unresolved — do not stress-test unstable video on that device without approval

## Packaging

| Output | Alpha.1 status |
|---|---|
| Python wheel / sdist | Built and install-verified in CI |
| Linux Debian/Ubuntu from-source path | Documented; install-path smoke script provided |
| Linux `.deb` | Buildable via `./scripts/build_deb.sh` (system GTK/mpv deps); CI builds artifact; **not** archive-uploadable until licence is set |
| Flatpak | Experimental host-mpv bridge (`./scripts/build_flatpak.sh`); embedded libmpv unsupported; **not** Flathub-ready until licence is set |
| Linux AppImage | Not included |
| macOS `.app` / `.dmg` | Not included |
| PyPI / Homebrew publish | Not enabled |

## Dependencies

GTK 3, PyGObject, mpv and yt-dlp are **system** dependencies. Installing the wheel does not install them.

## Privacy

Do not ship personal playlists, history, caches or credentials with any release asset.
