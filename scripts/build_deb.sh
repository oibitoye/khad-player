#!/usr/bin/env bash
# Build a simple architecture-independent .deb for Debian/Ubuntu testing.
# Depends on system GTK/mpv/yt-dlp (not bundled).
#
# Layout is intentional for *any* Debian/Ubuntu python3:
#   /usr/bin/khad-media-player          → #!/usr/bin/python3 wrapper
#   /usr/lib/python3/dist-packages/…    → pure-Python package (not
#                                         CI's pythonX.Y/site-packages)
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
WHEEL_EXTRACT="$(mktemp -d)"
OUT_DIR="${ROOT}/dist"
mkdir -p "$OUT_DIR"
cleanup() { rm -rf "$STAGE" "$WHEEL_EXTRACT"; }
trap cleanup EXIT

echo "Staging ${PY_VERSION} as Debian ${DEB_VERSION}..."
"$PYTHON" -m pip install -q --upgrade pip build
"$PYTHON" -m build --wheel >/dev/null

WHEEL="$(ls -1 "${OUT_DIR}"/khad_media_player-"${PY_VERSION}"-*.whl | head -1)"
if [[ -z "${WHEEL}" || ! -f "${WHEEL}" ]]; then
  echo "Wheel not found for ${PY_VERSION} under ${OUT_DIR}" >&2
  exit 1
fi

"$PYTHON" -m zipfile -e "${WHEEL}" "${WHEEL_EXTRACT}"
install -d "${STAGE}/usr/lib/python3/dist-packages"
# Copy package only (skip .dist-info for a minimal runtime tree; keep RECORD-free).
cp -a "${WHEEL_EXTRACT}/khad_media_player" "${STAGE}/usr/lib/python3/dist-packages/"
# Drop any bytecode that may have been baked for the builder's Python.
find "${STAGE}/usr/lib/python3/dist-packages/khad_media_player" \
  -type d -name '__pycache__' -prune -exec rm -rf {} +

install -d "${STAGE}/usr/bin"
cat >"${STAGE}/usr/bin/khad-media-player" <<'EOF'
#!/usr/bin/python3
"""System launcher for the Debian/Ubuntu package."""
from khad_media_player.application import run

raise SystemExit(run())
EOF
chmod 0755 "${STAGE}/usr/bin/khad-media-player"

# Fail the build if we accidentally bake a CI/host-specific shebang again.
SHEBANG="$(head -1 "${STAGE}/usr/bin/khad-media-player")"
if [[ "${SHEBANG}" != "#!/usr/bin/python3" ]]; then
  echo "Refusing non-portable shebang: ${SHEBANG}" >&2
  exit 1
fi
if [[ -d "${STAGE}/usr/lib/python3."* ]]; then
  echo "Refusing versioned site-packages layout under usr/lib:" >&2
  find "${STAGE}/usr/lib" -maxdepth 2 -type d >&2
  exit 1
fi
test -f "${STAGE}/usr/lib/python3/dist-packages/khad_media_player/application.py"

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
echo "Launcher shebang: $(dpkg-deb --fsys-tarfile "$DEB_PATH" | tar -xO ./usr/bin/khad-media-player | head -1)"
