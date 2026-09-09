---
name: git-workflow
description: "Git branching strategies, Conventional Commits, hooks, code review, and release/monorepo CI. Use when designing branch strategy, enforcing commit conventions, wiring Husky/commitlint, automating releases (semantic-release/release-please), setting up CODEOWNERS/monorepo CI, or deciding rebase vs cherry-pick vs force-push."
---

# Git Workflow

Workflow core below; deep configuration lives in `references/` and loads only when needed.

| Need | Reference |
|---|---|
| Husky v9 / lint-staged / commitlint wiring, PR template | [references/hooks.md](references/hooks.md) |
| semantic-release / release-please, tag signing | [references/release-automation.md](references/release-automation.md) |
| Nx/Turborepo affected builds, CODEOWNERS, CI matrix | [references/monorepo-ci.md](references/monorepo-ci.md) |
| `.gitignore` baselines per language | [references/gitignore.md](references/gitignore.md) |

## Branching Strategies

| Strategy | Best For | Branch Lifetime | Release Cadence |
|---|---|---|---|
| **Trunk-Based** | CI/CD, small teams | Hours | Continuous |
| **GitHub Flow** | SaaS, web apps | Days | On merge |
| **GitFlow** | Versioned software, mobile | Weeks | Scheduled |

Pick by release cadence and how long work must stay isolated — not by habit. If a
repository already documents a model, follow it; do not swap it silently.

- **Trunk-Based** — commit to `main` (or merge within ~24h); use **feature flags** for
  incomplete work, not long-lived branches; CI green on every commit to `main`.
- **GitHub Flow** — `git checkout -b feat/x` → push → `gh pr create --base main --fill` →
  review → squash-merge → deploy.
- **GitFlow** — `main` = tagged releases only; `develop` = integration; `feature/*` →
  `develop`, `release/*` → `main`+`develop`, `hotfix/*` → `main`+`develop`.

For agent experiment/spike branch lifecycle (`exp/*`, accept/reject/continue, worktree
per writer), use the `git-branch-experiment-management` skill.

## Commit Conventions (Conventional Commits)

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

| Type | SemVer Bump | Example |
|---|---|---|
| `fix` | PATCH | `fix(auth): handle expired refresh tokens` |
| `feat` | MINOR | `feat(api): add pagination to /users` |
| `feat!` or `BREAKING CHANGE:` | MAJOR | `feat(api)!: remove v1 endpoints` |
| `chore`, `docs`, `ci`, `refactor`, `test`, `perf` | none | `ci: add Node 24 to matrix` |

If the repository already has a commit convention, changelog format, or release
tooling that reads commit messages, follow it. Introduce Conventional Commits where
nothing is established, or when the user asks to change the convention — then enforce it
mechanically with **commitlint**, see [references/hooks.md](references/hooks.md).

## Code Review Checklist

- [ ] PR is < 400 lines (split if larger)
- [ ] Tests cover new behavior and edge cases
- [ ] No secrets, credentials, or PII in diff
- [ ] Breaking changes documented and flagged
- [ ] Error handling is explicit (no swallowed errors)
- [ ] No `TODO` without a linked issue
- [ ] DB migrations are reversible
- [ ] API changes are backward-compatible (or versioned)

For large or high-risk diffs (broad refactors, security/persistence/compat boundaries),
use the `large-change-review` skill — it adds a risk-tiered diff walkthrough on top of
this checklist.

## Rebase vs Merge

| Use | When |
|---|---|
| **Squash merge** | Feature branches → main (clean history) |
| **Rebase** | Updating feature branch with latest main |
| **Merge commit** | Release branches, preserving full history |

```bash
git fetch origin && git rebase origin/main   # update feature branch (never rebase shared branches)
git rebase -i HEAD~5                          # clean up before PR
```

## Cherry-Pick: Forward-port vs Backport

Fix the bug **once** on the branch where the code currently lives, then move the commit
with `cherry-pick -x` (records "cherry picked from <sha>").

- **Backport** (`main → release/*`): fix on `main`, `git switch release/2.3`,
  `git cherry-pick -x <sha>`, **re-test on the destination** (surrounding code differs),
  push, tag a patch release from there.
- **Forward-port** (`release/* → main`): a hotfix made under pressure on a release branch;
  cherry-pick it to `main` so the next version keeps it.

Rules of thumb: pick a **single source of truth** per fix and cherry-pick *from* it;
`--continue` / `--abort` on conflict, never resolve blind; contiguous span is
`git cherry-pick <oldSha>^..<newSha>`.

## Safety Rules (history, force-push, signing)

These operations lose other people's work or corrupt shared history.

- **Never rewrite shared history.** `rebase`, `commit --amend`, `reset --hard`,
  `push --force` are fine on *your own un-pushed branch* only.
- **Force-push your own branch with `--force-with-lease`**, never `--force` — it refuses
  if the remote moved since your last fetch:
  `git push --force-with-lease origin feat/my-branch`
- **Protect long-lived branches** (`main`, `develop`, `release/*`) with host branch
  protection: require PR + passing checks + Code Owner review; disallow force-push and
  deletion; require signed commits if your org mandates provenance.
- **Sign commits and tags.** SSH signing is the low-friction option:
  ```bash
  git config --global gpg.format ssh
  git config --global user.signingkey ~/.ssh/id_ed25519.pub
  git config --global commit.gpgsign true
  git config --global tag.gpgsign true
  ```
  Add the same public key as a *Signing key* in your GitHub account for the "Verified"
  badge. (GPG works too — set `gpg.format` back to `openpgp`.)
- **Recover from a bad rewrite with `git reflog`** (~90 day retention): find the good SHA,
  `git reset --hard <sha>`.
- **Delete branches safely.** `git branch -d` refuses unmerged work; `-D` forces it.
  Remote copy: `git push origin --delete <branch>`.

## Quick Reference

```bash
git reset --soft HEAD~1                 # undo last commit, keep changes
git bisect start && git bisect bad && git bisect good v2.0.0   # find the bad commit
git commit --amend --no-edit            # amend without changing message
git stash push -m "wip: auth refactor"  # named stash

# Clean up merged branches (anchored regex avoids matching e.g. "maintenance")
git branch --merged main | grep -vE '^[*+ ]*(main|master|develop)$' | xargs -r git branch -d
```
