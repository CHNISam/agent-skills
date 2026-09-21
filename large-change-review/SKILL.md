---
name: large-change-review
description: Review a completed change as a whole when semantic or architectural risk can escape ordinary tests. Use for broad cross-cutting changes, materially high-risk boundary changes, or an explicitly requested final walkthrough. Route by semantic impact, not file labels or line count; a localized change does not become high-risk merely because it touches persistence, concurrency, or another sensitive area.
---

# Large Change Review

Complement automated verification with one question:

> Does the complete delivered change still fit the intended system model and risk boundary?

This skill is not a substitute for tests and does not require a review artifact by default.

## Route by semantic impact

Use this skill when at least one of these is true:

- the diff crosses multiple responsibilities or changes architecture, authority, ownership, or lifecycle semantics;
- persistence/migration, concurrency, security/trust, public protocol/API, released compatibility, or another sensitive boundary is **materially changed**;
- a confirmed P0/P1 or similarly consequential change leaves judgment-heavy residual risk;
- the user or repository policy explicitly requires a whole-change review.

Do **not** invoke it solely because a touched file belongs to a sensitive subsystem. A localized change inside an established contract can use normal verification plus a complete-diff self-check when that is sufficient.

Repository policy may deliberately set a stricter gate.

## Establish the review boundary

Recover the task and acceptance criteria. Determine the intended target branch and merge base, then inspect the complete `<merge-base>...HEAD` task diff plus task-owned staged, unstaged, and untracked changes.

Review the delivered state, not only the last fix or latest commit.

## Review what tests may miss

Inspect only risk that can materially change the completion judgment:

1. **Purpose and scope** — does the complete diff still implement the intended task without unrelated change?
2. **Architecture and authority** — did ownership, source of truth, control flow, lifecycle, or dependency boundaries drift?
3. **Compatibility and recovery** — when applicable, are migration, old data, version skew, retry, rollback, and interrupted execution handled?
4. **Change quality** — look for duplicated mechanisms, stale/dead code, silently removed behavior, boundary violations, and unnecessary complexity.
5. **Verification sufficiency** — do the executed checks actually falsify the important contracts and failure modes?
6. **Residual risk** — state only unresolved uncertainty capable of changing acceptance, rollout, or follow-up.

For high-risk boundary-specific prompts, read `references/high-risk.md`.

## Evidence and independent review

Verification remains the completion gate. Record exact commands and actual pass/fail/skip results in the normal task handoff.

Use a fresh-context read-only reviewer only when repository policy requires one, the user asks for one, or material judgment-heavy risk remains that cannot be exercised mechanically. A bare approval is not evidence; require inspected scope, concrete findings, and remaining uncertainty.

Do not create `review-pack.md` or another durable artifact merely because this skill ran. Create a concise durable review note only when repository policy, auditability, or handoff cost justifies one.

## Completion

Review evidence applies to the content that was actually reviewed. Re-review affected boundaries when executable behavior, contracts, dependencies, or architecture change after review; formatting/comment-only deltas may retain prior evidence after a self-check.

Finish when the complete change is verified, semantically coherent for its risk boundary, and any material residual risk is explicit.
