# Flatpak packaging (experimental)

## What this Flatpak does

- Runs the Khad Media Player GTK UI inside `org.gnome.Platform//47`
- Installs `yt-dlp` into the sandbox
- Forces **external** render mode
- Runs **host** `mpv` through `flatpak-spawn` (`/app/bin/mpv-host`)

## Requirements

- `flatpak` + `flatpak-builder`
- GNOME Platform/SDK 47 from Flathub
- **Host** `mpv` installed and on `PATH`

```bash
sudo apt-get install -y flatpak flatpak-builder
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install -y flathub org.gnome.Sdk//47 org.gnome.Platform//47
./scripts/build_flatpak.sh
flatpak install --user dist/io.khad.MediaPlayer.flatpak
flatpak run io.khad.MediaPlayer
```

## Limitations

- Embedded libmpv is **not** supported in this Flatpak
- Not Flathub-ready until an OSI licence is confirmed
- Host mpv bridge needs Flatpak portal / `flatpak-spawn` permissions
- First full Flatpak build can take several minutes (SDK download)

## Next steps (later)

- Bundle mpv/libmpv inside the runtime for embedded playback
- Add proper AppStream screenshots
- Replace `LicenseRef-proprietary` after founder licence decision
