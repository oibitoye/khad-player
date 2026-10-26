#!/usr/bin/env bash
# Smoke-check the Debian/Ubuntu from-source install path (dependencies + import).
# Does not claim GUI/playback verification.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== Dependency probe =="
python3 "$ROOT/scripts/check_dependencies.py" || {
  echo "NOTE: missing system deps are expected on some CI images; install via docs/INSTALL_LINUX.md" >&2
}

echo "== Editable install into temp venv =="
TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

python3 -m venv "$TMP/venv"
# shellcheck disable=SC1091
source "$TMP/venv/bin/activate"
python -m pip install -U pip
python -m pip install -e "$ROOT"

python -c "import khad_media_player; print(khad_media_player.__version__)"
command -v khad-media-player
echo "Linux install-path smoke check passed (import + console script)."
echo "GUI launch and playback remain manual — see docs/COMPATIBILITY.md"
