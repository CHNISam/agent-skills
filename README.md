# agent-skills

A cross-project, versioned library of [Agent Skills](https://github.com/agentskills/agentskills)
plus the tooling that distributes them safely to Codex, Claude Code, Cursor, and OpenCode.

It is a shared toolbox, not a harness for the projects that use it. Every project owns its
own agent guidance, architecture, tests, CI, and runtime rules; nothing here requires a
project to adopt a particular operating doctrine.

## What this repository owns

- Agent Skills that are genuinely reusable across projects and agents.
- The distribution mechanism: `skill-profiles.json`, `scripts/distribute_skills.py`, and
  the ownership/collision/rollback safety around it.
- Its own CI, structural validation, and regression tests (`scripts/validate_repo.py`,
  `tests/`).
- Provenance and licensing for bundled upstream skills (see [`NOTICE`](NOTICE)).

## What it does not own

- Any project's architecture, tests, CI, commands, release process, or runtime rules.
- Any project's `AGENTS.md` / `CLAUDE.md` content. Those are written from the project's
  real stack and live in the project repository.
- A global operating contract that projects must follow.
- Per-project or per-machine configuration. Installed copies under `~/.agents/skills` and
  `~/.claude/skills` are generated; this Git worktree is the source of truth.

## Install or refresh

```bash
# Preview; dry-run is the default and nothing is written
python scripts/distribute_skills.py --profile core --target all

# First adoption: explicitly accept replacing same-name existing copies
python scripts/distribute_skills.py --profile core --target all --apply --adopt-existing

# Normal refresh after pulling this repository
python scripts/distribute_skills.py --profile core --target all --apply --prune
```

`skill-profiles.json` defines the `core`, `authoring`, and `all` profiles and exactly two
physical write roots — see **Discovery-aware placement** below for why it's two, not five.
The distributor records ownership in each target's `.skills-managed.json`, replaces or
prunes only skills it manages, refuses unmanaged same-name collisions unless
`--adopt-existing` is passed, stages copies atomically, verifies digests afterwards, rolls
back on failure, and leaves unrelated personal skills untouched.

## Discovery-aware placement

Physical target directories are not the same thing as agents. Codex, OpenCode, and Cursor
each scan multiple directories for skills — including each other's — so copying the same
skill into "one folder per agent" creates real, user-visible duplicates: Codex does not
deduplicate skills with the same name found at different paths, and even the agents that do
dedupe still have to detect and discard the collision, which is unnecessary work this repo
can avoid by never creating it. `skill-profiles.json`'s `discovery_graph` records what each
agent actually reads (verified against each agent's own docs or source — see
[`discovery_graph_notes.md`](discovery_graph_notes.md)), and `targets` holds only the
physical roots this repo writes:

| write root | path | required because |
|---|---|---|
| `claude` | `~/.claude/skills` | Claude Code's only root; no cross-tool overlap |
| `agents` | `~/.agents/skills` | Codex's current root (its `~/.codex/skills` is deprecated); also the root OpenCode and Cursor scan for cross-tool skills |

Nothing is written to `~/.codex/skills` (deprecated), `~/.config/opencode/skills`, or
`~/.cursor/skills` (both redundant once `~/.agents/skills` exists) — those paths are real
discovery roots, just not ones this repo needs to populate. `scripts/audit_catalog.py`
computes each agent's actual effective catalog from the live discovery graph and flags any
skill name it finds at more than the roots that graph predicts.

An existing installation from before this design still has old copies sitting in those
three now-unmanaged roots; retire them with:

```bash
python scripts/distribute_skills.py --decommission ~/.codex/skills --apply
python scripts/distribute_skills.py --decommission ~/.config/opencode/skills --apply
python scripts/distribute_skills.py --decommission ~/.cursor/skills --apply
```

This removes exactly the skills this repo's own `.skills-managed.json` record shows it
placed there, then removes that record — it never touches a directory this repo never
managed, and never touches a skill it didn't put there itself.

## Profiles

`core` is the default install set — broadly useful, agent-agnostic skills with real,
non-generic content (concrete commands, decision tables, or tooling), audited to exclude
anything a capable model already does by default without a skill saying so:

| Skill | Responsibility |
|---|---|
| `ask-questions-if-underspecified` | resolve material intent/risk ambiguity with minimum friction |
| `automated-testing-workflow` | requirements-first test strategy, quality, and completion evidence |
| `context-retrieval` | cheapest-capable retrieval ladder |
| `git-workflow` | Git conventions and history safety |
| `git-branch-experiment-management` | experiment lifecycle and concurrent-writer isolation |
| `init-repository-governance` | help a project write its own agent guidance and gates |

`authoring` adds `skill-creator`. `all` exposes the entire library, including domain,
vendor, and format skills; use it deliberately.

Everything outside a profile is still available on demand — `brainstorming`,
`test-driven-development`, `large-change-review` (a whole-diff walkthrough and review pack
for broad/high-risk changes — real value, but not every change needs it, so it loads when
asked rather than installing by default), `systematic-debugging` (a debug-discipline
skill — structured evidence/hypothesis/smallest-experiment method plus a five-whys
technique for causal chains that cross system boundaries; kept because of that concrete
technique, demoted from core because the base contract is close to what a competent agent
already does), the document/format skills, and the domain skills — they load when their
specific task appears. None of them is mandatory because a repository happens to use that
language or engine.

Retired from the active surface: `using-superpowers`, `root-cause-and-verification`,
`5-whys-root-cause-analysis`, `pause-and-clarify-riper5`, `verification-before-completion`,
`ai-native-sop`, `ai-native-product-spec`, `product-to-spec` (a near-duplicate of
`ai-native-product-spec` — both converted product ideas into Agent-Ready Specs), and
`preventing-repeat-failures` (a generic "classify the failure, prefer the cheapest durable
guard" wrapper with no project- or tool-specific content — the judgment it encoded is
restated inline in `init-repository-governance` where it is actually used, rather than kept
as a standalone skill). Their useful invariants live once, where they still add something;
`skill-profiles.json` lists retired names so validation keeps them from reappearing.

`sync-global-skills` — this repository's own publish/backup workflow — is not a
root-level, distributable skill any more. It lived at `sync-global-skills/` before, which
made it eligible for `--profile all` distribution to every project on every agent, even
though it only makes sense inside a checkout of this repository. It now lives as a
project-level skill committed to this repo's own `.claude/skills/sync-global-skills/` and
`.agents/skills/sync-global-skills/` — Claude Code, Codex, OpenCode, and Cursor all pick up
project-level skills from inside a repository, so it still loads automatically when working
in *this* repo, and is structurally invisible to the distributor (which only scans direct
children of the repository root for skills), so it can never leak into another project.

## Adopt in a project

Use `init-repository-governance`. It reads the project's real stack, commands, and
existing instructions first, then helps the project author *its own* `AGENTS.md` and
mechanical gates. It does not copy this repository's rules into the project and does not
copy the skill library into the project.

## Verify changes to this repository

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -p "test_*.py" -v
```

GitHub Actions runs the same two commands. `scripts/validate_repo.py` rejects malformed or
duplicate Skill metadata, missing or duplicated profile entries, retired skills that
reappeared at the root, profiles that reference skills that do not exist, and a
`discovery_graph` whose `write_root` names don't match `targets`.

`scripts/audit_catalog.py` is a separate, machine-level check, and deliberately not one
check but two — see `discovery_graph_notes.md`'s "Two separate checks, on purpose" for
why they must stay apart:

```bash
# The narrow, scoped gate distribute_skills.py --apply already runs automatically after
# every SYNC_OK. Binary: only fails on a duplicate among skills THIS repo just applied.

# The full, whole-machine picture -- every agent, every real discovery root, every
# logical skill identity:
python scripts/audit_catalog.py

# ...and, additionally, ask each agent that can render its own catalog to do so and fail
# on any drift from the model above. Deterministic and LLM-free; skips agents that are
# not installed, so it is safe to run anywhere:
python scripts/audit_catalog.py --runtime
```

The invariant it enforces: **a logical skill may be materialized into several
agent-specific locations, but no single agent may ever *expose* it more than once** unless `skill-profiles.json`'s `duplicate_exceptions` records an explicit,
reviewed exception naming the agent, the identity, and the exact set of contributing
paths. An exception that matches nothing is itself a failure, so a waiver cannot outlive
the duplicate it waives.

"Logical identity" is what the agent's catalog actually keys on, which is *not* the bare
`name:` frontmatter: a skill shipped inside a plugin enters as `<plugin>:<skill>`. Two
copies of one plugin therefore are a duplicate, and a plugin's `brainstorming` next to a
standalone `brainstorming` is not. See `discovery_graph_notes.md`, "Logical identity is
plugin-namespaced", for the runtime evidence.

"Expose" is equally literal, and two things separate paths on disk from entries in a
picker. Paths that resolve to the same directory -- the symlinks and Windows junctions
that make cross-agent sharing work -- are one skill reached twice, not two skills. And an
agent that deduplicates by identity (`dedup_kind: "by-name"`, e.g. OpenCode and Cursor)
shows exactly one entry no matter how many roots contribute, so reuse across shared roots
is `DEDUPED`, never a defect; only a `by-path` agent such as Codex turns a second path
into a second entry. `dedup_kind` has no permissive default and `validate_repo.py`
requires it, so an unverified guess cannot silence a real duplicate.

`audit_catalog.py`'s full audit ends with `FULL_CATALOG_STATUS: CLEAN|REVIEW_REQUIRED|PROBLEM`
(exit 0/2/1). `CLEAN` is the only status meaning "nothing unresolved anywhere" — a
third-party duplicate this repo correctly refuses to delete forces `REVIEW_REQUIRED`, never
`CLEAN`; a duplicate this repo genuinely owns and can fix forces `PROBLEM`. Reporting a
passing scoped gate as if it were a clean full audit is exactly the failure mode this split
exists to prevent.

Licenses vary by skill. Each skill's `LICENSE.txt` or `NOTICE` governs; see [`NOTICE`](NOTICE).
