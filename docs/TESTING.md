# Testing

```bash
python3 -m pytest tests/unit -q
python3 -m pytest tests/integration -q   # skips without mpv
```

## Coverage focus

- Playlist parsing including ≥11,356 synthetic entries
- History atomic writes / corrupt recovery
- Executable discovery and profile selection
- Queue-preserving Play Now logic
- Optional live mpv IPC ready/shutdown

## Manual UI smoke

1. Launch app; confirm five tabs
2. Play a local file or known URL
3. Search (requires network + yt-dlp)
4. Queue add/remove/clear
5. Open M3U browser filter
6. History replay/delete

Do not run automatic full-screen video stress tests on the Yoga tablet.
