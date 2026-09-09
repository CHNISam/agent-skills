---
name: preventing-repeat-failures
description: Turn explicit user dissatisfaction, escaped regressions, repeated agent failures, or review findings into the smallest durable protection at the correct scope. Use after correcting the current outcome when the failure reveals a missing test, deterministic guard, project rule, or shared skill.
---

# Preventing Repeat Failures

Improve the system without converting every complaint into global policy.

## 1. Capture the failure precisely

Record only what changes future decisions:

- observed outcome and evidence;
- expected outcome or violated contract;
- why existing tests, checks, instructions, or tools did not prevent it;
- whether this is a first occurrence, a regression, or a repeated pattern.

Fix the current task first. Do not use process work to avoid delivering the requested
outcome.

## 2. Choose the ownership scope

| Scope | Signal | Destination |
|---|---|---|
| Task | Wording/context was missing only in this request | Improve the current task contract or handoff; no permanent global rule. |
| Project | Depends on one product, architecture, command, data model, or repository convention | Project test/script/CI/AGENTS or owned technical doc. |
| Shared skills | Repeated or clearly generalizable failure across projects/agents | The shared skill repository, with its validation and explicit authority. |

A strong user preference is not automatically universal. Promote to shared scope only
when the rule is cross-project, the same failure repeats, or a general mechanism can
prevent a demonstrated class of failures without constraining unrelated work.

## 3. Prefer executable protection

Choose the first effective layer:

```text
regression/contract test
  → deterministic check or script
  → CI/merge gate
  → project instruction or architecture invariant
  → shared Skill
  → global prose rule
```

Do not add a Skill when a test can reject the failure. Do not add a global rule when a
project invariant owns it. Consolidate or remove an obsolete rule when the new mechanism
supersedes it; avoid parallel wrappers.

## 4. Respect mutation boundaries

Within an authorized implementation task, add project-local regression protection that
is necessary to make that task complete. Do not silently edit global configuration,
external repositories, or shared skills. To change a shared skill, obtain explicit
authority, use an isolated branch, run that repository's own validation, and provide a
whole-diff walkthrough proportional to risk.

## 5. Prove the improvement

Verify two outcomes:

1. the original task now satisfies its contract;
2. the new protection would fail or alert on the escaped behavior.

Report the chosen scope, protection, and any reason the failure remains only documented.
If no durable change is justified, say so and avoid adding policy noise.
