# High-risk review prompts

Read only when the change materially alters a high-risk boundary. Verification and runtime
evidence are mandatory; independent review is risk-triggered rather than automatic.

Check only the boundary that creates material risk:

- auth/security/privacy: denied paths, privilege changes, secret exposure, abuse inputs;
- persistence/migrations: forward/backward compatibility, partial application, retry,
  rollback, old data, and interrupted execution;
- concurrency/lifecycle: ownership, ordering, cancellation, cleanup, idempotency, races;
- public API/protocol: callers, consumers, version skew, error semantics, deprecation;
- released compatibility: supported tags, stored formats, configuration, deployment order.

Preserve the exact reviewed range, verification evidence, unresolved risk, and any
independent-review findings in the normal task handoff or an existing project record.
Create a separate review artifact only when repository policy, auditability, or handoff
cost justifies it.

Re-review affected executable content when it changes after review; formatting/comment-only
deltas may retain prior evidence after a self-check.
