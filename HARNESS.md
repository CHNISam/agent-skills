# Agent Harness

This repository is a versioned skill library plus a small, enforceable harness core for
Codex, Claude Code, Cursor, OpenCode, and other Agent Skills-compatible coding agents.
It is not an agent framework. Prefer native capabilities, repository tests, and CI over
more orchestration.

The Git worktree is the source of truth. Local agent skill directories are generated
copies managed by `scripts/distribute_skills.py`; do not edit those copies as canonical
source.

## Operating contract

### 1. Turn plain language into a task contract

Users should be able to state the task naturally. Internally normalize it to:

```text
Goal        observable outcome
Constraints what must not change, risk/compatibility boundaries
Done when   evidence that proves the outcome
References  only supplied or genuinely useful sources
```

Do not require the user to fill a template. First inspect repository evidence. Use a
reasonable project convention for small reversible ambiguity. Ask only when unresolved
ambiguity materially changes product behavior, scope, architecture, risk, or an
irreversible action. Treat user explanations of causes as hypotheses until verified;
treat explicit product intent as authoritative.

`ask-questions-if-underspecified` teaches the low-friction question format when this gate
actually fires.

### 2. Retrieve the least context that can answer the question

Use `context-retrieval`:

```text
known context → LSP → exact search → semantic/index search → targeted reads → repo docs
              → installed Skill → external source/MCP
```

Stop when the evidence is sufficient. Do not build a vector database, RAG service, code
graph, or custom indexer until native tools have demonstrably failed.

### 3. Verification is the completion gate

`automated-testing-workflow` owns verification judgment. A repository's canonical
command or `automated-testing-workflow/scripts/verify.*` executes the deterministic
gate. No relevant failure may be hidden by deleting, skipping, weakening, or repeatedly
rerunning tests until green.

Priority:

```text
P0 executable requirement and regression tests
P0 deterministic format/lint/type/build/test gate
P1 runtime/integration evidence at real boundaries
P1 test quality: the test would fail if required behavior broke
P2 review-pack.md for broad/high-risk changes
P3 independent human/agent review when risk still needs judgment
```

Passing tests are evidence only when they exercise the requirement. Prefer many fast,
deterministic tests, enough contract/integration coverage for real boundaries, and a few
high-value E2E/runtime flows. UI and games add visual/runtime evidence when pixels or
animation matter. A flaky result is a defect signal, not a pass.

### 4. Isolate change; scale review by risk

- `git-workflow` owns general Git safety and conventions.
- `git-branch-experiment-management` owns experiments and concurrent-writer isolation.
- Normal work uses a short-lived change branch. A separate worktree is required for
  genuinely concurrent writers and risky isolated experiments, not every sequential edit.
- `large-change-review` produces one `review-pack.md` outside shipped output for broad or
  high-risk work. The walkthrough helps people and future agents understand the whole
  diff. Independent review is optional and risk-triggered; verification is not optional.

### 5. Convert failures into the smallest durable guard

Use `harness-self-improvement` when the user rejects an outcome, a regression escapes, a
review finds a recurring failure, or an agent repeatedly takes the wrong path.

```text
failure → classify task/project/shared scope → fix current outcome
        → regression test → deterministic check/CI → project rule → shared Skill
        → global prose only as a last resort
```

Do not promote a one-off preference into global policy. Shared-harness changes require a
cross-project or repeated, generalizable failure and explicit authority to edit this
repository.

## Distribution

`harness-profile.json` is the machine-readable routing manifest.

```bash
# Preview; no writes
python scripts/distribute_skills.py --profile core --target all

# First adoption: explicitly accept replacement of same-name existing copies
python scripts/distribute_skills.py --profile core --target all --apply --adopt-existing

# Normal refresh after pulling this repository
python scripts/distribute_skills.py --profile core --target all --apply --prune
```

The distributor records ownership in each target's `.harness-managed.json`. It replaces
or prunes only skills it manages, refuses unmanaged collisions by default, stages copies
atomically, verifies digests, and leaves unrelated personal skills untouched.

## Skill tiers

### Core profile

| Skill | Responsibility |
|---|---|
| `ask-questions-if-underspecified` | resolve material intent/risk ambiguity with minimum friction |
| `automated-testing-workflow` | requirements-first test strategy, quality, and completion evidence |
| `context-retrieval` | cheapest-capable retrieval ladder |
| `git-workflow` | Git conventions and history safety |
| `git-branch-experiment-management` | experiment lifecycle and concurrent-writer isolation |
| `harness-self-improvement` | route failures to the smallest durable protection |
| `init-repository-governance` | tailor thin project adapters and wire mechanical gates |
| `large-change-review` | whole-diff walkthrough and canonical review pack |
| `systematic-debugging` | evidence → falsifiable hypothesis → smallest experiment → root fix |

### On demand

`brainstorming` for genuine product discovery; `test-driven-development` when red/green
adds confidence; `skill-creator` for maintaining skills; domain/vendor/format skills only
when their specific task appears. They are not installed by the default core profile.

### Retired from the active surface

`using-superpowers`, `root-cause-and-verification`, `5-whys-root-cause-analysis`,
`pause-and-clarify-riper5`, `verification-before-completion`, and `ai-native-sop` were
removed. Their useful invariants live once in the core above; their mandatory wrappers,
duplicated reasoning instructions, and prose-heavy ceremony do not.

## Harness verification

Every change to this repository must pass:

```bash
python scripts/validate_harness.py
python -m unittest discover -s tests -p "test_*.py" -v
```

GitHub Actions runs the same checks. `scripts/validate_harness.py` rejects malformed or
duplicate Skill metadata, missing profile entries, discoverable retired Skills, and
broken core routing.
