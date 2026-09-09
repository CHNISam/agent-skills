---
name: coding-agent-environment
description: Maintain a consistent local coding-agent baseline across Codex, Claude Code, OpenCode, and Cursor: native file access, code search, diagnostics/LSP where supported, documentation access, and shared skills. Use for a new machine, a new coding agent, environment audits, or cross-agent capability drift; not for project dependencies or business features.
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
