# Release process

Semantic versioning starts at **0.1.0** (`pyproject.toml` and `src/khad_media_player/__init__.py`).

## Release candidate checklist

Before tagging:

- [ ] CI on `main` is green
- [ ] `python -m build` succeeds locally
- [ ] `CHANGELOG.md` updated for the release
- [ ] Version strings match in `pyproject.toml` and `__init__.py`
- [ ] Maintainer approval
- [ ] `docs/COMPATIBILITY.md` reflects honest platform evidence (no unverified claims)

## Creating a release

1. Merge the release prep PR to `main` (squash preferred).
2. Tag annotated release:

```bash
git checkout main
git pull
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

3. The **Release** workflow validates, builds artifacts and creates a GitHub Release for `v*` tags.
4. Manual alternative: Actions → Release → Run workflow.

## What is not automated

- Publishing to **PyPI**, **Homebrew** or other registries (requires explicit founder approval)
- Claiming new platform support without runtime evidence
- Releases from ordinary pull requests

## Preferred merge strategy

Use **squash merge** into `main` so history stays linear and Conventional Commit summaries remain readable.
