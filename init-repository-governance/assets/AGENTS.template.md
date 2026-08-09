# AGENTS.md

This file applies to this repository and all subdirectories unless a closer `AGENTS.md` or `AGENTS.override.md` provides more specific guidance.

## Repository context

- Purpose: `<one-sentence repository purpose>`
- Primary areas: `<packages/services/apps and ownership boundaries>`
- Out of scope: `<adjacent systems or responsibilities that belong elsewhere>`

Before editing, confirm the repository root, working directory, current branch, Git remote, and which package or service owns the requested change. Preserve unrelated and uncommitted user changes.

## Setup and commands

- Install: `<verified command or “see …”>`
- Develop: `<verified command>`
- Format/lint: `<verified command>`
- Type-check/build: `<verified command>`
- Focused tests: `<verified command and selection syntax>`
- Full verification: `<verified command>`

Use commands documented by manifests, task runners, CI, or repository documentation. Do not invent commands or silently switch package managers.

## Implementation workflow

1. Read applicable instructions, relevant source, tests, configuration, and architecture decisions.
2. Confirm expected behavior and scope. Investigate repository evidence before asking discoverable questions.
3. For behavior changes and bug fixes, add or update focused tests before or with the implementation.
4. Make the smallest coherent change and preserve established architecture and public contracts.
5. Run focused checks, then broader verification in proportion to risk.
6. Review the diff and report changed files, checks run, omissions, and remaining risks.

Do not weaken, skip, or delete tests merely to make a run pass. Ask before changing business expectations, acceptance criteria, compatibility, migrations, authentication, authorization, privacy, credential handling, or irreversible infrastructure.

## Git and release safety

- Completely read and follow the installed `git-workflow` skill before any Git-policy decision or Git mutation.
- Every concurrent agent or session that may write must use its own Git worktree and branch, even when planned files do not overlap. Read-only work may share a worktree.
- Before concurrent work starts, record each writer's absolute worktree path, branch, and file/resource ownership. Integrate only reviewed commits from isolated branches.
- If another writer already occupies the current worktree or unexplained concurrent changes appear, stop writing and preserve the state until ownership is confirmed; do not format, stage, commit, or deploy overlapping work.
- Unless established repository policy says otherwise, use controlled GitFlow: `feature/*` → `develop`, validated `release/*` → `main`, and `hotfix/*` → both `main` and `develop`.
- Keep `main` releasable; do not develop, commit, or push directly on it.
- Use Conventional Commits: `<type>[scope]: <description>`.
- Inspect branch, status, tracking relationship, remote, and exact targets before Git mutations.
- Do not rewrite history, overwrite files, delete branches/tags, or discard changes without explicit authorization.
- Keep `<production branch>` releasable. Follow `<release/staging/approval documentation>` for deployments and releases.
- Verify Git, push, tag, release, and deployment claims with fresh output.

## Project-specific invariants

- `<critical architecture or ownership invariant>`
- `<data/security invariant>`
- `<compatibility or API invariant>`

## UI and prototypes

<!-- Remove this section for non-UI repositories. -->

- Treat approved prototypes and screenshots as implementation baselines unless redesign is explicitly authorized.
- Map each supplied page/state to its route or component and validate at matching viewport sizes.
- Preserve the established visual language and report unavailable assets, fonts, or platform limitations.

## Nested guidance

- `<path>/AGENTS.md`: `<scope and reason>`

Create nested guidance only when a subtree needs genuinely different commands or rules. Keep mechanical formatting checks in tooling or CI and keep this file concise.

## Tool and browser reuse

- Reuse installed tools and browser connectors before proposing downloads. A missing default executable path is not proof that the application is absent.
- Obtain explicit authorization before downloading browsers, drivers, or large runtime dependencies.
- For local UI evidence, verify the exact URL, port ownership, page title, and a distinctive page marker before saving screenshots.
