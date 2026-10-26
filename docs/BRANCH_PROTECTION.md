# Branch protection / rulesets for `main`

These settings must be activated manually in GitHub. They cannot be enforced by repository files alone.

Repository: https://github.com/oibitoye/khad-player

## Recommended ruleset (initial)

Path: **Settings → Rules → Rulesets → New ruleset → Branch ruleset**

Target: `main`

Enable:

1. **Restrict deletions** — block branch deletion
2. **Block force pushes**
3. **Require a pull request before merging**
   - Require conversation resolution before merging
   - Allowed merge methods: prefer **Squash** (also set under Settings → General → Pull Requests)
4. **Require status checks to pass**
   - Require branches to be up to date before merging (optional but recommended)
   - Required checks (after first green CI run, select by exact job name):
     - `Linux (Ubuntu) (3.11)` / matrix equivalents as shown in Actions
     - `Linux (Ubuntu) (3.12)`
     - `macOS (non-GUI)`
5. **Require a pull request review**
   - **If an independent reviewer is available:** require 1 approving review and optionally require CODEOWNERS review
   - **If the founder is the sole maintainer:** do **not** enable a mandatory approval that blocks self-maintained merges. Keep CODEOWNERS review *requests* enabled; avoid a deadlock.

Do **not** add exceptions that silently bypass required CI checks.

## CODEOWNERS note

`.github/CODEOWNERS` assigns `@oibitoye` for review requests.  
CODEOWNERS alone does **not** enforce approvals — enable “Require review from Code Owners” in the ruleset only when practical.

## Pull request settings (General)

Settings → General → Pull Requests:

- Allow squash merging (preferred)
- Optionally disable merge commits / rebase if you want squash-only
- Automatically delete head branches (optional)

## Security / supply chain settings

Settings → Code security and analysis (names vary by GitHub plan):

- Enable **Dependency graph**
- Enable **Dependabot alerts**
- Enable **Dependabot security updates** (optional; PRs still need CI)
- Enable **Secret scanning** where available
- Enable **Private vulnerability reporting**
- Enable **Dependency review** on private/public plans that support it

Dependabot config lives in `.github/dependabot.yml`. Do not auto-merge dependency PRs before CI passes.

## Verification

After enabling the ruleset:

1. Open a test PR with a trivial docs change
2. Confirm CI runs with `permissions: contents: read`
3. Confirm merge is blocked while checks are pending/failing
4. Confirm squash merge works for the maintainer
