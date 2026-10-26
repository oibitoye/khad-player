# Configuration

## Environment overrides

| Variable | Purpose |
|---|---|
| `KHAD_MPV_PATH` | Absolute path to `mpv` |
| `KHAD_YTDLP_PATH` | Absolute path to `yt-dlp` |
| `KHAD_MPV_PROFILE` | Renderer profile name |

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
