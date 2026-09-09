---
name: systematic-debugging
description: Diagnose bugs, test failures, performance problems, and unexpected behavior through reproducible evidence and falsifiable hypotheses before changing production behavior. Use when the cause is not already proven or when previous fixes failed.
---

# Systematic Debugging

## Debug contract

1. Reproduce the symptom, or gather the best available logs, traces, state, and timing
   evidence when reproduction is intermittent.
2. Read the complete error and recent relevant diff. Trace inputs, outputs, ownership,
   configuration, and state across the boundary where correct becomes incorrect.
3. Separate facts from inference. State one falsifiable hypothesis: cause, supporting
   evidence, and the observation that would disprove it.
4. Run the smallest experiment that changes one variable. Instrument boundaries instead
   of adding several speculative fixes.
5. Fix the earliest proven cause that owns the invariant, not a downstream symptom.
6. Add regression protection where practical and run the relevant verification from
   `automated-testing-workflow`.
7. If repeated attempts fail or each fix exposes new coupling, stop stacking patches and
   reconsider the assumption or architecture with the user.

Do not require a literal five-question chain. Use [five-whys.md](references/five-whys.md)
only when a causal chain spans process or system boundaries and the technique adds
clarity.

## Evidence at multi-component boundaries

For each relevant boundary, capture what enters, what exits, which configuration/version
is active, and who owns the state. Avoid logging secrets or sensitive payloads. A useful
probe should identify the failing boundary, not just produce more output.

## When the cause is external

Record what was ruled out and add the appropriate handling or observability: a bounded
retry, timeout, actionable error, health signal, or diagnostic event. Do not label a cause
“external” merely because it is hard to reproduce.
