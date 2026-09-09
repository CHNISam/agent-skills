# High-risk review prompts

Read only for a High-risk change. Verification and runtime evidence are mandatory;
independent review is risk-triggered rather than automatic.

Check the boundary that creates the risk:

- auth/security/privacy: denied paths, privilege changes, secret exposure, abuse inputs;
- persistence/migrations: forward/backward compatibility, partial application, retry,
  rollback, old data, and interrupted execution;
- concurrency/lifecycle: ownership, ordering, cancellation, cleanup, idempotency, races;
- public API/protocol: callers, consumers, version skew, error semantics, deprecation;
- released compatibility: supported tags, stored formats, configuration, deployment order.

Preserve exact reviewed range, verification evidence, unresolved risk, and any independent
review findings in the single `review-pack.md`. Re-review executable content if it changes
after review; formatting-only deltas may retain prior evidence after a self-check.
