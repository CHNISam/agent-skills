---
name: large-change-review
description: Produce a whole-diff walkthrough and risk assessment for broad, high-risk, architectural, compatibility-sensitive, or hard-to-understand completed changes. Use when asked for a walkthrough/final review or when the diff crosses important boundaries; ordinary localized changes need only normal verification and a concise diff review.
---

# Large Change Review

Verification remains the quality gate. This skill lowers the cost of understanding and
handing off a broad change; it does not substitute a reviewer for tests.

## Tier by semantic impact

| Tier | Boundary | Review |
|---|---|---|
| Lightweight | Formatting, comments, spelling, mechanical rename; no behavior, config, test expectation, or contract change. | Complete-diff self-check; no artifact. |
| Ordinary | Local behavior or multi-file change within existing contracts. | Walkthrough and `review-pack.md` when breadth makes handoff useful. |
| High-risk | Security/auth, credentials, sensitive data, persistence/migration, concurrency/lifecycle, public protocol/API, released compatibility, or confirmed P0/P1. | Full walkthrough, broad verification, explicit residual risk. Independent review only when requested or when material risk cannot be mechanically exercised. |

Line count does not lower risk. Test deletion, changed expectations, and CI/build changes
are never Lightweight.

## Establish the baseline

Recover the original task and acceptance criteria. Compute the merge base with the target
branch and review the complete `<merge-base>...HEAD` diff plus task-owned staged,
unstaged, and untracked changes. Check a released tag separately when downstream
compatibility requires it.

## Canonical deliverable

For Ordinary/High-risk work, produce exactly one `review-pack.md` outside the shipped
deliverable unless repository policy requires it in-tree. Reference canonical files and
the diff; do not paste source or restate Skill bodies.

1. Tier and one-line reason.
2. Task and acceptance criteria.
3. Target, merge-base SHA, and exact reviewed range/state.
4. Change summary and why this shape was chosen.
5. Architecture/control-flow/data-ownership changes, or “none.”
6. Important files and what each now owns.
7. Narrated walkthrough of the complete diff, grouped by responsibility and tied to the
   acceptance criteria.
8. Exact verification commands and actual pass/fail/skip results; what was not run.
9. Regression, compatibility, migration, rollout, and rollback risk as applicable.
10. Unresolved findings, accepted risk, deferred work, and review revision count.

Actively look for unrelated changes, duplicated mechanisms, boundary violations, stale
or dead code, silently removed behavior, weak regression coverage, and unnecessary
complexity. A passing suite is meaningful only if it would fail when the requirement is
broken.

## Optional independent review

Use a fresh-context read-only reviewer when the user asks, repository policy requires it,
or judgment-heavy residual risk remains after tests and runtime evidence. Give it the
review pack, exact diff, and named architecture sources—not the implementer's suspected
findings. Require inspected scope, actionable findings, and uncertainty; a bare “looks
good” is not a review.

Validate findings, fix them in a coherent batch, and rerun affected verification. Do not
spawn reviewers by default for an ordinary change, and do not block mechanically proven
work merely because an independent reviewer is unavailable unless project policy says so.

Finalize the pack only after `automated-testing-workflow` has verified the delivered
state. The chat handoff can remain brief and link to the pack.
