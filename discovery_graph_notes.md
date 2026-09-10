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

**Recursion.** Source: same repo, `codex-rs/ext/skills/src/loader/host.rs`:

```rust
pub(crate) fn discovery_mode(&self) -> SkillDiscoveryMode {
    self.plugin
        .as_ref()
        .map_or(SkillDiscoveryMode::Recursive, |plugin| {
            plugin.discovery_mode
        })
}
```

`DirectChildren` mode (depth-limited to `root/<name>/SKILL.md`) applies only when a root
belongs to a plugin (`self.plugin` is `Some`). Every root this repo cares about — `.codex/skills`
and `.agents/skills` — is constructed via `HostSkillRoot::host(...)`, which leaves `plugin: None`,
so `discovery_mode()` falls through to `Recursive` (`codex-rs/ext/skills/src/loader/discovery.rs`
walks up to `MAX_SCAN_DEPTH`, collecting **every** `SKILL.md` found, at any depth). This means a
duplicate does not require two different roots at all: two sibling directories *inside the same
root* that both contain a nested `SKILL.md` with the same declared `name` are indistinguishable
from a cross-root duplicate to Codex — both paths are discovered, neither is preferred, both are
shown. Confirmed on this machine: `~/.codex/skills/blender-agent-studio/` and
`~/.codex/skills/blender-agent-studio-suite/` are two top-level directories (an old install and a
later reinstall under a renamed folder) that are **byte-identical**, each containing the same 11
nested skills (`blender-agent-benchmark/SKILL.md`, `blender-animation-workflow/SKILL.md`, …).
Codex's recursive walk finds all 22 files and shows all 11 skill names twice. This is real,
third-party content with zero presence anywhere in `agent-skills`' history (`git log --all -- '*blender*'`
touches only an unrelated `godot-master/scripts/*_blender.gd` filename) — this repo does not
manage or remove it; see the Real Machine Verification section of the corresponding task report.

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

**Recursion.** `EXTERNAL_SKILL_PATTERN = "skills/**/SKILL.md"` and
`OPENCODE_SKILL_PATTERN = "{skill,skills}/**/SKILL.md"` (both quoted above) are glob patterns
with `**` — recursive, any depth, same consequence as Codex: a nested duplicate inside one root
is found and shown the same as a cross-root duplicate.

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

**Recursion.** Cursor's own docs state it directly: "Cursor walks the skills root recursively
and picks up any `SKILL.md` it finds." Same consequence as Codex/OpenCode.

## Escaped regression: physical-install correctness was not effective-catalog correctness

An earlier pass of this repo's own distributor validated dry-run convergence, managed-state
correctness, and rollback/prune safety — and still shipped a machine with real duplicate
skills in Codex's catalog. Two independent gaps let it through:

1. **State-file narrowing.** `distribute_skills.py`'s `write_state()` always overwrites a
   target's `managed_skills` with the *current* run's selection. A `--profile all --apply`
   followed later by `--profile core --apply` (no `--prune`) leaves the earlier run's ~90
   extra directories physically in place but silently untracked — never prunable again,
   invisible to every check that only reads the state file.
2. **One-level scanning.** The original `audit_catalog.py` scanned exactly `root/<name>/SKILL.md`,
   one level. It could not have caught the `blender-agent-studio` / `blender-agent-studio-suite`
   pattern above even in principle, because Codex's own real scan is recursive and this
   tool's model of it was not.

Neither gap was visible from `.skills-managed.json`, from a passing dry-run, or from
`SYNC_OK`. They were only visible by walking the *real* discovery graph — recursively, where
each agent's real behavior is recursive — and diffing that against the machine's actual files.
That is what `scripts/audit_catalog.py` now does, and why a distribution is not complete just
because it reports success; see the completion-gate section of the task report for how this is
now enforced mechanically rather than left to inspection.

## Net result

Two physical write roots — `.claude/skills` and `.agents/skills` — cover all four agents.
`.codex/skills`, `.config/opencode/skills`, and `.cursor/skills` are real discovery roots
these agents scan, but every skill this repo manages already reaches them through the two
roots above; writing a third copy there would only add duplication, not coverage. This
repo's distributor never writes to those three, and the machine's existing copies from
before this change were decommissioned (see `scripts/distribute_skills.py --decommission`).

## Two separate checks, on purpose

`audit_catalog.py` deliberately does not have one "is it done" answer. It has two:

- **`managed_gate()`** — what `distribute_skills.py --apply` calls right after `SYNC_OK`.
  Binary, scoped to exactly the skills that run just placed. It answers "did this apply
  create an unintended duplicate among skills this repo manages" and nothing about the
  rest of the machine. A personal skill pack's own internal duplicate, or a third-party
  plugin's, never fails this gate — it never looked at them.
- **`full_audit()`** — what `python scripts/audit_catalog.py` (no arguments) runs. Walks
  every discovery root for every agent and classifies every duplicate name found,
  anywhere, into `EXPECTED` / `REVIEW_REQUIRED` / `PROBLEM`. Its own status
  (`FULL_CATALOG_STATUS: CLEAN|REVIEW_REQUIRED|PROBLEM`) is a three-way result, and only
  `CLEAN` — exit code 0 — means "nothing unresolved anywhere". `REVIEW_REQUIRED` has its
  own exit code (2), distinct from `PROBLEM`'s (1), specifically so a script or an agent
  cannot collapse "not a hard failure" into "success". Conflating these two checks — or
  reporting a scoped `managed_gate()` pass as if it were a clean `full_audit()` — is
  exactly the escaped-regression pattern this file documents above; keep them separate.

`REVIEW_REQUIRED` exists for duplicates this repo has no authority or confident basis to
resolve on its own:

- a name agent-skills has never shipped (current or retired) — third-party content, never
  auto-deleted, no matter how confidently it looks like a duplicate;
- a name agent-skills recognizes, but the content genuinely differs across paths this repo
  does not uniformly control — which version is authoritative is a decision, not something
  to guess;
- a name — retired or current — found nested inside something deeper than this repo's own
  distributor ever writes (`<root>/<name>/SKILL.md`, always exactly one level). Some of
  this repo's own now-retired skills were themselves verbatim copies of an upstream source
  (see `NOTICE`), so a raw install of that same upstream plugin can be byte-identical to
  what this repo once shipped and retired, without being this repo's placement — or this
  repo's to delete — at all. Confirmed on this machine: a separately-installed, unmodified
  `obra/superpowers` plugin sits at `.claude/skills/superpowers/<name>/SKILL.md` for
  fourteen names, two of which (`using-superpowers`, `verification-before-completion`) are
  also this repo's own retired names. `PROBLEM`'s "remove it" fix only ever applies to a
  *direct* placement — one this repo's own tooling could actually have made.

`REVIEW_REQUIRED` is not a permanent resting state for a name this repo *does* control: nine
non-core skills found with genuinely diverged content between `.claude/skills` and
`.agents/skills` (independent installs at different times, before this repo's own state
tracking existed) were resolved by syncing both copies to the current canonical repo
content — an objective, reproducible reference point, not a guess about which locally-
drifted version was more "intended". They now register as `EXPECTED` like any other
Claude+Agents overlap. What remains under `REVIEW_REQUIRED` on this machine is exactly the
third-party content above (the `blender-agent-studio` duplicate, `blender-production-suite`,
`bencium-controlled-ux-designer`'s nested plugin layout, the `superpowers` plugin pack, and
Codex's own bundled `openai-docs`/`skill-creator` under `.system/`) plus `reaper-music-
production`, none of which this repo has ever shipped or has any basis to touch.

## Cursor's dedup behavior remains genuinely unverified

Checked for a real introspection path on this machine: the `cursor` binary
(`D:\cursor\resources\app\bin\cursor.cmd`) is the GUI editor launcher only — its `--help`
exposes no skill-listing or debug command comparable to Codex's `codex debug prompt-input`.
A `cursor-agent` entry exists on `PATH` but resolves to nothing (`command not found`) — a
standalone Cursor CLI product is not installed here. Unlike Codex, verified against real
runtime output, Cursor's dedup precedence is asserted only from its own docs' silence on the
topic, and stays classified that way (`"dedup": "undocumented by Cursor; verify empirically"`
in `skill-profiles.json`) rather than being claimed as verified. Confirming it requires
either a human opening Cursor's own Skills panel (Customize → Skills) and reporting what it
shows for a name known to exist at both `.claude/skills` and `.agents/skills`, or a future
session with access to a Cursor CLI product this one does not have.

## Logical identity is plugin-namespaced (runtime-verified, 2026-09-10)

Everything above describes *where* agents look. This section describes *what they key
on* once they get there, which is the part the audit got wrong for its first few
revisions and the part the reported duplicate-skill symptom actually turns on.

A skill's catalog identity is **not** simply its `name:` frontmatter. When a skill lives
inside a plugin — i.e. some ancestor directory carries a plugin manifest
(`.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`)
— the runtime keys it as `<plugin name>:<skill name>`. A standalone skill keeps its bare
name.

### How this was established

`codex debug prompt-input` renders the exact model-visible prompt, including the skills
block, without calling a model. It is the runtime's own answer to "what is in your
catalog", and it is what `scripts/audit_catalog.py --runtime` diffs the static model
against. Probe skills were written into `~/.agents/skills`, the command re-run, and the
rendered ids read back:

| fixture                                            | rendered id                     |
| -------------------------------------------------- | ------------------------------- |
| `zzprobe-top/`                                      | `zzprobe-top`                   |
| `zzprobe-bundle-a/zzprobe-nested/`                  | `zzprobe-nested`                |
| `zzprobe-bundle-b/zzprobe-nested/`                  | `zzprobe-nested` (again)        |
| `zzprobe-bundle-c/zzprobe-top/`                     | `zzprobe-top` (again)           |
| `zzprobe-plug/` + `.claude-plugin/plugin.json`      | `zzprobe-plug:zzprobe-inplug`   |

Three things fall out of this, all of which the audit now encodes:

1. **A container directory does not namespace anything.** Two sibling bundle directories
   inside one root, each holding a skill with the same `name:`, produce the *same id
   twice*. Nothing merges them and nothing warns.
2. **A plugin manifest does namespace.** Only the manifest — not depth, not scan order,
   not collision with an existing bare name — introduces the `<plugin>:` prefix.
3. **There is no name-level deduplication at all.** Order was tested in both directions
   (`zzprobe-alpha` at top level plus `zzprobe-zbundle/zzprobe-alpha`, and the reverse
   ordering above); the loser is never suppressed or renamed. Codex's
   `dedupe_skill_roots_by_path` dedupes *roots*, not skills.

### Why the manifest walk resolves symlinks

`~/.agents/skills/superpowers` is a link to `~/.codex/superpowers/skills` — the plugin's
*inner* `skills/` directory. The manifest lives at `~/.codex/superpowers/.claude-plugin/`,
one level above the link target and entirely outside the walked root. Walking unresolved
paths finds nothing and reports `brainstorming`, colliding falsely with the standalone
`~/.agents/skills/brainstorming`. `plugin_namespace()` therefore resolves before walking.

Relatedly, `Path.rglob` stopped following symlinks while expanding `**` in Python 3.13;
`scan_root()` passes `recurse_symlinks=True` because the agents do follow them, and an
unfollowed link is a blind spot rather than a conservative omission. (On Windows this is
easy to miss: a *junction*, which is how several packs here are installed, is not a
symlink to Python and recurses either way.)

## Roots the earlier model missed

Two roots were absent from `discovery_graph` and were found by diffing the model against
the rendered runtime catalog:

- **`$CODEX_HOME/skills/.system`** — Codex's own built-in skills. Not a separate root in
  the manifest: `.codex/skills` is scanned recursively, and `.system` is a subdirectory of
  it, dot-prefix notwithstanding. This is where the `openai-docs` / `skill-creator`
  collisions with this repo's own copies came from.
- **`<cwd>/.agents/skills`** (and `<cwd>/.claude/skills` for Claude Code) — the
  **project-scoped** root. Anchored on the working directory, not the home directory, so
  the graph gained a `"base": "project"` field and the audit a `--project` argument. This
  repository's own `.agents/skills/` is exactly this shape, which is how the gap surfaced.

## Install-gated roots

`$CODEX_HOME/plugins/cache` holds plugin-provided skills as
`<plugin>/<version>/skills/<name>`, but only *installed and enabled* plugins reach the
catalog, and install state is not a filesystem fact. It is declared in the graph with
`"install_gated": true`: recorded, never statically walked (a walk would report skills the
runtime does not show, including phantom duplicates between two cached versions of one
plugin), and exempted from the runtime diff. `runtime_check()` is deliberately asymmetric
for the same reason — a runtime entry the model does not know about is a blind spot and
fails; a modelled entry the runtime does not show is conservative and only warns.
