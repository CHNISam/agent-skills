---
name: test-driven-development
description: Apply a focused red-green-refactor cycle when a feature, bug fix, or refactor has a deterministic observable contract and seeing the test fail first would materially strengthen confidence. Use on request or when regression proof benefits from test-first development; do not force it onto exploratory, generated, visual-only, or untestable work.
---

# Focused Test-Driven Development

TDD is one useful method inside `automated-testing-workflow`, not a universal ceremony.

1. State one observable behavior or invariant.
2. Write the smallest test that would fail because the behavior is absent or broken.
3. Run it and confirm the failure is for the intended reason, not setup or syntax.
4. Implement the smallest coherent production change.
5. Run the focused test, then affected tests.
6. Refactor while keeping the contract green.

Prefer real behavior over mock call counts. Do not mirror production logic in the test.
For an already-written fix, do not delete correct work merely to recreate ritual order;
instead prove the regression test against the pre-fix behavior in an isolated and safe
way when practical.

Skip or adapt TDD when the work is exploratory, configuration-only, generated, dominated
by visual judgment, or lacks a deterministic harness. Still provide the best available
automated or runtime verification and state the limitation.
