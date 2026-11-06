---
name: project-modeling
description: Derive project work from goals, outcomes, capabilities, dependencies, milestones/gates, gaps, and evidence. Use for project structure, dependency maps, milestone derivation, scope control, and deciding whether a work item is justified. Do not treat task lists as the fundamental model of the project.
---

# Project Modeling

For project work, derive work through:

```text
Goal
  ↓
Outcome
  ↓
Required Capability
  ↓
[Problem Frame / Ownership Frontier, when materially decision-relevant]
  ↓
[Capability Source / Solution, when materially decision-relevant]
  ↓
Dependency
  ↓
Milestone / Gate
  ↓
Gap
  ↓
Work Item
  ↓
Implementation
  ↓
Evidence
```

Square brackets mean the layer is conditional only when its separate representation
cannot change the current decision, risk, reroute, sourcing choice, or proof.

Keep this distinction explicit:

```text
Need
  ≠
Required Capability
  ≠
Capability Source / Solution
  ≠
Implementation
  ≠
Evidence
```

A Required Capability states what the project must be able to do.

Only after the Required Capability is justified should its source be selected.
Do not jump directly from Capability to Implementation when the capability-source
or solution choice is materially unresolved.

Before compiling meaningful project-owned implementation / asset / workflow work,
verify that the current decomposition and **Ownership Frontier** are sufficiently
justified. If a mature parent-level baseline, reference, or oracle could eliminate
the child work, resolve that frame / sourcing question first.

A technically valid local closure may be **strategically superseded** when a
higher-level baseline or changed ownership boundary makes continued ownership
unnecessary. Preserve useful evidence and contracts; do not preserve implementation
for its own sake.

Tasks are interventions against project Gaps. They are not the fundamental structure of the project.

## Bidirectional traceability and compilation integrity

A current Work Item should normally answer:

- Which Gap does it close?
- Which Dependency or Required Capability does that affect?
- Which Outcome does that support?
- Which Goal does that ultimately serve?
- When it creates material project-owned surface, why is that ownership still
  justified rather than inherited from the current decomposition?

An important Goal / Outcome / Claim should also be able to trace downward to:

- required capability;
- selected capability source / solution where material;
- milestone/gate;
- gap/work;
- evidence owner or closure proof.

When compiling an upstream project model into a release outcome, task, prompt,
or implementation contract, preserve the upstream meaning. If two claims can
fail for different reasons and require different reroutes, keep their judgments
separable even when they share one implementation surface or representative case.

If it cannot, consider:

- Future
- Research
- Nice-to-have
- Remove

rather than Current Work.

## Coordination with other skills

- unclear project reality → `modeling`;
- missing external/project facts → `evidence-acquisition`;
- multiple directions → `decision-analysis`;
- capability source unresolved → `capability-sourcing`;
- execution dependencies after direction selection → `planning`;
- proof of milestone/outcome → `validation`.
