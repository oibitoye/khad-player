# Release process

Package versions use [PEP 440](https://peps.python.org/pep-0440/).  
Git tags use a readable SemVer-style form.

| Git tag | Package version (`pyproject.toml`) |
|---|---|
| `v0.1.0-alpha.1` | `0.1.0a1` |
| `v0.1.0-rc.1` | `0.1.0rc1` |
| `v0.1.0` | `0.1.0` |

Current prep target: **`v0.1.0-alpha.1`** / **`0.1.0a1`**.

## Alpha.1 checklist (before tagging)

- [ ] CI on `main` is green (including `Linux integration (mpv)`)
- [ ] `python -m build` succeeds
- [ ] `./scripts/verify_wheel_install.sh` passes
- [ ] `./scripts/verify_linux_install_path.sh` reviewed on a Linux desktop (or noted as CI-limited)
- [ ] `CHANGELOG.md` has an `0.1.0a1` section
- [ ] Version strings match in `pyproject.toml` and `__init__.py`
- [ ] [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) reviewed
- [ ] [COMPATIBILITY.md](COMPATIBILITY.md) has no unverified claims marked as supported
- [ ] **Licence decision** recorded (or explicitly deferred — do not invent a licence file)
- [ ] Maintainer approval to publish the GitHub Release
- [ ] Optional: minimal real-device playback smoke on at least one Linux host

## Creating the alpha GitHub Release

Human-controlled. Do **not** auto-publish to PyPI/Homebrew.

```bash
git switch main
git pull --ff-only origin main
# confirm version is 0.1.0a1
git tag -a v0.1.0-alpha.1 -m "v0.1.0-alpha.1"
git push origin v0.1.0-alpha.1
```

The **Release** workflow will:

1. Validate (compile, lint, unit tests)
2. Build wheel + sdist
3. Write `SHA256SUMS`
4. Create a **prerelease** GitHub Release with artifacts

Attach or link:

- Installation: [INSTALL_LINUX.md](INSTALL_LINUX.md), [INSTALL_MACOS.md](INSTALL_MACOS.md)
- Limitations: [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)

## Outputs for alpha.1

| Asset | Include? |
|---|---|
| Wheel + sdist + SHA256SUMS | Yes |
| Linux from-source instructions | Yes |
| macOS `.app` | **No** until GUI/playback evidence |
| PyPI upload | **No** without founder approval |

## Preferred merge strategy

Squash-merge prep PRs into `main`, then tag from `main`.
