# macOS packaging notes

Khad Media Player currently supports **install and run from source** on macOS.

A self-contained `.app` bundle is intentionally deferred until:

1. Intel macOS runtime smoke tests pass
2. Apple Silicon macOS runtime smoke tests pass
3. GTK / PyGObject / mpv bundling strategy is verified

See `docs/INSTALL_MACOS.md` for Homebrew-based setup.
