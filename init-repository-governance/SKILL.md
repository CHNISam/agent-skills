---
name: init-repository-governance
description: Inspect a software repository and create or improve concise, evidence-based agent guidance plus mechanical verification wiring. Use for repository /init, AGENTS.md or CLAUDE.md adoption, helping a project set up its own agent harness, or auditing project instructions for stale, duplicated, missing, or unenforced rules.
---

# Initialize Repository Governance

Help a repository write **its own** agent guidance from its own real stack, commands, and
invariants. The project owns the result; this skill is only the tool that produces it.

Do not install a framework, do not copy the skill library into the project, and do not
transplant the rules of the repository this skill ships from. Nothing here is a doctrine
the project must adopt — every rule that survives must be traceable to evidence in the
target repository or to an explicit decision by its owner.

For a sense of what a good, fully project-owned result looks like, read a mature real
repository's own file — for example [`openai/codex`'s `AGENTS.md`][codex-agents], which is
almost entirely specific to that codebase: its crate naming, its `just` commands, its
snapshot-test and API-versioning rules. Borrow the *shape* and specificity; do not copy its
content.

[codex-agents]: https://github.com/openai/codex/blob/main/AGENTS.md

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

## Wire the project's own gates

Each item below is a candidate. Keep it only when the repository has, or is choosing to
add, a real mechanism behind it; drop it rather than writing an unenforced rule.

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
6. **Self-improvement:** when an outcome is rejected or a failure repeats, prefer the
   smallest durable fix that would have caught it — a regression test, then a deterministic
   check, then a project rule — before adding prose; keep the protection in the project
   unless the failure is proven to repeat across projects.
7. **Source of truth:** state what the repository owns and what external product/roadmap
   system owns, without duplicating live backlog state.

Reference only installed Skills, and only where a pointer beats restating the rule.
Domain Skills are available on demand, never mandatory merely because the repository uses
that language or engine. If a skill is absent on a contributor's machine, the project's own
file must still stand on its own.

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
