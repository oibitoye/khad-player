# Architecture

## Overview

```mermaid
flowchart TB
  UI[ui tabs] --> App[application.py]
  App --> Playback[playback_service]
  Playback --> RenderMode{render mode}
  RenderMode -->|external default| MpvProc[mpv_process + mpv_ipc]
  RenderMode -->|embedded planned| Libmpv[libmpv Render API]
  App --> Search[youtube_search]
  App --> Queue[queue_service]
  App --> History[history_service]
  App --> Playlist[playlist_parser]
```

## Modules

| Area | Responsibility |
|---|---|
| `application.py` | Gtk.Application lifecycle |
| `config.py` | App ID, mpv profiles |
| `paths.py` | Data/config/cache/runtime locations |
| `dependencies.py` | `mpv` / `yt-dlp` discovery |
| `player/` | Process ownership, IPC, playback API |
| `services/` | Search, queue, history, playlist, title cache |
| `ui/` | Five GTK tabs |
| `platform/` | Linux / macOS adapters |

## Playback modes

- **External (default):** spawn mpv with `--input-ipc-server` and control via JSON IPC
- **Embedded (planned):** libmpv Render API widget; external remains fallback

UI code must call `PlaybackService`, not construct mpv CLI arguments.

## Legacy baseline

`legacy/app.py` is the behavioural source of truth for the refactor (SHA-256 recorded in `legacy/BASELINE.md`).
