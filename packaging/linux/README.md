# Linux packaging

## Debian / Ubuntu `.deb` (alpha)

Build on Debian/Ubuntu:

```bash
sudo apt-get install -y python3-pip python3-venv dpkg-dev
./scripts/build_deb.sh
# → dist/khad-media-player_0.1.0~a5-1_all.deb
```

Install:

```bash
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 mpv yt-dlp
sudo apt-get install -y ./dist/khad-media-player_*.deb
khad-media-player
```

The launcher is `#!/usr/bin/python3` and the package lives under
`/usr/lib/python3/dist-packages` so it works on Bookworm/Ubuntu regardless of
which Python minor version built the `.deb` in CI.

The `.deb` depends on system GTK / mpv / yt-dlp (not bundled).

Uninstall:

```bash
sudo apt-get remove khad-media-player
```

**Do not upload to Debian/Ubuntu archives** until a licence is confirmed (`packaging/debian/copyright`).

## Flatpak (experimental)

See [../flatpak/README.md](../flatpak/README.md).

## From-source (fallback)

See [docs/INSTALL_LINUX.md](../../docs/INSTALL_LINUX.md) and `./scripts/install_linux.sh`.

Desktop entry: [io.khad.MediaPlayer.desktop](io.khad.MediaPlayer.desktop).
