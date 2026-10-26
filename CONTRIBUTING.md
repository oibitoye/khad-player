# Contributing to Khad Media Player

Thanks for contributing.

**Lifecycle:** Issue → Fork/Branch → Pull Request → Automated Validation → Maintainer Review → Merge → Release

## Before you start

1. Search existing issues and pull requests.
2. For bugs/features/docs, open an issue using the templates (except security — see below).
3. Read:
   - [README.md](README.md)
   - [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
   - [docs/TESTING.md](docs/TESTING.md)
   - [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)
   - [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
   - [SECURITY.md](SECURITY.md)

**Do not invent or change the project licence.** Licence decisions are made by the founder.

## Security vulnerabilities

Report privately via [GitHub Security Advisories](https://github.com/oibitoye/khad-player/security/advisories/new).  
Do not disclose exploitable issues in public issues or pull requests.

## Development environment

Install system dependencies using the platform guides (do not duplicate those steps here):

- Linux: [docs/INSTALL_LINUX.md](docs/INSTALL_LINUX.md)
- macOS: [docs/INSTALL_MACOS.md](docs/INSTALL_MACOS.md)

Then from a clone:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
# optional embedded playback:
# python -m pip install -e ".[dev,embed]"
```

Quick checks:

```bash
python -m compileall -q src
python -m ruff check src tests
python -m pytest tests/unit -q
python -m pytest tests/integration -q   # skips if mpv is unavailable
python -m build                         # package build verification
make test                               # convenience wrapper
```

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) and [docs/TESTING.md](docs/TESTING.md).

## Fork, clone and branch

1. Fork https://github.com/oibitoye/khad-player
2. Clone your fork and add the upstream remote
3. Create a branch from an up-to-date `main` (see workflow below)

| Prefix | Use |
|---|---|
| `feat/` | Behaviour-preserving enhancement |
| `fix/` | Bug fix |
| `docs/` | Documentation only |
| `refactor/` | Internal restructuring without intentional behaviour change |
| `test/` | Tests only |
| `ci/` | CI / tooling |

Examples: `feat/improve-playlist-filter`, `fix/history-atomic-write`, `docs/install-macos`.  
Never create a literal placeholder branch such as `feat/your-feature-name`.

Prefer [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, …). Clear messages matter more than perfect formatting.

### Maintainer / local CLI workflow

For each new piece of work, start with a clean working tree and an up-to-date `main`:

```bash
git status
git switch main
git pull --ff-only origin main
git switch -c feat/short-description
```

Do the work, test locally, then commit and push the branch:

```bash
git add .
git commit -m "feat: describe the change"
git push -u origin HEAD
```

Create a pull request against `main`:

```bash
gh pr create --base main --fill
```

CI runs on the PR when workflows are configured for `pull_request`. Prefer **manual** squash-merge after checks and human review (do not auto-merge on green CI while the testing baseline is still maturing):

```bash
gh pr merge --squash --delete-branch
```

Synchronise the local machine:

```bash
git switch main
git pull --ff-only origin main
```

The same flow works in the GitHub web UI; the CLI is simply more convenient.

## Submitting a pull request

1. Push your branch (fork or origin, as appropriate).
2. Open a PR against `main` using the pull request template (`gh pr create --base main --fill` or the web UI).
3. Link the issue when applicable (`Closes #123`).
4. Ensure CI is green.
5. Keep the PR focused; do not mix unrelated refactors.

Preferred merge strategy on `main` is **squash merge** (configured by maintainers in GitHub settings).

### Review expectations

- Maintainers look for requirement fit, behaviour preservation, tests, docs honesty and security/privacy hygiene.
- Respond to review comments; resolve conversations when addressed.
- `@oibitoye` is listed in `.github/CODEOWNERS` for review requests. CODEOWNERS alone does not enforce approvals — repository rulesets do.

### Documentation-only changes

Trivial docs PRs do not need full UI smoke checklists. Mark unrelated template sections as N/A.

## GTK UI changes

- Preserve the accepted five-tab workflows and two-window/external fallback behaviour unless fixing a documented defect.
- Prefer extending existing UI modules under `src/khad_media_player/ui/`.
- Include screenshots for visible UI changes.
- Do not introduce a new GUI framework without maintainer approval.
- Manual smoke: launch, affected tabs, and confirm no personal data is committed.

## Platform compatibility reports

When you verify a platform, update [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md) with honest evidence:

- Source-compatible / deps installed / GUI launch / smoke / playback / embedded / packaged
- Mark unverified cells **NOT TESTED**
- Never claim native GTK runtime success from compile-only CI

## What not to commit

- Personal IPTV playlists, history, title caches, media, credentials, `.env`
- Private engineering packet files (`plan.md`, `writing-block.md`, supplements) — already gitignored
- Generated build artifacts and local virtualenvs

## Releases

Releases are maintainer-controlled. See [docs/RELEASE.md](docs/RELEASE.md).  
Do not publish to PyPI, Homebrew or other registries without founder approval.
