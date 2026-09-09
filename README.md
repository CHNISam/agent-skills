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
- Per-project or per-machine configuration. Installed copies under `~/.agents/skills`,
  `~/.codex/skills`, `~/.claude/skills`, `~/.cursor/skills`, and
  `~/.config/opencode/skills` are generated; this Git worktree is the source of truth.

## Install or refresh

```bash
# Preview; dry-run is the default and nothing is written
python scripts/distribute_skills.py --profile core --target all

# First adoption: explicitly accept replacing same-name existing copies
python scripts/distribute_skills.py --profile core --target all --apply --adopt-existing

# Normal refresh after pulling this repository
python scripts/distribute_skills.py --profile core --target all --apply --prune
```

`skill-profiles.json` defines the `core`, `authoring`, and `all` profiles and the target
directory for each agent. The distributor records ownership in each target's
`.skills-managed.json`, replaces or prunes only skills it manages, refuses
unmanaged same-name collisions unless `--adopt-existing` is passed, stages copies
atomically, verifies digests afterwards, rolls back on failure, and leaves unrelated
personal skills untouched.

## Profiles

`core` is the default install set — broadly useful, agent-agnostic skills:

| Skill | Responsibility |
|---|---|
| `ask-questions-if-underspecified` | resolve material intent/risk ambiguity with minimum friction |
| `automated-testing-workflow` | requirements-first test strategy, quality, and completion evidence |
| `context-retrieval` | cheapest-capable retrieval ladder |
| `git-workflow` | Git conventions and history safety |
| `git-branch-experiment-management` | experiment lifecycle and concurrent-writer isolation |
| `init-repository-governance` | help a project write its own agent guidance and gates |
| `large-change-review` | whole-diff walkthrough and canonical review pack |
| `preventing-repeat-failures` | route a failure to the smallest durable protection, at the right scope |
| `systematic-debugging` | evidence → falsifiable hypothesis → smallest experiment → root fix |

`authoring` adds `skill-creator`. `all` exposes the entire library, including domain,
vendor, and format skills; use it deliberately.

Everything outside a profile is still available on demand — `brainstorming`,
`test-driven-development`, the document/format skills, and the domain skills load when
their specific task appears. None of them is mandatory because a repository happens to use
that language or engine.

Retired from the active surface: `using-superpowers`, `root-cause-and-verification`,
`5-whys-root-cause-analysis`, `pause-and-clarify-riper5`, `verification-before-completion`,
and `ai-native-sop`. Their useful invariants live once in the skills above;
`skill-profiles.json` lists them so validation keeps them from reappearing.

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
reappeared at the root, and profiles that reference skills that do not exist.

Licenses vary by skill. Each skill's `LICENSE.txt` or `NOTICE` governs; see [`NOTICE`](NOTICE).
