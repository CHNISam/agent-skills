---
name: init-repository-governance
description: Inspect a software repository and create or improve concise, evidence-based agent guidance plus mechanical verification wiring. Use for repository /init, AGENTS.md or CLAUDE.md adoption, new-project harness setup, or auditing project instructions for stale, duplicated, missing, or unenforced rules.
---

# Initialize Repository Governance

Build a thin adapter from the shared harness to the repository's real commands and
invariants. Do not install a framework or copy the global harness into every project.

## Inspect first

1. Read every applicable `AGENTS.md`, override/fallback instruction file, and `CLAUDE.md`
   or scoped editor rule that may contain accurate project knowledge.
2. Inspect repository status/worktrees, manifests, README/contribution docs, CI, test and
   build configuration, release docs, generated/vendor boundaries, and architecture
   decisions. Preserve unrelated changes.
3. Run `scripts/inventory_repository.py --root <repo-root>` when available. Treat detected
   commands as candidates and confirm them against manifests/CI.
4. Read [references/reusable-governance.md](references/reusable-governance.md) and select
   only rules that apply.

## Create the minimum effective adapter

- Root `AGENTS.md`: repository identity/ownership, verified commands, critical invariants,
  Git/release safety, protected paths, and completion criteria.
- Nested `AGENTS.md`: only for a subtree with genuinely different ownership or commands.
- `CLAUDE.md`: thin pointer to `AGENTS.md` plus any Claude-only adapter; no duplicated policy.
- Cursor/editor rules: scoped only when the editor needs behavior not already available
  from `AGENTS.md` or installed Skills.

Start from [assets/AGENTS.template.md](assets/AGENTS.template.md) for a new file. Remove
placeholders and irrelevant sections. Merge accurate existing project rules rather than
overwriting them wholesale.

## Wire the harness

1. **Plain-language task contract:** tell agents to infer Goal, Constraints, and Done when
   internally. Repository discovery answers repository facts. Material product or risk
   ambiguity uses `ask-questions-if-underspecified`; minor reversible choices follow
   project conventions.
2. **Retrieval:** route to `context-retrieval` and add stack-specific search exclusions.
3. **Verification:** record one canonical repository command. If none exists, add an
   honest `verify.config` for `automated-testing-workflow/scripts/verify.*`; never invent
   a command. A normal behavior change must not be marked done without relevant fresh
   evidence.
4. **Test quality:** encode critical observable contracts and previously escaped bugs.
   Prefer tests/checks/CI over prose. Do not rely on coverage percentage alone.
5. **Review:** route broad/high-risk diffs to `large-change-review` and its one
   `review-pack.md`; independent review is optional unless repository policy requires it.
6. **Self-improvement:** route rejected outcomes and repeated failures to
   `harness-self-improvement`, keeping project-specific protections in the project.
7. **Source of truth:** state what the repository owns and what external product/roadmap
   system owns, without duplicating live backlog state.

Reference only installed Skills. Domain Skills are available on demand, never mandatory
merely because the repository uses that language or engine.

## Git and authority

Read the installed `git-workflow` before Git-policy decisions or mutations. Follow the
repository's established branch model; ask before replacing it. Give genuinely concurrent
writers separate worktrees/branches. Initialization does not authorize pushes, releases,
dependency installation, production writes, destructive cleanup, or global configuration
changes.

## Validate

Run `scripts/validate_agents.py <path-to-AGENTS.md>`, the repository's focused instruction
checks, and its canonical verification when executable content changed. Report preserved
rules, changed files, verified commands, mechanical gates added, unresolved choices, and
what was not run.
