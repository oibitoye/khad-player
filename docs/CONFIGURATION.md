# Configuration

## Environment overrides

| Variable | Purpose |
|---|---|
| `KHAD_MPV_PATH` | Absolute path to `mpv` |
| `KHAD_YTDLP_PATH` | Absolute path to `yt-dlp` |
| `KHAD_MPV_PROFILE` | Renderer profile name |
| `KHAD_RENDER_MODE` | `auto` (default), `embedded`, or `external` |

### Render modes

- **`auto`** — try embedded libmpv Render API; fall back to external mpv window
- **`embedded`** — require in-window video (`pip install '.[embed]'` + system libmpv); fall back if init fails
- **`external`** — always use the separate mpv window (legacy baseline)

Embedded mode is preferred UX but only claimed per platform after runtime verification.

## Screen lock

While status is **Playing**, the app requests a session idle/suspend inhibit
(`Gtk.Application.inhibit`) so the display does not lock mid-video. Inhibit is
released on pause, stop, or quit. External mpv also uses `--stop-screensaver=yes`.

## Profiles

- `linux-wayland` — Yoga-compatible GPU/Wayland/VAAPI options
- `linux-x11`
- `linux-standard`
- `macos-standard`
- `low-resource`

## Data locations

**Linux (XDG):**

- `~/.local/share/khad-media-player/`
- `~/.config/khad-media-player/`
- `~/.cache/khad-media-player/`

**macOS:**

- `~/Library/Application Support/Khad Media Player/`
- `~/Library/Caches/Khad Media Player/`

IPC socket: private per-user runtime directory (not a world-writable path).

## Legacy import

On first run, if Khad history is missing, compatible Yoga history/titles may be copied once from `~/.local/share/yoga-media-player/` without modifying the Yoga files.
