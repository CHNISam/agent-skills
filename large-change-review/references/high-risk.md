# High-risk review protocol

Read this only when the change is **High-risk** per the tier table in `SKILL.md`:
security, credentials, sensitive data, auth/trust, persistence / durable state /
migrations, concurrency / cancellation / shared lifecycle, released or cross-package
compatibility, protocol or public API surface — or any cycle carrying a confirmed P0/P1.

## Two independent reviewers, complementary focus

Launch **two** reviewers in fresh contexts (no inherited implementer conversation, no
shared reviewer conversation). Split their charge so coverage is complementary, e.g.:

- Reviewer A: correctness and the specific high-risk boundary (the auth check, the
  migration's forward/backward behavior, the lock ordering, the exported type).
- Reviewer B: blast radius — callers, consumers, released compatibility, failure and
  cancellation paths, what happens on partial application / retry / resume.

Each does one read-only pass and returns inspected scope + concrete findings + residual
uncertainty. Neither is given the other's conclusions or the implementer's suspected findings.

## Evidence to preserve

High-risk work still produces the single canonical `review-pack.md` (SKILL.md §3) — no
extra report files. Alongside it, keep, outside the shipped deliverable:

- the exact diff reviewed (a saved patch, or a content fingerprint), so a later
  comparison can prove what was reviewed;
- for each reviewer, its returned scope and findings, and how each finding was resolved,
  appended to `review-pack.md` item 10.

`review-pack.md` already carries the target/base/head IDs and merge-base (item 3) and the
verification commands and output (item 8); do not duplicate them into separate notes.

If the final content changes after review — behavior, expectations, contracts, or
dependencies — re-review the changed content and its boundaries. A demonstrably
formatting-only delta may retain prior review after a self-check; an executable change may
not. Committing or staging identical content does not invalidate a review.

## Resolution

- Fix findings as one batch; update the implementation strategy only if the contract or
  the shape of the implementation actually changed.
- Re-run every affected check plus the full verification gate on the final content.
- If repeated findings keep exposing the same design problem, stop adding conditions —
  reset the design and re-review.
- Keep consumed revision cycles and unresolved root causes in `review-pack.md` (item 10)
  so they survive any handoff or context compaction. If the budget is exhausted, get a
  concrete decision from the user before dispatching another round.

## If an independent reviewer is unavailable

Say so explicitly in the report. Self-review does **not** satisfy the high-risk gate —
the change ships as "reviewed by author only, independent review pending" and the user
decides whether that is acceptable.
