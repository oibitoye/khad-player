# Development

Full contribution workflow: [CONTRIBUTING.md](../CONTRIBUTING.md).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

System GTK/mpv/yt-dlp: see [INSTALL_LINUX.md](INSTALL_LINUX.md) / [INSTALL_MACOS.md](INSTALL_MACOS.md).

## Common commands

```bash
python -m compileall -q src
python -m ruff check src tests
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m build
make test
```

## Layout

- `src/khad_media_player/` — application package
- `legacy/app.py` — immutable behavioural baseline
- `tests/unit` — no GTK/mpv required
- `tests/integration` — skips when mpv absent
- `.github/` — CI, templates, CODEOWNERS, Dependabot

## Extraction rule

Prefer relocating legacy logic over rewriting. Preserve five-tab UX.
