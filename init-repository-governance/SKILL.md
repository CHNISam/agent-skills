---
name: init-repository-governance
description: Inspect a new or existing software repository and create, migrate, or improve concise AGENTS.md guidance tailored to its actual stack, commands, ownership boundaries, Git workflow, testing, safety, clarification, design, and release practices. Use when initializing a repository for Codex, running or extending `/init`, converting reusable CLAUDE.md rules to AGENTS.md, standardizing agent instructions across repositories, or auditing repository guidance for missing or overly project-specific rules.
---

# Initialize Repository Governance

Create evidence-based repository instructions. Treat Codex `/init` as an optional starter, then replace generic output with rules grounded in the repository.

## Workflow

1. Read every applicable `AGENTS.md`, `AGENTS.override.md`, and configured fallback instruction file before changing anything. Also inspect `CLAUDE.md` when present as a migration source, not as automatically active Codex guidance.
2. Before designing Git policy or performing any branch, commit, push, pull, merge, rebase, PR, tag, release, CI/CD, or Git-hook operation, completely read and follow the installed `git-workflow` skill. If it is unavailable, stop before Git mutations and record that the required workflow could not be loaded.
3. Before allowing concurrent agents or sessions to write in a Git repository, assign every writer its own Git worktree and branch, and record each worktree path, branch, and ownership boundary. Read-only agents may share a worktree. If another writer already occupies the current worktree or unexplained concurrent changes appear, stop writing and preserve the worktree until ownership is confirmed.
4. Run `python <skill-dir>/scripts/inventory_repository.py --root <repo-root>` to collect a read-only inventory. If Python is unavailable, inspect the same facts manually.
5. Read the detected manifests, primary README, contribution guide, CI configuration, test configuration, release documentation, and existing instruction files. Prefer repository evidence over assumptions.
6. Read [references/reusable-governance.md](references/reusable-governance.md). Select only rules relevant to this repository.
7. Decide the instruction layout:
   - Put repository-wide commands, invariants, safety rules, and completion criteria in the root `AGENTS.md`.
   - Put service-, package-, or language-specific rules in the closest nested `AGENTS.md`.
   - Use `AGENTS.override.md` only for an intentional temporary replacement.
   - Keep detailed policies in checked-in docs and link them from `AGENTS.md`.
8. Start from [assets/AGENTS.template.md](assets/AGENTS.template.md) when creating a file. When updating a file, preserve accurate project-specific rules and merge deliberately instead of overwriting it wholesale.
9. Remove every placeholder and irrelevant section. Replace example commands with commands verified from manifests, task runners, CI, or documentation.
10. Use controlled GitFlow as the user's preferred default only when the repository has no contrary documented branch model: `feature/*` to `develop`, `release/*` from `develop` to `main`, and `hotfix/*` from `main` back to both long-lived branches. Keep `main` releasable and prohibit direct development there. Ask before changing an established model or repairing a repository whose current branches contradict the policy.
11. Ask before selecting any other policy that repository evidence cannot establish and that materially affects contributors, including production release gates, accepted business behavior, security boundaries, migrations, or new tooling. Continue independent read-only discovery while awaiting the answer.
12. Validate with `python <skill-dir>/scripts/validate_agents.py <path-to-AGENTS.md>`. Resolve errors; treat warnings as prompts for human judgment.
13. Report created or updated files, preserved local rules, verified commands, unresolved choices, and validation performed.

## Required Judgments

- Never copy repository names, absolute paths, deployment vendors, feature flags, reference projects, or product boundaries from the source template unless they apply to the target repository.
- Never mandate a named skill, tool, package manager, branch model, hosting platform, or test command unless it is installed, available, or explicitly chosen.
- Do not silently replace controlled GitFlow with trunk-based development merely because a repository is small or has one contributor.
- Prefer concise operational rules over philosophy. Keep the combined instruction chain comfortably below Codex's configured project-document byte limit; use nested files and linked docs when necessary.
- Encode repeatable human judgment in `AGENTS.md`; enforce mechanical formatting and static checks with linters, hooks, or CI instead of prose alone.
- Preserve uncommitted user changes. Do not use repository initialization as permission to commit, push, install dependencies, modify global configuration, or alter production systems.
- In Git repositories, never let multiple writing agents or sessions share one worktree, even when their planned file sets do not overlap. Require a dedicated worktree and branch per writer; integrate only reviewed commits. When shared-worktree interference is discovered, stop all further writes, formatting, staging, commits, and deployments from that worktree until ownership is resolved.
- Before downloading a browser, browser driver, Playwright runtime, or similar large tool, check existing system browsers, non-default/portable install paths, and available IDE browser connectors. A missing executable at one default path is inconclusive. Prefer an existing browser and obtain explicit user authorization before any download or installation.
- Before accepting local UI evidence, verify the exact URL, port owner, and page title or a distinctive DOM marker. An HTTP 200 response alone does not prove the intended application is serving the port.

## Codex Integration

- `/init` can generate an initial `AGENTS.md` in the current directory. Use this skill to tailor or audit that scaffold.
- Codex loads global guidance first, then one applicable instruction file per directory from repository root to the working directory. Closer files take precedence.
- Codex reads `AGENTS.md` natively. Migrate useful `CLAUDE.md` content explicitly or configure a fallback filename; do not assume `CLAUDE.md` is discovered by default.
