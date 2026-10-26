# Install on Linux

## Debian / Ubuntu (reference)

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 mpv yt-dlp
```

## From source

```bash
cd "/path/to/Khad Media Player"
chmod +x scripts/install_linux.sh
./scripts/install_linux.sh
khad-media-player
```

Or manually:

```bash
python3 scripts/check_dependencies.py
python3 -m pip install --user -e .
khad-media-player
```

## Desktop launcher

Copy `packaging/linux/io.khad.MediaPlayer.desktop` to `~/.local/share/applications/`.

## Notes

- Do not use `sudo pip install`
- Virtualenvs may not see system GTK typelibs; prefer the system Python with GI packages
- Override binaries with `KHAD_MPV_PATH` / `KHAD_YTDLP_PATH` if needed
