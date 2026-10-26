# Contributing

Thanks for helping improve Khad Media Player.

## Development setup

1. Install system dependencies (GTK 3, PyGObject, mpv, yt-dlp)
2. `python3 -m pip install --user -e ".[dev]"`
3. `make test`

## Guidelines

- Preserve existing user-facing behaviour unless fixing a defect or portability issue
- Prefer extracting and adapting legacy logic over rewriting features
- Do not commit personal playlists, history, credentials, or media files
- Do not push private engineering packet files (`plan.md`, `writing-block.md`, supplements)
- Document platform test evidence honestly in `docs/COMPATIBILITY.md`

## Pull requests

Use the PR template. Include what changed, why, and how you tested.
