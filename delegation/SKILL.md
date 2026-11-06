---
name: delegation
description: Compile a sufficiently understood action into a minimal execution contract or prompt for another agent, model, tool, repository, runtime, or environment. Use only after the relevant action is sufficiently clear. Do not copy the entire world model into every prompt or turn an unverified capability assumption into an implementation mandate.
---

# Delegation and Prompt Compilation

Use when another agent or tool needs to execute a sufficiently understood action.

## Execution contract

Include only fields capable of changing execution.

Possible fields:

- Objective
- Current Problem
- Source of Truth
- Constraints
- Acceptance Criteria
- Evidence

When materially relevant:

- Required Capability
- Relevant Capability Surface / Available Means
- Existing Capability / Selected Source
- Verified Baseline / Closure, when prior proof should constrain the task
- Fixed Core / Allowed Variation / Project Delta, when materially relevant
- Pinned Reference / Fixture / Behavioral Oracle, when it constrains implementation or proof
- Capability-choice freedom retained by the downstream executor, when the source is intentionally not fixed upstream
- Priority / Trade-off Policy
- Decision Rights
- Escalation Conditions

These are not mandatory headings.

They are an execution contract, not a universal ontology.

They do not replace Modeling, Capability Sourcing, Decision Analysis, or Planning.

For production, migration, release, destructive, expensive, irreversible, or high-risk work, make the relevant constraints, authority, capability source, and evidence explicit.

## General-purpose AI → Coding Agent handoff

When this Skill is used by a general-purpose AI to prepare work for a Coding Agent, keep responsibility split:

```text
General-purpose AI
  → understand / model / research / decide
  → compile the minimum sufficient validated task slice

Coding Agent
  → inspect the target code repository
  → implement the requested change
  → run the target repository's required verification
```

Before compiling a task that would create meaningful project-owned code, assets,
systems, workflow, or maintenance, confirm upstream has sufficiently resolved the
problem frame / Ownership Frontier and materially relevant source decision. If not,
delegate the missing modeling / sourcing decision rather than encoding an
implementation-shaped assumption as a coding mandate.

Do **not** automatically instruct the Coding Agent to read this shared Skills repository.

The Coding Agent should normally receive:

- Objective
- Current Problem
- target repository / Source of Truth
- Constraints
- Acceptance Criteria
- Evidence / required proof

It should follow the target repository's own `AGENTS.md`, code, tests, documentation, and local instructions.

Pass methodology or shared Skill material downstream only when:

- this Skill or its source repository is the implementation target;
- the user explicitly requests it;
- a methodology rule cannot be safely represented in the execution contract; or
- the Coding Agent is deliberately being asked to perform upstream modeling rather than implementation.

## Prompt compilation

A prompt is one deployment format for an action.

Before compiling a prompt whose purpose is to create a reusable harness,
workflow, Skill, validator, schema, prompt system, orchestration layer, or other
meta-capability, confirm that its authoring/source decision has already passed
Capability Sourcing. A long prompt is not a substitute for a mature baseline or
repository-local mechanism.

Compile the **minimum sufficient serialization of the validated model slice** relevant to the current action and executor.

When a task touches a recurring/consequential Fixed Core, include the owning
mechanical gate or Human gate when it changes what the executor may modify or
what proof must run. Do not rely on prose alone when the project already has an
enforceable boundary.

Do not:

- compile unresolved ownership or decomposition assumptions into implementation work;
- copy the entire world model into every prompt;
- compile an unverified capability assumption into an implementation mandate;
- compress away a decision-relevant capability surface and leave the downstream executor to choose by native-tool bias;
- preserve information that cannot change judgment, choice, capability sourcing, implementation, boundary, constraints, or acceptance.

When capability-source choice remains open and materially affects the outcome, preserve either the selected source or enough discoverable available means for the downstream executor to choose correctly.

When a valid prior closure materially constrains execution, compile the relevant
baseline/scope and the allowed variation / unresolved delta into the contract.
Do not ask the downstream executor to rediscover or redesign the fixed core unless
the closure is explicitly invalidated.

Adapt instructions to the actual agent, model, tool, repository, runtime, and environment.

If direct execution is possible and delegation adds no value, execute directly.
