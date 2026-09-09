# Reusable repository governance

Select only rules supported by repository evidence and the user's intent.

## Scope and ownership

- Identify the repository, package/service, and files that own the requested capability.
- Preserve uncommitted work and keep client/server/infrastructure/data boundaries intact.
- Put shared invariants at root and specialized commands next to the subtree they govern.
- Record external Sources of Truth instead of copying their changing backlog or status.

## Intent and uncertainty

- Normalize natural language internally to Goal, Constraints, and Done when.
- Discover versions, commands, branch model, components, and existing behavior from the
  repository before asking.
- Ask when remaining ambiguity changes product behavior, architecture, compatibility,
  security/data boundaries, correctness criteria, or irreversible actions.
- Follow existing conventions for small reversible decisions; do not interview the user
  about spacing, naming, or configuration the repository already settles.

## Implementation and verification

- Express changed behavior as observable contracts or invariants.
- Use fast deterministic tests for logic, real-boundary contract/integration tests where
  needed, and a few high-value runtime/E2E flows.
- For a bug: reproduce, add regression protection where practical, fix the proven cause,
  and prove the symptom gone.
- A green suite is useful only if it would fail on broken required behavior. Reject empty
  assertions, implementation-copy oracles, mock-only proof, hidden skips, and flaky-by-design
  timing.
- Confirm before changing business expectations. Report exact commands/results and gaps.

## Git and collaboration

- Follow the repository's established branch model and the installed `git-workflow`.
- Separate genuinely concurrent writers by worktree/branch and record ownership.
- Inspect exact targets before destructive or irreversible operations; preserve history
  unless explicitly authorized.
- Keep release, tag, staging, and production gates project-specific and evidence-based.

## Risk boundaries

Authentication, authorization, privacy, credentials, destructive migrations, production
data, persistence formats, concurrency/lifecycle, public APIs, and released compatibility
need explicit contracts and proportionate verification. Prefer mechanical enforcement to
an instruction that merely says “be careful.”

## UI/game/runtime evidence

When presentation matters, validate the real route/scene, viewport/platform, input flow,
and visible states. Automated state checks do not prove pixels or animation; screenshots
do not prove underlying logic. Use both where the contract crosses both layers.

## Feedback improvement

After an escaped failure, ask why existing protection missed it. Keep a one-off correction
in the task, a product-specific guard in the project, and only a repeated/generalizable
mechanism in the shared harness. Prefer regression test → deterministic check → CI →
project rule → Skill → global prose.
