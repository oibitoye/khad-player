#!/usr/bin/env bash
# Build a simple architecture-independent .deb for Debian/Ubuntu testing.
# Depends on system GTK/mpv/yt-dlp (not bundled).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v dpkg-deb >/dev/null; then
  echo "dpkg-deb is required (Debian/Ubuntu packaging tools)." >&2
  exit 1
fi

PYTHON="${PYTHON:-python3}"
eval "$("$PYTHON" - <<'PY'
import re
import tomllib
from pathlib import Path

version = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
upstream = version
upstream = re.sub(r"(\d)a(\d+)", r"\1~a\2", upstream)
upstream = re.sub(r"(\d)b(\d+)", r"\1~b\2", upstream)
upstream = re.sub(r"(\d)rc(\d+)", r"\1~rc\2", upstream)
print(f"PY_VERSION={version!r}")
print(f"DEB_UPSTREAM={upstream!r}")
print(f"DEB_VERSION={upstream + '-1'!r}")
PY
)"

ARCH="all"
STAGE="$(mktemp -d)"
OUT_DIR="${ROOT}/dist"
mkdir -p "$OUT_DIR"
cleanup() { rm -rf "$STAGE"; }
trap cleanup EXIT

echo "Staging ${PY_VERSION} as Debian ${DEB_VERSION}..."
"$PYTHON" -m pip install -q --upgrade pip build
"$PYTHON" -m build >/dev/null
"$PYTHON" -m pip install --root "$STAGE" --prefix=/usr "${ROOT}"

install -d "$STAGE/usr/share/applications"
install -m 0644 "$ROOT/packaging/linux/io.khad.MediaPlayer.desktop" \
  "$STAGE/usr/share/applications/io.khad.MediaPlayer.desktop"

install -d "$STAGE/usr/share/doc/khad-media-player"
install -m 0644 "$ROOT/NOTICE.md" "$STAGE/usr/share/doc/khad-media-player/NOTICE.md"
install -m 0644 "$ROOT/packaging/debian/copyright" "$STAGE/usr/share/doc/khad-media-player/copyright"
install -m 0644 "$ROOT/README.md" "$STAGE/usr/share/doc/khad-media-player/README.md"
gzip -9n -c "$ROOT/CHANGELOG.md" >"$STAGE/usr/share/doc/khad-media-player/changelog.gz"

install -d "$STAGE/DEBIAN"
sed "s/@DEB_VERSION@/${DEB_VERSION}/g" "$ROOT/packaging/debian/control.in" >"$STAGE/DEBIAN/control"
SIZE="$(du -sk "$STAGE" | awk '{print $1}')"
echo "Installed-Size: ${SIZE}" >>"$STAGE/DEBIAN/control"

DEB_PATH="${OUT_DIR}/khad-media-player_${DEB_VERSION}_${ARCH}.deb"
rm -f "$DEB_PATH"
dpkg-deb --root-owner-group --build "$STAGE" "$DEB_PATH"
echo "Built ${DEB_PATH}"
dpkg-deb --info "$DEB_PATH" | sed -n '1,25p'
