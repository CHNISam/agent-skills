---
name: automated-testing-workflow
description: Design and enforce requirements-first automated verification for features, bug fixes, refactors, business rules, and test changes. Use to choose risk-proportionate test layers, prove regressions, assess whether passing tests are meaningful, diagnose failures, or report completion evidence.
---

# Automated Testing Workflow

Automated verification is the completion gate, not an optional final check. Test the
requirement, not the implementation.

The repository's own testing policy is authoritative wherever it exists: its canonical
command, required layers, coverage rules, CI and merge gates, and review requirements.
Follow what the repository settles; this skill supplies judgment only for what it leaves
open. When it has no canonical command, configure
`scripts/verify.sh` or `scripts/verify.ps1` with a repo-local `verify.config`; the scripts
execute format → lint → typecheck/build → test in order, fail fast, and report exactly
what did and did not run.

## 1. Define observable proof

Translate the requested outcome into a contract or invariant before choosing tests.

- Good: “after climbing stops, stamina no longer decreases.”
- Weak: “`stop_climbing()` was called once.”

Choose the cheapest layer that can falsify the contract, then add the smallest amount of
real-boundary coverage needed:

| Change | Minimum useful evidence |
|---|---|
| Local non-behavioral edit | Focused static check or relevant test. |
| Feature / behavior change | Focused contract tests plus canonical repository verification. |
| Bug fix | Reproduce → regression protection → fix → prove the original symptom gone. |
| Refactor | Existing characterization/contract tests before and after; add missing boundary coverage when risk warrants. |
| API/data/security/persistence/concurrency | Contract and integration tests for failure, retry, authorization, and compatibility paths as applicable. |
| UI/game/presentation | Automated logic/scene checks plus runtime or visual evidence where pixels, animation, or input matter. |

Prefer many fast deterministic tests, enough integration tests for real boundaries, and a
few high-value E2E flows. Do not turn “important” into “everything must be E2E.”

## 2. Prove test quality

A green suite is evidence only if it would fail when the required behavior is broken.
For every added or materially changed test, check:

- the assertion observes the contract rather than a private call sequence;
- the test is not permanently true, empty, or only proving a mock;
- production logic is not copied into the test as its oracle;
- the failure path and important boundary cases are represented;
- the test is isolated and deterministic, without order dependence or arbitrary sleeps.

For a regression, demonstrate the test against the pre-fix behavior when practical and
safe (red/green, a temporary revert in an isolated worktree, or a controlled mutation).
If that proof is infeasible, record why and what alternative evidence shows the test is
capable of failing.

Use property-based, contract, snapshot/visual, performance, or mutation testing only when
the contract benefits from it. Mutation testing is especially useful for critical logic
or a periodic test-quality audit, not as a default per-commit tax.

## 3. Handle failures without gaming the gate

A failure means observed behavior and expectation differ. Establish whether the cause is
product code, the test, the environment, or an authorized requirement change before
editing.

Proceed with adding coverage, fixing code to a confirmed contract, or refactoring tests
without semantic change. Obtain confirmation before changing a business expectation.
Never delete, skip, quarantine, loosen, swallow, or replace a deterministic assertion
merely to get green.

An intermittent failure is a flaky signal, not a pass. Record and fix shared state,
ordering, timing, environment, or observability. A rerun may gather evidence; it does not
erase the first failure.

## 4. Completion gate

Before claiming done:

1. Run every added or changed test.
2. Run affected module and contract tests.
3. Run the repository's canonical verification for normal, broad, or risky behavior
   changes; if impossible, state the concrete blocker.
4. Add runtime/visual evidence when automated tests cannot observe the required outcome.
5. Read the exit code and output; do not infer success from code inspection or an agent's
   report.

Report exact commands, pass/fail/skip results, what was not run and why, and residual
untested risk. A relevant unexplained failure means the task is not complete.
