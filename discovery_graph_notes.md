# Discovery graph — evidence

`skill-profiles.json`'s `discovery_graph` records what each agent *actually* scans for
skills, and which of that this repository writes to (`write_root`) versus which paths are
real but intentionally left unmanaged (`write_root: null`) because a `write_root` this
repo already populates already satisfies them. This file is the evidence trail for that
manifest — verified against each agent's own docs or source, not guessed, on 2026-09-09.

## Claude Code

Official docs (`code.claude.com/docs/en/skills`, "Where skills load"): personal skills load
from `~/.claude/skills/<name>/SKILL.md`, project skills from `.claude/skills/<name>/SKILL.md`.
No cross-tool root — Claude Code does not read `~/.agents/skills`. This is the one agent
with a single, non-overlapping root, and the one place `.claude/skills` is not optional.

## Codex CLI

Source: `openai/codex`, `codex-rs/ext/skills/src/host_roots.rs`,
`roots_from_layer_stack()`, the `ConfigLayerSource::User` branch:

```rust
// Deprecated user skills location (`$CODEX_HOME/skills`), kept for backward
// compatibility.
roots.push(local_root(config_folder.join(SKILLS_DIR_NAME), SkillScope::User));

if let Some(home_dir) = home_dir {
    roots.push(local_root(
        home_dir.join(AGENTS_DIR_NAME).join(SKILLS_DIR_NAME),
        SkillScope::User,
    ));
}
```

So Codex reads both `~/.codex/skills` (its own comment marks this **deprecated**) and
`~/.agents/skills` (the current root). Deduplication happens in the same file via
`dedupe_skill_roots_by_path`, which — as the name says — dedupes by filesystem *path*, not
by declared skill `name`. A skill with the same `name` present under two different roots is
not merged; it is presented twice. This is the confirmed, source-level mechanism behind the
reported duplicate-skill symptom (e.g. the same skill appearing twice in a selector) for any
agent that (a) reads a root this repo writes to and (b) does not itself dedupe by name.
Consequence for this repo: never write to `.codex/skills`; write only `.agents/skills`.

## OpenCode

Source: `anomalyco/opencode` (formerly `sst/opencode`),
`packages/opencode/src/skill/index.ts`, `discoverSkills()`:

```ts
const CLAUDE_EXTERNAL_DIR = ".claude"
const AGENTS_EXTERNAL_DIR = ".agents"
...
if (!disableExternalSkills) {
  if (!disableClaudeCodeSkills) externalDirs.push(CLAUDE_EXTERNAL_DIR)
  externalDirs.push(AGENTS_EXTERNAL_DIR)
  for (const dir of externalDirs) {
    const root = path.join(global.home, dir)
    if (yield* fsys.isDir(root)) yield* scan(state, root, EXTERNAL_SKILL_PATTERN, ...)
  }
  ...
}
const configDirs = yield* config.directories()   // OpenCode's own root(s)
for (const dir of configDirs) yield* scan(state, dir, OPENCODE_SKILL_PATTERN)
```

and the merge step in `add()`:

```ts
if (state.skills[md.data.name]) {
  yield* Effect.logWarning("duplicate skill name", { name: ..., existing: ..., duplicate: match })
}
state.skills[md.data.name] = { ... }   // last write wins
```

OpenCode scans `~/.claude/skills` and `~/.agents/skills` unconditionally (both default on),
in that order, *plus* its own `~/.config/opencode/skills`. It **does** dedupe — by name,
last scan wins, with a logged warning on every collision. Because `~/.claude/skills` is
required anyway (Claude Code has no other root) and `~/.agents/skills` is required anyway
(Codex's current root), OpenCode will always see a repo-managed skill via two roots and log
a warning about it; that overlap is intrinsic to OpenCode's own cross-tool design, not
something this repo's placement choice can remove without dropping support for either
Claude Code or Codex. What this repo *can* remove is the third, redundant copy: OpenCode's
own root is fully covered once `.agents/skills` exists, so this repo does not write to
`~/.config/opencode/skills`.

## Cursor

Docs: `cursor.com/docs/skills` ("Where skills load"):

| Location            | Scope          |
| -------------------- | -------------- |
| `.agents/skills/`    | Project-level  |
| `.cursor/skills/`     | Project-level  |
| `~/.agents/skills/`  | User-level     |
| `~/.cursor/skills/`   | User-level     |

plus, verbatim: "For compatibility, Cursor also loads skills from Claude and Codex
directories: `.claude/skills/`, `.codex/skills/`, `~/.claude/skills/`, and
`~/.codex/skills/`."

So Cursor reads all four ecosystems' user roots. Its docs do not state a dedup/precedence
rule for a name collision across those roots — unlike Codex (proven, no dedup) and OpenCode
(proven, dedup by name), Cursor's behavior here is **undocumented and unverified** (Cursor
is closed-source, so there is no source to read the way there is for Codex/OpenCode).
Since `.claude/skills` and `.agents/skills` are both required regardless (Claude Code and
Codex each need one of them), Cursor will see a repo-managed skill via both no matter what
this repo does — the same irreducible overlap as OpenCode's. This repo does not additionally
write to `.cursor/skills` (redundant with `.agents/skills`) or `.codex/skills` (Codex's own
deprecated root). **Action item for a human:** after distribution, open Cursor's Skills
panel (Customize → Skills) once and confirm no unexpected duplicate entries — this is the
one agent in the graph this repo could not verify mechanically.

## Net result

Two physical write roots — `.claude/skills` and `.agents/skills` — cover all four agents.
`.codex/skills`, `.config/opencode/skills`, and `.cursor/skills` are real discovery roots
these agents scan, but every skill this repo manages already reaches them through the two
roots above; writing a third copy there would only add duplication, not coverage. This
repo's distributor never writes to those three, and the machine's existing copies from
before this change were decommissioned (see `scripts/distribute_skills.py --decommission`).
