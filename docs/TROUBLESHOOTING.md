# Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| GTK import fails | Missing PyGObject/GTK | Install system GI packages / Homebrew gtk+3 |
| Player not ready | mpv missing or IPC failed | `scripts/check_dependencies.py`; check `KHAD_MPV_PATH` |
| No search results | yt-dlp missing/outdated | Install/update yt-dlp; set `KHAD_YTDLP_PATH` |
| Queue empty after Play Now | Unexpected — report as bug | Queue-preserving play should keep other items |
| macOS library conflicts | Wrong Python arch | Use native Homebrew Python |
| Wayland video issues | GPU/hwdec | Try `KHAD_MPV_PROFILE=low-resource` |
| Yoga tablet freeze | Known unresolved | Do not claim fixed; avoid automated video tests on Yoga |

IPC is local-only. Never expose the mpv socket remotely.
