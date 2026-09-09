# agent-skills

A personal, versioned library of [Agent Skills](https://github.com/agentskills/agentskills)
for Codex, Claude Code, Cursor, and OpenCode, with a small test-first harness core.

- Read [`HARNESS.md`](HARNESS.md) for the operating contract and skill tiers.
- `harness-profile.json` defines the portable `core`, `authoring`, and `all` profiles.
- `scripts/distribute_skills.py` safely refreshes supported local agents from this Git
  worktree; dry-run is the default and unrelated skills are preserved.
- `scripts/validate_harness.py` plus `tests/` enforce the repository's own invariants in CI.

## Install or refresh the core

```bash
python scripts/distribute_skills.py --profile core --target all
python scripts/distribute_skills.py --profile core --target all --apply --adopt-existing
```

After first adoption, pull this repository and run:

```bash
python scripts/distribute_skills.py --profile core --target all --apply --prune
```

The Git worktree is the source of truth. Do not edit generated copies under
`~/.agents/skills`, `~/.codex/skills`, `~/.claude/skills`, `~/.cursor/skills`, or
`~/.config/opencode/skills` and expect them to flow back automatically.

## Adopt in a project

Use `init-repository-governance`. It inspects the real stack and creates thin project
adapters (`AGENTS.md`, `CLAUDE.md`, scoped Cursor rules only when useful), records the
canonical verification command, and points detailed reusable behavior back to installed
skills. It does not copy the whole skill library into the project.

## Verify changes

```bash
python scripts/validate_harness.py
python -m unittest discover -s tests -p "test_*.py" -v
```

Licenses vary by skill. Each skill's `LICENSE.txt` or `NOTICE` governs; see [`NOTICE`](NOTICE).
