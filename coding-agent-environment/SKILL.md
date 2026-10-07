---
name: coding-agent-environment
description: Maintain a consistent local coding-agent baseline across Codex, Claude Code, OpenCode, and Cursor, including supported Windows Claude Code multi-account isolation. Use for a new machine, agent-environment audits, Claude Code account-entry setup, or cross-agent capability drift; not for project dependencies or business features.
---

# Coding Agent Environment

Keep the baseline small and observable. Each installed agent should be able to:

1. access project files with native tools;
2. search code with `rg`/`fd` or an equivalent built-in index;
3. obtain diagnostics through LSP or the repository's CLI linters/type checkers;
4. query current official documentation when repository evidence is insufficient;
5. discover the same shared core skills.

Do not add a filesystem MCP when native file tools already cover the need. Add business
connectors such as GitHub, databases, chat, and cloud providers only for tasks that use
them. Do not build a custom code RAG, Tree-sitter service, LSP proxy, or sandbox when the
agent/editor already supplies the capability.

## Shared skills

The canonical source is the `agent-skills` Git worktree. Distribute its core profile with:

```bash
python scripts/distribute_skills.py --profile core --target all
python scripts/distribute_skills.py --profile core --target all --apply --adopt-existing
```

Subsequent updates use `--apply --prune`. The distributor manages only entries recorded
in each target's `.skills-managed.json` and preserves unrelated personal skills.

## Audit

Use `checklist.md` as a machine-oriented inventory, but verify every version/path against
the installed product rather than assuming a historical table is current. For each agent,
exercise file read, known-symbol search, a deliberate diagnostic, current-doc retrieval,
and discovery of one core skill. Record material environment changes in `update-log.md`.

Agent/editor support changes over time. Prefer current official documentation and an
actual smoke test over claims in this skill.

## Claude Code 多账号（Windows）

For terminal Claude Code accounts, use Anthropic's documented `CLAUDE_CONFIG_DIR`
mechanism rather than copying credentials or persisting API/OAuth tokens. Keep the
original `claude` entry untouched; create a separate process-scoped launcher such as
`claude2` for each additional account.

Read [references/claude-code-multi-account-windows.md](references/claude-code-multi-account-windows.md)
before changing account entries. It defines the supported authentication boundary and
the complete discovery, apply, verify, and rollback workflow. Use
`scripts/manage_claude_code_account.ps1` for Windows:

```powershell
& '<skill-dir>\scripts\manage_claude_code_account.ps1' -Action Discover -Name claude2
```

The script is parameterized: future entries such as `claude3` use the same mechanism.
It only creates or removes an exactly matched marked launcher and never reads, copies,
or changes credential files. `Verify` asks the CLI for its status in memory only and
refuses to claim account isolation while a known process-level provider or profile
selector is present. Do not use it for Codex accounts, and do not claim isolation for
IDE extension hosts or unsupported keyless Claude Console dual-login flows.

To preview distribution of just this on-demand Skill to Claude Code without trying to
replace every locally installed Skill, use the repository's focused profile:

```powershell
python scripts/distribute_skills.py --profile claude-code-multi-account --target claude
```

That command is a dry run. Add `--apply` only after reviewing its plan; if it detects
an existing unmanaged copy, inspect it and decide explicitly whether `--adopt-existing`
is appropriate.
