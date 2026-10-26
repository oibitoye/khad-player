## Summary

<!-- What changed and why -->

## Linked issue

<!-- Closes #123 — or "N/A" for trivial docs -->

## Type of change

- [ ] Bug fix
- [ ] Feature / enhancement (behaviour-preserving)
- [ ] Refactor (no intentional behaviour change)
- [ ] Tests
- [ ] Documentation
- [ ] CI / tooling

## Affected platforms

- [ ] Linux
- [ ] macOS Intel
- [ ] macOS Apple Silicon
- [ ] Docs / CI only (no runtime change)

## Testing performed

<!-- For documentation-only PRs, "docs reviewed" is enough -->

- [ ] `python -m compileall -q src`
- [ ] `python -m ruff check src tests`
- [ ] `python -m pytest tests/unit -q`
- [ ] `python -m pytest tests/integration -q` (skipped OK if mpv unavailable)
- [ ] Manual UI smoke of affected tabs (if UI/runtime changed)
- [ ] Updated `docs/COMPATIBILITY.md` with runtime evidence (if claiming platform support)

## Screenshots

<!-- Required for relevant UI changes; otherwise write N/A -->

## Risks

<!-- Compatibility, security, packaging or playback risks. "None" is fine when accurate. -->

## Confirmations

- [ ] No personal playlists, history caches, credentials, private media or secrets are included
- [ ] Existing accepted functionality is preserved unless this PR documents a defect/security/portability fix
- [ ] I did not use `pull_request_target` secrets or publish package registries from this change
