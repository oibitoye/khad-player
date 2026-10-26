#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Khad Media Player — macOS install from source"
ARCH="$(uname -m)"
echo "Architecture: $ARCH"

if command -v brew >/dev/null 2>&1; then
  echo "Homebrew detected. Recommended packages:"
  echo "  brew install python pygobject3 gtk+3 mpv yt-dlp"
else
  echo "Homebrew not found. Install from https://brew.sh then install pygobject3 gtk+3 mpv yt-dlp"
fi

# Prefer Homebrew Python for GI typelib compatibility when available.
PYTHON="python3"
if [[ -x /opt/homebrew/bin/python3 ]]; then
  PYTHON=/opt/homebrew/bin/python3
elif [[ -x /usr/local/bin/python3 ]]; then
  PYTHON=/usr/local/bin/python3
fi

"$PYTHON" "$ROOT/scripts/check_dependencies.py"

if [[ ! -d "$ROOT/.venv" ]]; then
  "$PYTHON" -m venv "$ROOT/.venv"
fi
# shellcheck disable=SC1091
source "$ROOT/.venv/bin/activate"
python -m pip install -U pip
python -m pip install -e "$ROOT"

echo
echo "Installed into $ROOT/.venv"
echo "Run: source .venv/bin/activate && khad-media-player"
echo "Or: $ROOT/.venv/bin/python -m khad_media_player"
echo "A distributable .app bundle is not included in this release."
