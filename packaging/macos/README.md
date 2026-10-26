# macOS packaging (alpha)

## v0.1.0-alpha.1

**No `.app` bundle is published** for this preview.

Supported path: install from source / wheel after Homebrew dependencies — see [docs/INSTALL_MACOS.md](../../docs/INSTALL_MACOS.md).

## Before publishing `.app` assets

Required for each architecture (Intel and Apple Silicon), separately:

1. Native GUI launch verified
2. Playback smoke verified (external and/or embedded)
3. Document how GTK / PyGObject typelibs / libmpv are bundled or required alongside the app
4. Signing / notarisation decision by the founder
5. Update [docs/COMPATIBILITY.md](../../docs/COMPATIBILITY.md) with runtime evidence

Until then, do not attach `.app` files to GitHub Releases.
