---
name: large-change-review
description: Risk-tiered walkthrough and review for broad or high-risk changes before integration. Use for large refactors, multi-file rewrites, architecture or module-boundary changes, changes touching security/credentials/persistence/concurrency/released compatibility, or any diff big enough that a single-pass self-check is not enough. For a normal small feature, use requesting-code-review instead. Also use when asked to "walk through", "audit", or "final review" a completed branch or PR.
---

# Large Change Review

A structured walkthrough of a **completed** change against its **original intent**, before
it integrates. Scales with risk: trivial changes stay trivial, high-risk changes get an
independent pass. Adapted from OpenAI's `implementation-final-review` — see `NOTICE`.

Do not bury this logic in `AGENTS.md`. It is a workflow with judgment, so it is a skill.

## 1. Pick the tier — by semantic impact, not line count

Classify the **whole** change. Record the tier and a one-line reason in your working notes.

| Tier | Boundary | Required review |
|---|---|---|
| **Lightweight** | Only spelling, comments, formatting, or a pure mechanical rename. No change to execution, public contracts, test expectations, config, or documented meaning. | Self-check the complete diff + run focused checks. No independent reviewer. |
| **Ordinary** | Local behavior changes within an existing contract; ordinary test additions; behavioral docs. No high-risk boundary touched. | Do the walkthrough (§2–§3). One independent read-only reviewer (§4) if the diff is large or spans many modules; otherwise a rigorous self-walkthrough is enough. |
| **High-risk** | Touches security, credentials, sensitive-data handling, auth/trust, persistence / durable state / migrations, concurrency / cancellation / shared lifecycle, released or cross-package compatibility, protocol or public API surface. Also: any review cycle with a confirmed P0/P1. | Full walkthrough + **independent** reviewer(s) in a fresh context. Read [references/high-risk.md](references/high-risk.md). |

Escalate, never downgrade: a one-line condition fix on an auth check is High-risk. Test
deletion, changed test expectations, and CI/build config changes are **not** Lightweight.
If you are unsure whether a boundary is high-risk, treat it as high-risk until proven
otherwise.

Trivial changes do not need this skill at all — a typo fix or a single obvious bugfix
goes through `requesting-code-review` or straight to normal verification.

## 2. Establish the baseline

1. **Original task & acceptance criteria** — restate what this change was supposed to do
   and how "done" was defined. If you cannot, stop and recover it first.
2. **Merge base** — `git merge-base <target-branch> HEAD`. Review the **complete** diff
   from there (`git diff <merge-base>...HEAD`), including committed, staged, unstaged, and
   task-owned untracked files. **Not** just the latest commit.
3. **Released compatibility** — if downstream consumers pin a released version, also diff
   against that tag separately.

## 3. Walkthrough — produce a concise written summary

Cover, briefly:

- **What changed** — the components touched and the shape of the change.
- **Why** — tie each cluster of edits back to the acceptance criteria.
- **Architecture / control-flow deltas** — new or moved boundaries, changed call graphs,
  changed data ownership, new async/lifecycle behavior.
- **Migration / compatibility impact** — schema, API, config, on-disk format, public
  exports. What a consumer must do to adopt.
- **Tests & evidence** — which suites ran, results, what visual/manual evidence exists.
- **Residual risk** — what is still uncertain or deferred.

Then scan the diff specifically for:

- accidental **unrelated** changes (stray formatting, debug prints, unrelated files)
- **duplicated** implementation of something that already exists in the repo
- **architecture boundary violations** (a layer reaching past its contract)
- **stale / dead code** left behind by the change
- **missing regression coverage** for the behavior that changed
- **unnecessary complexity** — conditions piled on conditions; if the same design problem
  keeps generating findings, reset the design instead of adding more branches
- **behavior silently removed** — a feature or guard that quietly stopped happening

## 4. Independent reviewer (only when size/risk justifies the token cost)

Launch **one** agent with no inherited implementer conversation. Give it: the original
request, a short scope contract, target/base/head refs, the complete diff including
new-file contents, relevant architecture docs, and the exact focused-check commands + results.
Do **not** hand it your suspected findings or proposed fixes.

The reviewer does **one read-only pass** — no edits, no re-running the implementation
strategy, no recursive delegation, no broad suites (focused non-mutating probes only). It
returns: the scope it actually inspected, concrete actionable findings, and remaining
uncertainty. A bare "looks good" without inspected scope is not a review.

Then: validate findings against intended behavior, fix them as **one batch**, re-run
affected checks, and get an independent pass on the changed content if scope or
cross-cutting assumptions moved. Keep a running count of revision cycles in your notes —
if it climbs past a handful, get a concrete scope/design decision from the user rather
than looping.

## 5. Verify and report

Run the full applicable verification gate on the **final** content
(`automated-testing-workflow` + its `scripts/verify.*`). A lighter review tier does not
waive verification. Report completion only when both review and verification apply to the
delivered state, and state the tier, what the reviewer inspected, and residual risk.
