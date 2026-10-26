#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Khad Media Player — Linux install from source"
echo "This script does not use sudo pip and does not change system configuration silently."

if command -v apt-get >/dev/null 2>&1; then
  echo "Debian/Ubuntu detected. Recommended packages:"
  echo "  sudo apt-get install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 mpv yt-dlp"
fi

python3 "$ROOT/scripts/check_dependencies.py"

python3 -m pip install --user -e "$ROOT"
echo
echo "Installed console command: khad-media-player"
echo "Desktop launcher: packaging/linux/io.khad.MediaPlayer.desktop"
echo "Copy it to ~/.local/share/applications/ if desired."
