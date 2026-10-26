# Contribution pipeline implementation report (KMP-CONTRIB-001)

## Summary

Established a lightweight, secure contribution pipeline for https://github.com/oibitoye/khad-player without modifying application playback logic.

## What changed

| Area | Action |
|---|---|
| Issue templates | Replaced thin markdown with YAML bug / feature / documentation forms; added `config.yml` security contact link |
| PR template | Expanded for summary, issue link, type, platforms, testing, screenshots, risks, privacy/behaviour confirmations |
| Ownership | Added `.github/CODEOWNERS` → `@oibitoye` |
| Docs | Expanded `CONTRIBUTING.md`; added `CODE_OF_CONDUCT.md`, root `SECURITY.md`, `docs/RELEASE.md`, `docs/BRANCH_PROTECTION.md` |
| CI | Restricted `permissions: contents: read`; `pull_request` (not `pull_request_target`); Linux matrix with compile/ruff/unit/integration(+mpv)/build; macOS non-GUI job; no `\|\| true` |
| Dependabot | Weekly grouped updates for Actions + pip |
| Release | Tag/`workflow_dispatch` validation + artifact build; GitHub Release on `v*` tags; **no** PyPI/Homebrew publish |
| Hygiene | `.gitignore` already excludes personal data and private engineering packets |

## Manual GitHub activation required

Documented in `docs/BRANCH_PROTECTION.md`:

- Ruleset on `main` (PR required, CI required, no force-push, no deletion, conversation resolution)
- Squash-merge preference
- Sole-maintainer guidance for approval requirements
- Secret scanning / private vulnerability reporting / dependency review toggles

## Security posture

- Contributor CI cannot access write secrets for publishing
- Release write permission limited to the tag-based GitHub Release job
- Security issues directed to private advisories (issue template contact link + `SECURITY.md`)
- Dependabot does not auto-merge

## Validation performed (local)

Commands to re-run:

```bash
python -m compileall -q src
python -m ruff check src tests
python -m pytest tests/unit tests/integration -q
python -m build
```

CI YAML uses stable action majors (`checkout@v4`, `setup-python@v5`, `upload-artifact@v4`, `action-gh-release@v2`).

## Not done in this packet (by design)

- No playback / UI architecture changes
- No licence invention
- No automatic registry publishing
- No claim of GTK GUI verification from macOS CI
- Branch ruleset not applied via API (manual activation)

## Completion criteria status

| Criterion | Status |
|---|---|
| Structured issue templates | Done |
| PR-based contribution path | Done |
| Automated validation on PRs | Done (workflow); enforce via ruleset |
| Maintainer review path / CODEOWNERS | Done |
| Main protection | Instructions ready — **activate manually** |
| Controlled versioned releases | Done |
| Private security reporting route | Done |
| No speculative app refactor | Observed |
