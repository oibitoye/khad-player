# Install on macOS

Supports **Intel** and **Apple Silicon** from source. A portable `.app` is not provided in v0.1.0.

## Homebrew dependencies

```bash
brew install python pygobject3 gtk+3 mpv yt-dlp
```

Use architecture-native Homebrew (`/opt/homebrew` on Apple Silicon, `/usr/local` on Intel). Avoid mixing Intel-only Python with ARM64 libraries.

## Install

```bash
chmod +x scripts/install_macos.sh
./scripts/install_macos.sh
khad-media-player
```

## Troubleshooting

- If `import gi` fails, ensure you are using Homebrew Python, not Xcode's
- Set `KHAD_MPV_PATH` / `KHAD_YTDLP_PATH` when binaries are outside PATH
- Wayland/VAAPI mpv flags are **not** used on macOS

## Application bundle

See `packaging/macos/README.md`. Signing and notarisation are separate founder decisions.
