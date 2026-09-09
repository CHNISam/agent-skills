# agent-skills

A personal library of [Agent Skills](https://github.com/agentskills/agentskills) for AI
coding agents (Claude Code, Codex CLI, OpenCode, Cursor), plus a thin **harness spine**
that routes between them.

- **Start here:** [`HARNESS.md`](HARNESS.md) — the four layers (Capability, Context,
  Verification, Change isolation & review), the cheap→expensive ladders, and the skill
  tier table (`core` / `on-demand` / `domain` / `deprecated`).
- **Each skill** is a directory with a `SKILL.md` (YAML frontmatter: `name`,
  `description`) and optional `references/`, `scripts/`, `assets/`. Content loads
  progressively — metadata first, the rest only when the skill is invoked.
- **Licensing:** skills come from several upstreams under different licenses. Each skill's
  own `LICENSE.txt` / `NOTICE` governs; see [`NOTICE`](NOTICE). First-party skills are MIT.

## Using it in another repository

Run the `init-repository-governance` skill against the target repo. It inspects the
actual stack and configures only what applies — thin `AGENTS.md`, search exclusions,
relevant skills, MCP recommendations, Git/branch strategy, testing + review wiring — and
never installs everything.

## Syncing

Source of truth for authored skills is `~/.agents/skills/`. This repo is the backup:
`github` = `CHNISam/agent-skills`, `origin` = Aliyun codeup. Push with the
`sync-global-skills` skill.
