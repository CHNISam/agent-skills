---
name: install-skills-global
description: Safely install or refresh repository-owned Agent Skills for Codex, Claude Code, Cursor, OpenCode, or the shared Agent Skills directory. Use when the user asks to install, copy, distribute, or synchronize skills across local coding agents.
---

# Install Skills Across Local Agents

Use the canonical `agent-skills` Git worktree as source. Installed agent directories are
generated copies, not authoring sources.

## Workflow

1. Locate the worktree containing `skill-profiles.json` and
   `scripts/distribute_skills.py`. Pull only with a safe fast-forward after checking the
   branch and working tree; preserve local changes.
2. Detect installed agents/config directories. Do not create targets the user did not
   request when detection is inconclusive.
3. Preview the exact plan:

   ```bash
   python scripts/distribute_skills.py --profile core --target all
   ```

4. On first adoption, inspect same-name existing directories. Use
   `--adopt-existing` only after confirming they are disposable copies or their changes
   are preserved in the source repository.
5. Apply and verify:

   ```bash
   python scripts/distribute_skills.py --profile core --target all --apply --adopt-existing
   ```

   Later refreshes normally use `--apply --prune`; pruning is restricted to directories
   recorded in `.skills-managed.json`.
6. Restart or reload agents that do not discover changed skills live.

Dry-run is the default. Do not replace an unmanaged collision by hand, copy with a broad
`cp -r`, delete an entire agent skill directory, or edit generated copies as source.

Use `core` for the lightweight default, `authoring` when maintaining skills, and `all`
only when the user deliberately wants the full library exposed to every agent.
