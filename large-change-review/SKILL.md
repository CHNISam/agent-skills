---
name: large-change-review
description: Risk-tiered walkthrough and review for broad or high-risk changes before integration. Use for large refactors, multi-file rewrites, architecture or module-boundary changes, changes touching security/credentials/persistence/concurrency/released compatibility, or any diff big enough that a single-pass self-check is not enough. For a normal small feature, use requesting-code-review instead. Also use when asked to "walk through", "audit", or "final review" a completed branch or PR.
---

# Large Change Review

A structured walkthrough of a **completed** change against its **original intent**, before
it integrates. Scales with risk: trivial changes stay trivial, high-risk changes get an
independent pass. Adapted from OpenAI's `implementation-final-review` — see `NOTICE`.

Do not bury this logic in `AGENTS.md`. It is a workflow with judgment, so it is a skill.

## Canonical deliverable: `review-pack.md`

Every Ordinary or High-risk run produces **exactly one** artifact — `review-pack.md` —
written after implementation and verification. It is the standard hand-off: enough for
another agent to review the change or continue it without re-deriving context. Do not
invent per-task walkthrough or report filenames, and do not create additional report
artifacts unless the task explicitly asks for them. Lightweight runs produce nothing.

Put `review-pack.md` outside the shipped deliverable (e.g. a scratch/notes location), not
in the change itself, unless repository policy says otherwise. Its required contents are
defined in §3.

## 1. Pick the tier — by semantic impact, not line count

Classify the **whole** change. Record the tier and a one-line reason as the first line of
`review-pack.md`.

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

## 3. Write `review-pack.md`

One file, concise, in this order. Reference canonical files (paths, commit ranges, doc
links) instead of pasting them. Do **not** dump the full diff or full source. Do **not**
restate skill bodies.

1. **Tier** — Lightweight / Ordinary / High-risk, with a one-line reason.
2. **Task & acceptance criteria** — what this change had to do and how "done" was defined.
3. **Baseline** — target branch, `git merge-base` SHA, and the reviewed range
   (`<merge-base>...HEAD`); note if released-tag compatibility was also checked.
4. **Change summary** — a short paragraph: the shape of the change and why.
5. **Architecture / control-flow changes** — new or moved boundaries, changed call graphs,
   changed data ownership, new async/lifecycle behavior. "None" is a valid answer.
6. **Important changed files & ownership** — the handful that matter, one line each on
   what each now owns. Not an exhaustive list; point at the diff for the rest.
7. **Full-diff walkthrough** — walk the *complete* diff (committed + staged + unstaged +
   task-owned untracked), grouped by area, each group tied back to the acceptance
   criteria. This is a narrated map of the diff, not the diff itself.
8. **Verification** — the exact commands run and their **actual** results (pass/fail/skip
   counts, key output lines), plus what was not run and why.
9. **Regression / compatibility / migration risks** — schema, API, config, on-disk
   format, public exports; what a consumer must do to adopt.
10. **Unresolved findings / deferred work** — open items, known-but-accepted risks,
    follow-ups, and the revision-cycle count if a reviewer loop ran.

While walking the diff (item 7), actively check for and record: accidental **unrelated**
changes; **duplicated** implementation of something that already exists; **architecture
boundary violations**; **stale / dead code** left behind; **missing regression coverage**
for changed behavior; **unnecessary complexity** (if the same design problem keeps
generating findings, reset the design instead of adding branches); **behavior silently
removed**. Anything found goes into item 4/5 or item 10.

## 4. Independent reviewer (only when size/risk justifies the token cost)

Launch **one** agent with no inherited implementer conversation. Hand it `review-pack.md`
plus the reviewed diff and any architecture docs it names. Do **not** hand it your
suspected findings or proposed fixes.

The reviewer does **one read-only pass** — no edits, no re-running the implementation
strategy, no recursive delegation, no broad suites (focused non-mutating probes only). It
returns: the scope it actually inspected, concrete actionable findings, and remaining
uncertainty. A bare "looks good" without inspected scope is not a review.

Then: validate findings against intended behavior, fix them as **one batch**, re-run
affected checks, and get an independent pass on the changed content if scope or
cross-cutting assumptions moved. Record the revision-cycle count in `review-pack.md`
(item 10); if it climbs past a handful, get a concrete scope/design decision from the
user rather than looping.

## 5. Verify, then finalize `review-pack.md`

Run the full applicable verification gate on the **final** content
(`automated-testing-workflow` + its `scripts/verify.*`). A lighter review tier does not
waive verification. Then update `review-pack.md` items 8 and 10 with the real results and
any remaining open items.

Report completion only when review and verification both apply to the delivered state.
The chat report can be brief — tier, what was inspected, residual risk — and should point
to `review-pack.md` rather than repeat it.
