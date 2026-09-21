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
- Use `large-change-review` when semantic impact warrants a whole-change review, such as
  a broad cross-cutting or materially high-risk change. Do not require a separate review
  artifact unless this repository has an explicit audit/handoff need; fresh verification
  is still required.
- Explicit dissatisfaction, escaped regressions, and repeated failures use
  `preventing-repeat-failures`: prefer test/check/CI, then a project rule, and promote to a
  shared Skill only when genuinely cross-project.

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
