# Development

```bash
python3 -m pip install --user -e ".[dev]"
make compile
make test
```

## Layout

- `src/khad_media_player/` — application package
- `legacy/app.py` — immutable behavioural baseline
- `tests/unit` — no GTK/mpv required (except optional integration)
- `tests/integration` — skips when mpv absent

## Extraction rule

Prefer relocating legacy logic over rewriting. Preserve five-tab UX.
