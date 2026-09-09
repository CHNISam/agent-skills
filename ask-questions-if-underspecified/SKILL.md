---
name: ask-questions-if-underspecified
description: Resolve material ambiguity after repository discovery with the fewest useful questions. Use when remaining uncertainty would change product behavior, scope, architecture, risk, compatibility, destructive actions, or the definition of done; skip for minor reversible choices that project conventions can settle.
---

# Intent and Uncertainty Gate

Ask only when an answer changes a costly direction. The user is authoritative about
product intent; user explanations of technical causes are hypotheses to verify.

## Before asking

1. Normalize the request internally as Goal, Constraints, Done when, and useful
   References. Do not make the user fill a template.
2. Inspect applicable instructions, repository state, configuration, tests, history, and
   existing conventions. Do not ask for facts that can be discovered cheaply.
3. Classify remaining uncertainty:

| Uncertainty | Action |
|---|---|
| None | Proceed. |
| Minor, reversible, low-cost | Follow the existing convention or state a reasonable default and proceed. |
| Material product/scope/architecture/compatibility choice | Ask before dependent implementation. |
| High-risk or hard-to-reverse action | Confirm the exact target and consequence immediately before acting. |
| Open-ended product discovery explicitly requested | Use the optional `brainstorming` skill. |

Read-only discovery may continue while awaiting an answer, but do not commit to a branch
of implementation that depends on it.

## How to ask

- Ask one to three high-information questions in one round when possible.
- Lead with the concrete ambiguity and why it changes the result.
- Offer two or three mutually exclusive choices, put the recommended default first, and
  allow a compact response.
- Use open-ended questions only when the answer space cannot be represented honestly.
- Do not repeat answered questions or seek approval for details the user delegated.

Example:

```text
“Merge the rankings” has one product-level ambiguity:

A. One combined ranking and one UI (recommended)
B. One entry point, but two rankings remain inside
C. Combine data only; keep the current UI

Reply A/B/C. I can continue repository discovery meanwhile.
```

After the answer, restate the resolved outcome in one or two sentences and continue. Stop
asking once Goal, material Constraints, and Done when are actionable.
