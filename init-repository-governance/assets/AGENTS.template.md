# AGENTS.md

This file applies to the repository and descendants unless a closer instruction file
provides more specific guidance.

## Repository contract

- Purpose: `<one sentence>`
- Owned areas: `<packages/services/apps>`
- External source-of-truth boundary: `<what this repository must not duplicate>`

Before editing, confirm repository root, current branch/worktree, remote, and the component
that owns the requested change. Preserve unrelated and uncommitted work.

## Verified commands

- Setup: `<verified command or documentation link>`
- Focused check: `<verified command and selection syntax>`
- Canonical verification: `<one command>`
- Runtime/visual evidence: `<when and how, or not applicable>`

Use commands proven by manifests, task runners, CI, or repository docs. Do not invent or
silently replace them.

## Working contract

- Infer Goal, Constraints, and Done when from ordinary user language. Inspect repository
  evidence before asking questions. Ask only when unresolved ambiguity materially changes
  product behavior, scope, architecture, compatibility, risk, or an irreversible action.
- Follow `context-retrieval` for least-cost code discovery.
- Use `automated-testing-workflow` for risk-proportionate verification. Test observable
  requirements; a passing test must be capable of failing when required behavior breaks.
- Bug fixes add regression protection where practical. Do not delete, skip, or weaken tests
  to get green; confirm before changing a business expectation.
- Broad/high-risk changes use `large-change-review` and one `review-pack.md`. Independent
  review is optional unless project policy says otherwise; fresh verification is required.
- Explicit dissatisfaction, escaped regressions, and repeated failures get the smallest
  durable fix that would have caught them — a regression test, then a deterministic check,
  then a project rule — before adding prose; promote to a shared Skill only when the
  failure is proven to repeat across projects.

## Project invariants

- `<critical architecture/ownership invariant>`
- `<data/security/compatibility invariant>`
- Protected/generated paths: `<paths and required mechanism>`

## Git and release safety

- Follow the installed `git-workflow` plus this repository's established branch model.
- Concurrent writers use separate worktrees and branches; read-only work may share.
- Do not rewrite history, discard changes, delete branches/tags, deploy, or modify
  production without the required explicit authority.
- Branch model: `<verified repository model>`
- Release/deployment gate: `<verified policy or documentation>`

## Completion

Report changed behavior/files, exact verification and runtime evidence, failures/skips,
what was not run, and residual risk. Do not claim a test, push, merge, release, deployment,
or visual result without fresh evidence.
