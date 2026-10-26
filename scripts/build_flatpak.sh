#!/usr/bin/env bash
# Build the experimental Flatpak (requires flatpak-builder + GNOME 47 SDK).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v flatpak-builder >/dev/null; then
  echo "flatpak-builder is required." >&2
  echo "Debian/Ubuntu: sudo apt-get install -y flatpak flatpak-builder" >&2
  echo "Then: flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo" >&2
  echo "      flatpak install -y flathub org.gnome.Sdk//47 org.gnome.Platform//47" >&2
  exit 1
fi

OUT_DIR="${ROOT}/dist"
BUILD_DIR="${ROOT}/build/flatpak"
REPO_DIR="${ROOT}/build/flatpak-repo"
mkdir -p "$OUT_DIR" "$BUILD_DIR" "$REPO_DIR"

MANIFEST="${ROOT}/packaging/flatpak/io.khad.MediaPlayer.yaml"

echo "Building Flatpak from ${MANIFEST}..."
flatpak-builder --force-clean --repo="${REPO_DIR}" "${BUILD_DIR}" "${MANIFEST}"

BUNDLE="${OUT_DIR}/io.khad.MediaPlayer.flatpak"
rm -f "$BUNDLE"
flatpak build-bundle "${REPO_DIR}" "$BUNDLE" io.khad.MediaPlayer
echo "Built ${BUNDLE}"
echo "Install with: flatpak install --user ${BUNDLE}"
echo "Note: host mpv must be installed; embedded libmpv is not supported in this bundle."
