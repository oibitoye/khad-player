# Linux packaging (alpha)

## Supported path for v0.1.0-alpha.1

Debian/Ubuntu **from source** (or editable install), not a self-contained `.deb`:

1. Install system packages — [docs/INSTALL_LINUX.md](../../docs/INSTALL_LINUX.md)
2. `./scripts/install_linux.sh` or `python -m pip install` the published wheel/sdist
3. Desktop entry: [io.khad.MediaPlayer.desktop](io.khad.MediaPlayer.desktop)
4. Smoke check: `./scripts/verify_linux_install_path.sh`

## Not in this alpha

- Official `.deb` / Flatpak / AppImage
- Bundled GTK/mpv inside the Python package

## Uninstall

```bash
python -m pip uninstall khad-media-player
# remove ~/.local/share/applications/io.khad.MediaPlayer.desktop if you copied it
```

User data under `~/.local/share/khad-media-player/` is left in place unless deleted manually.
