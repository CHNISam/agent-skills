---
name: modeling
description: Build or attack a minimum sufficient model when the relevant reality is not understood well enough to predict, decide, act, or verify. Use for ambiguous goals, missing causal structure, unclear boundaries/states/relations, hidden assumptions, or model-quality testing. Do not use merely because a task is complex if the missing evidence or action is already known.
---

# Modeling

Use this skill for a **Model Gap**.

## Purpose first

For non-trivial work, do not assume the requested task / feature / requirement /
component is itself necessary just because it is clearly stated.

Determine only what can change the current work:

- Goal — intended real-world state.
- Current Question — what must be understood, chosen, changed, or verified now.
- Success — observable resolution.
- Necessity — whether the proposed work must exist to reach the Goal, or should be
  kept, reframed, replaced, deleted, or deferred.

When materially relevant, also distinguish Outcome Owner, Decision Owner, Risk Owner, and Priority / Trade-off Policy.

Do not automatically treat the user's proposed feature, task, implementation, workflow, technology, library, service, or terminology as the real Goal.

Before moving from Why to How, ask whether the proposed work is the problem, a
symptom, an inherited means, or one local expression of a higher-level need. If
removing or replacing it still satisfies the Goal better, reroute before
implementation.

Use Five Whys or another causal method only when the missing understanding is a
causal chain. "Why before How" is a necessity / problem-framing rule, not a
requirement to ask exactly five questions.

## Revalidate the problem frame / ownership boundary

A clear parent need can still be represented at the wrong level.

Use this check when the next action would create meaningful project-owned code,
assets, systems, workflow, or maintenance; when a backlog / prompt already presents
implementation-shaped child work; when repeated local closures are not moving the
parent Outcome enough; or when a stronger parent-level baseline could subsume
several child capabilities.

Ask:

- If the current implementation and task tree disappeared, what parent capability
  or Outcome would remain?
- Which parts of the decomposition are requirements versus inherited solution choices?
- If that parent capability already existed at the required production quality,
  what project-specific Delta would still remain?
- Which capability genuinely justifies project ownership because of differentiation,
  required control, or strategic learning?
- What highest sufficiently fitting reusable baseline, reference, Behavioral Oracle,
  platform, service, or composition could move the ownership boundary upward?

Treat the boundary between intentionally owned capability and consumed / adapted /
referenced capability as the **Ownership Frontier**.

The production-quality hypothetical above is a **Ceiling-Baseline Counterfactual**.
It is a framing operator, not evidence and not permission to copy protected
implementation. Its purpose is to break fixation on the incumbent decomposition
and expose the smallest plausible Project Delta.

If the frame changes, impact-analyze downstream work. A technically valid local
closure can become strategically superseded without becoming false.

## Select the model for the intended use

Before building an important model, determine what the model must support:

- question / decision / action / prediction / proof;
- relevant boundary, population, environment, version, or time horizon;
- required fidelity, precision, and uncertainty;
- materially different semantic layers that must remain visible.

Choose the minimum sufficient model kind / schema for that use.

Do not force a project hierarchy onto a decision problem, a causal model onto a
pure retrieval problem, or an architecture schema onto a user-research question
merely because the schema is familiar.

For a complex cross-layer model, make the semantic spine explicit enough that
missing decision-relevant layers are detectable. Once selected, do not silently
drop such a layer; if it is merged or omitted, know why doing so cannot change
the decision, reroute, sourcing choice, risk, or proof.

When auditing an **existing layered model or derivation chain**, validate the
current layer and its decision-relevant relation to the next layer before treating
deeper downstream structure as accepted. Inspect downstream material when useful
to test consistency, but do not prematurely elaborate, compile, or rely on it as
though its upstream derivation had already passed.

Where a mature domain method, standard, framework, or model kind is likely to
exist and the choice matters, source and tailor it before inventing a new one.

Treat important model PASS results as scoped to an intended-use envelope:
included boundary/population/environment/version, exclusions, assumptions,
evidence basis, and material uncertainty. Reassess model fit when the proposed
use materially exceeds that envelope.

## Build the minimum sufficient model

Preserve distinctions capable of changing a relevant prediction, decision, action, capability source, constraint, or acceptance result.

Possible dimensions:

- Boundary
- Entities
- State
- Relations
- Dynamics
- Causality
- Dependencies
- Capabilities
- Constraints / Invariants
- Time
- Actions / Inputs
- Authority / Agency
- Observations / Outputs
- Uncertainty

These are tools, not mandatory headings.

Preserve any materially different layer or relation that can change a prediction,
decision, action, reroute, capability-source choice, risk, or acceptance result.
Simplify wording, not semantics.

When relation meaning matters, type it explicitly enough to avoid collapse.
Useful generic meanings include derives-from, requires, provided-by, depends-on,
closes, verifies, and validates. These labels are illustrative rather than a
mandatory ontology.

Do not create information merely because a schema contains a field.

## Optional operators

Use only when triggered.

### First Principles

Use when a convention, inherited solution, or terminology may be mistaken for the requirement.

Ask what fundamentally must be true, what outcome matters, which constraints are conventions, and what requirement would remain if the current implementation disappeared.

### Inversion

Use when failure, reliability, regressions, omissions, or hidden failure modes matter.

Ask: **What would make this definitely fail?**

Work backward to causes, missing states, violated invariants, unsafe assumptions, guards, and required evidence.

### Stress Thinking

Use when scale, boundaries, resources, missing data, concurrency, accuracy, or failure cost may hide structural weakness.

Ask: **What breaks first?**

Use another established method when it is better suited.

## Attack important models

Apply rigor proportional to consequence, uncertainty, novelty, irreversibility, cost, and complexity.

- **Scenario / Run Test** — instantiate a representative concrete case, run it to a concrete result, then trace the important result back to the abstract model. For important cross-layer models distinguish Abstract Pass, Scenario Pass, and Reverse Pass. A scenario is an instantiation / test fixture, not evidence by itself; evidence begins when the scenario is executed, observed, measured, inspected, or otherwise grounded in reality.
- **Separation Test** — can the model distinguish cases that should differ?
- **Counterfactual Test** — if one important condition changes, what should change and remain unchanged?
- **Coverage Test** — check decision-relevant boundaries, exceptions, and failure modes.
- **Grounding Test** — connect important claims to code, data, documents, logs, measurements, behavior, tests, observations, or authoritative sources.
- **Falsification Test** — what evidence would make the model wrong?
- **Generalization Test** — test a materially different or off-nominal case where practical.
- **Bidirectional Traceability Test** — why does each important element exist, and what downstream realization/evidence closes or proves it?
- **Ablation Test** — if an element were removed, could any relevant result change?
- **Typed-Relation / Layer-Preservation Test** — do not flatten materially different meanings such as requirement, capability, solution, implementation, verification, or validation into one arrow.
- **Compilation Integrity Test** — when the model becomes a milestone, plan, task, prompt, or contract, does the downstream form preserve upstream semantics and separable failure modes?
- **Proof-Type Test** — distinguish model structure coherence, implementation verification, real-world validation, and unknown/untested evidence where materially relevant.
- **Change-Impact / Revalidation Test** — after a decision-relevant upstream change, identify affected dependents and revalidate only the affected scope before relying on prior PASS.
- **Claim–Evidence / Model-Use Fit Test** — confirm that evidence supports the actual claim scope and that the model is being used within the population, environment, version, assumptions, and intended-use envelope for which it is sufficiently supported.

## Exit

Stop modeling when the current model is sufficiently trustworthy for the current purpose.

If the exact missing observation is now known, reroute to **evidence-acquisition**.

If several materially different interventions remain, reroute to **decision-analysis**.

If the intervention is known but a capability is missing, reroute to **capability-sourcing**.
