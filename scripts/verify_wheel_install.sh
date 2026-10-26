#!/usr/bin/env bash
# Validate that a built wheel installs and imports cleanly (no GTK GUI required).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d dist ]]; then
  echo "dist/ missing — run: python -m build" >&2
  exit 1
fi

WHEEL="$(ls -1 dist/khad_media_player-*.whl 2>/dev/null | tail -1 || true)"
if [[ -z "${WHEEL}" ]]; then
  echo "No khad_media_player wheel found in dist/" >&2
  exit 1
fi

TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

python3 -m venv "$TMP/venv"
# shellcheck disable=SC1091
source "$TMP/venv/bin/activate"
python -m pip install -U pip
python -m pip install "$WHEEL"

python - <<'PY'
import khad_media_player
from importlib.metadata import version, entry_points

assert khad_media_player.__version__
print("import OK:", khad_media_player.__version__)
print("package version:", version("khad-media-player"))
eps = entry_points()
scripts = eps.select(group="console_scripts") if hasattr(eps, "select") else eps.get("console_scripts", [])
names = {ep.name for ep in scripts}
assert "khad-media-player" in names, names
print("console script OK: khad-media-player")
PY

echo "Wheel install verification passed: ${WHEEL}"
