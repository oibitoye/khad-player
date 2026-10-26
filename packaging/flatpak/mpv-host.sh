#!/bin/sh
# Spawn the host system's mpv from inside the Flatpak sandbox.
# Requires host mpv and finish-arg --talk-name=org.freedesktop.Flatpak.
set -e
if ! command -v flatpak-spawn >/dev/null 2>&1; then
  echo "flatpak-spawn not available; install Flatpak portal support." >&2
  exit 127
fi
exec flatpak-spawn --host mpv "$@"
