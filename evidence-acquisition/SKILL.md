---
name: evidence-acquisition
description: Retrieve, measure, and qualify real evidence once the relevant observation space is sufficiently understood. Use for research, inspection, measurement, testing, provenance checks, identity/version matching, source conflicts, or precision requirements. If the current search engine, platform, sample, database, telemetry stream, or other frame may materially miss relevant reality, use observability-coverage first. Do not substitute more abstract reasoning for a known Evidence Gap.
---

# Evidence Acquisition

Use this skill for an **Evidence Gap** after the relevant observation frame is sufficiently understood.

If source coverage, sampling frame, platform boundaries, or representation risk could materially change the conclusion, route to **observability-coverage** first.

## Define what evidence would resolve the gap

Before collecting broadly, identify the observation capable of changing the current decision, action, constraint, or acceptance result.

Only add evidence controls that matter:

- Source hierarchy / authority
- Provenance
- Identity matching
- Required precision
- Conflict handling
- Acceptance state
- Stop rule

## Evidence states

Where useful, classify evidence as:

- **Verified** — sufficiently supported for the current purpose.
- **Candidate** — plausible but still needs confirmation.
- **Approximate** — deliberately lower precision than Verified.
- **Conflicting** — credible evidence disagrees.
- **Unresolved** — relevant evidence remains insufficient.

Do not upgrade Candidate or Approximate evidence to Verified for convenience.

Evidence state is scoped to the current claim and intended use.
"Verified" for one population, version, environment, time range, or question does
not automatically transfer to another.

## Claim–evidence fit and credibility

Before using evidence to support an important claim, check only the dimensions
that could change the conclusion:

- exact claim scope;
- target population / system / environment;
- identity and version;
- source / input pedigree and provenance;
- observation coverage and selection effects;
- measurement quality and precision;
- uncertainty and sensitivity;
- transferability from the observed case to the proposed use;
- independence / corroboration when one source family may share the same bias.

Do not let the claim become broader than the evidence.

A representative scenario is a model instantiation or test fixture. It becomes
evidence only when it is executed, observed, measured, inspected, interviewed,
tested, or otherwise grounded through an appropriate channel.

If evidence supports only a narrower statement, narrow the statement or acquire
additional evidence.

## Source of Truth

Prefer reality or an authoritative external artifact:

- actual code or runtime state;
- authoritative database;
- logs;
- measurements;
- test results;
- official documents;
- validated user behavior;
- authoritative external sources.

The agent's model, summary, interpretation, plan, generated document, or previous answer is not automatically a Source of Truth.

## Procedure

1. State the exact evidence need internally.
2. Determine whether suitable traces already exist.
3. If traces exist, retrieve / inspect / query / crawl / fetch them through an appropriate channel.
4. If traces do not exist, measure / instrument / survey / interview / experiment / collect as appropriate.
5. Choose the cheapest sufficiently authoritative observation/source.
6. Verify identity, version, environment, or entity matching when it can change the result.
7. Resolve or expose material source conflicts.
8. Check that the evidence supports only the scope actually observed.
9. Stop when evidence is sufficient for the current purpose.

Do not research indefinitely.

## Exit

Evidence may:

- close the gap;
- contradict the working model;
- expose a new Model Gap;
- create a Decision Gap;
- show that execution can proceed.

Reroute accordingly.
