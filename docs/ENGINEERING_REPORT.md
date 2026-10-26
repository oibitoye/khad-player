# Engineering report — KMP-REF-001 v0.1.0 preparation

## Summary

The Yoga Media Player monolith (`src/app.py`, ~1021 lines) was preserved and extracted into the modular package `src/khad_media_player/` without a greenfield rewrite. External mpv + JSON IPC remains the fallback baseline. **Phase F** adds preferred embedded playback via the libmpv Render API into `Gtk.GLArea`, with automatic fallback when prerequisites fail.

## Baseline

| Item | Value |
|---|---|
| Legacy file | `legacy/app.py` |
| SHA-256 | `639c66f237da57af30a6f17782c8765d2ca31bfa58f2ab6b5c124475eaae0d40` |
| Original | `src/app.py` retained unchanged |

## Architecture delivered

- Config / paths / dependency discovery / platform adapters
- `player/` — process, IPC (request IDs), `PlaybackService` with `RenderMode`
- `services/` — history, title cache, YouTube search, playlist parser, queue
- `ui/` — five tabs matching legacy UX
- Packaging: `pyproject.toml`, Linux `.desktop`, install scripts, CI

## Preserved features

Now Playing, Search, Queue, Open (M3U browser), History, queue-preserving Play Now, seek controls, title cache, external mpv window.

## Defects / portability fixes

- Removed hard-coded `/usr/bin/mpv`, `~/.local/bin/yt-dlp`, `/run/user/...` socket assumption for non-Linux
- Platform mpv profiles (Wayland/VAAPI no longer unconditional)
- History delete write uses correct newline (legacy had escaped `\\n` bug in one path)
- PLS advertised support removed from Open status text until implemented
- Planning docs excluded from git (`.gitignore`)

## Tests

```bash
python3 -m pytest tests/unit tests/integration -q
```

Large synthetic playlist (≥11,356 entries) covered in unit tests. Live mpv IPC test skips when mpv is absent.

## Platform table

See `docs/COMPATIBILITY.md` — runtime verification **NOT TESTED** in the build workspace; do not claim full cross-platform readiness without evidence.

## Known issues / follow-ups

- Embedded libmpv: implemented; **runtime verification NOT TESTED** per platform (see `docs/COMPATIBILITY.md`)
- OpenGL Render API + GTK3 GLArea may need platform-specific tuning (Wayland/X11/macOS)
- `.app` bundle after dual-arch macOS smoke tests
- Yoga video freeze unresolved — do not run unstable embed tests on Yoga without approval
- Licence file awaiting founder choice
- GitHub visibility / signing decisions awaiting founder approval

## Recommended first release

**v0.1.0** once Linux modular regression (unit + manual smoke) passes on a real Linux host.

## Awaiting founder approval

- Open-source licence
- Public GitHub publication
- Signing/notarisation for future macOS bundles
- Unstable video testing on Yoga hardware
