# Compatibility matrix

| Platform | Source-compatible | Deps install | GUI launch | Functional smoke | Media playback | Embedded libmpv | Packaged app |
|---|---|---|---|---|---|---|---|
| Debian 12 x86_64 | Yes | Documented | **NOT TESTED** | **NOT TESTED** | **NOT TESTED** | **NOT TESTED** | N/A (desktop file only) |
| Linux ARM64 | Yes | Documented | **NOT TESTED** | **NOT TESTED** | **NOT TESTED** | **NOT TESTED** | N/A |
| Intel macOS | Yes | Documented | **NOT TESTED** | **NOT TESTED** | **NOT TESTED** | **NOT TESTED** | Not shipped |
| Apple Silicon macOS | Yes | Documented | **NOT TESTED** | **NOT TESTED** | **NOT TESTED** | **NOT TESTED** | Not shipped |

Embedded support must not be claimed for a platform until runtime testing demonstrates stable Render API drawing. External mode remains the verified behavioural baseline.

### CI coverage note

- Linux GitHub Actions: compile, lint, unit tests, mpv integration (when apt mpv installs), package build
- macOS GitHub Actions (`macos-latest`, typically Apple Silicon): compile, lint, unit tests, package build — **not** native GTK/mpv GUI verification
- Intel macOS: no dedicated free GitHub-hosted runner in this pipeline; treat as **NOT TESTED** until manual evidence exists

Update this table only with runtime evidence.
