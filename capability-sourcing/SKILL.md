---
name: capability-sourcing
description: Decide how to obtain a required capability before committing to custom implementation. Use when execution needs a capability that is unavailable, unlocated, unevaluated, or has materially different internal/external sources. Consider reuse, standards, libraries, APIs, services, workflows, datasets, models, composition, extension, and custom build. Do not run a large landscape study for trivial commodity choices.
---

# Capability Sourcing

Use this skill for a **Capability Gap**.

Core distinctions:

```text
Need
  ≠
Capability
  ≠
Capability Source
  ≠
Implementation

Capability exists
  ≠
Capability is discoverable / usable by this executor
```

> Source the capability before deciding to build it.

> Capability sourcing begins only after the parent need / outcome is sufficiently
> valid. Do not efficiently source a capability for work that should be reframed,
> replaced, deleted, or deferred.

> Do not let the executor's native modality choose the implementation.

> Establish or reuse the baseline, then build the delta.

> Project ownership is a sourcing decision, not the default result of decomposition.

> Do not silently reopen a still-valid solved capability as free-form implementation choice.

> Meta-capabilities are still capabilities. Harnesses, Skills, validators, schemas,
> prompt systems, orchestration workflows, and agent configurations do not bypass
> this sourcing gate.

## Trigger

Use this skill when sourcing could materially change output quality, quality ceiling, fit for the intended production role, cost, schedule, risk, reliability, maintenance/ownership burden, reproducibility, interoperability, or strategic differentiation.

Use proportional rigor. Do not turn a commodity choice into a research project.

## Capability-surface / existing-capability check

If the requested output is itself a reusable engineering mechanism (for example a
harness, Skill, validator, workflow, schema, prompt framework, or orchestration
layer), first inspect the current repository/runtime mechanism and mature
authoring approaches. Do not assume custom design simply because the requested
artifact is "meta" rather than product code.

First ask whether the capability already exists **and is discoverable to the current executor** in:

- the current project or adjacent modules;
- organizational systems or infrastructure;
- current workflows, automation, or specialist routes;
- installed tools and dependencies;
- existing APIs, datasets, assets, or models;
- repository-local capability maps / routing docs.

For repeated multi-tool domains, prefer one lightweight discoverable routing entry that points to authoritative detailed sources. Do not duplicate full tool documentation.

A capability can exist technically yet be operationally absent when it is hidden in scattered documentation, operator memory, another agent's context, or an unadvertised specialist workflow.

When source choice could materially change the result, inspect enough of the relevant capability surface to avoid omitting an important source class merely because it is outside the executor's native modality.

Prefer extending or composing an existing suitable capability over creating a duplicate.

## Existing solution landscape

When the choice matters, inspect plausible sources:

1. existing internal capability;
2. established standard / protocol;
3. mature library / framework;
4. CLI / SDK / API;
5. managed or external service;
6. existing workflow / automation;
7. existing dataset;
8. existing model;
9. composition of proven capabilities;
10. custom implementation.

Custom Build is neither automatically first nor automatically last.

For consequential sourcing choices, check **solution-space coverage**:

- cover materially different source classes, not only several familiar vendors,
  libraries, or models from the same family;
- include current-state / no-new-capability when the Goal can genuinely be met by
  removing, reframing, or avoiding the need;
- include materially different workflow, service, standard, integration,
  composition, extension, and custom approaches when relevant;
- record why an important source class was pruned when that rationale may matter
  later.

Several vendors in one class are not several fundamentally different solutions.

Before accepting the current decomposition as the sourcing unit, check the
**sourcing altitude**:

- can a mature integrated source satisfy the validated parent capability directly?
- can a higher-level baseline remove several child capabilities from project ownership?
- can a source that is unsuitable as a production dependency still serve safely
  as an Implementation Reference or Behavioral Oracle?
- would lower-level composition create more project-owned integration / maintenance
  than parent-level adoption plus bounded adaptation?

Start at the highest abstraction level that could plausibly satisfy the validated
parent capability, then descend only when fit, quality, licensing, provenance,
compatibility, performance, control, adaptation cost, lock-in, or another material
constraint rules that level out.

This check does not require a prior pattern of repeated sibling failures; it follows
whenever sourcing granularity can materially change the Ownership Frontier or total
unresolved Delta.

Do not blindly prefer the largest solution. Quality, compatibility, licensing,
provenance, performance, lock-in, maintainability, and adaptation cost still
govern fit.

Do not search exhaustively. Stop expanding the landscape when omitted source
classes are unlikely to change the decision at reasonable search cost.

## Maturity and differentiation

Estimate only as precisely as useful whether the capability is closer to:

- Genesis — novel, uncertain, rapidly changing;
- Custom — understood but context-specific;
- Product — commonly solved by established solutions;
- Commodity / Utility — standardized and routinely available.

More commoditized capability creates a stronger reason to reuse/adopt/integrate.

More novel or strategically differentiating capability creates a stronger reason to experiment/customize/build.

This is a bias, not an absolute rule.

Ask:

**Does custom ownership of this capability materially create the outcome or differentiation we care about?**

Even when the differentiating layer is custom, reuse commodity capabilities underneath it where possible.

## Fit-gap

For credible candidates classify requirements as:

- Supported
- Configurable
- Extensible
- Missing
- Incompatible

The important question is:

**How much unresolved task-specific delta remains?**

## Baseline acquisition / reference materialization

When a mature source solves a material portion of the requirement, classify how it should constrain execution:

- **Reusable component** — safe to adopt/integrate under the required production, licensing, provenance, and compatibility envelope.
- **Implementation reference** — inspect real source/structure, but do not necessarily vendor or ship it.
- **Behavioral oracle** — use observable behavior / acceptance as the reference without copying the implementation.
- **Evidence only** — useful for understanding, not a production baseline.

When practical, make the chosen source directly discoverable to the executor through a pinned revision/dependency, repository-local reference pack, executable example, fixture, golden trace, canonical asset, or equivalent artifact.

Then separate:

- **Fixed / proven core** — already solved and not to be redesigned without invalidating evidence.
- **Allowed variation** — intentionally configurable or creative degrees of freedom.
- **Project delta** — unresolved or differentiating work.

A prose instruction such as "make it like X" may still leave the solved problem open. Prefer a concrete baseline or oracle when it materially shrinks rediscovery and drift.

Do not promote study projects, reverse-engineering artifacts, or reference-only sources into production dependencies without checking licensing, provenance, compatibility, maintenance, and production fit.

## Cheap spike

When fit is uncertain and the decision matters, run the cheapest useful representative spike before full integration or custom replacement.

Test only what can change the sourcing decision: installation, representative input, API fit, performance, output quality, observability, deployment, compatibility, or failure behavior.

## Source decision

When multiple materially different sources remain, reroute into a Decision Gap.

Use only criteria that can change the choice:

- fit for purpose;
- quality / production ceiling — whether the source can reach the required fidelity, controllability, and final production role rather than only a prototype or intermediate artifact;
- executor fit — whether the current executor can use it effectively or should route through a different tool, workflow, model, or specialist;
- maturity / project or vendor health;
- time to usable capability;
- adoption and integration cost;
- custom delta;
- maintenance burden;
- total ownership cost;
- reliability;
- observability;
- reproducibility;
- interoperability;
- security / privacy;
- licensing / legal;
- switching cost / lock-in;
- failure surface;
- strategic differentiation;
- opportunity cost.

Possible outcomes:

- Reuse
- Configure
- Adopt
- Integrate
- Compose
- Extend
- Build

Prefer the source producing the best total outcome, not merely the least code, the fewest tool changes, or the closest match to the executor's native modality.

## Existing closure check

Before selecting a new implementation, ask whether the current project already contains a verified, sufficiently scoped baseline for this capability.

If it does and its dependencies / assumptions still hold, reuse or extend that baseline by default. Reopen the solved portion only when new evidence, changed requirements, changed scope, or changed production constraints invalidate it.

## Custom build

Custom implementation can be correct when existing options fail essential requirements or invariants, create unacceptable security/privacy/licensing/lock-in risk, miss required performance/observability/reliability, create excessive integration complexity, cost more over the relevant lifetime, or block strategically important differentiation.

Do not force reuse merely because reuse exists.

## Stop rule

Stop sourcing research when a sufficiently suitable source is established, remaining alternatives are unlikely to change the decision, search cost exceeds expected decision value, a spike gives enough evidence, or custom implementation is demonstrably cheaper and sufficiently safe.

Capability sourcing exists to reduce work, not create analysis paralysis.
