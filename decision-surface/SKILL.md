---
name: decision-surface
description: Compress complex analysis into a low-cognitive-load human-facing answer. Use when the work is non-trivial and the user mainly needs the current conclusion, decisive facts, next action, and proof rather than the full reasoning structure. Do not force this format on trivial requests, and do not hide information that materially changes the decision or risk.
---

# Decision Surface

The default human-facing answer is not a reasoning report.

Its purpose is to let the user quickly understand:

1. Where are we?
2. What does it mean?
3. What do we do next?
4. How will we know?

## Default surface

### Bottom Line

Give the most important conclusion first, normally in 1–3 sentences.

### Now

Show only 1–3 facts or state distinctions that materially support the Bottom Line.

Do not retell the investigation.

### Next

State one highest-leverage next action.

If no single action is justified, state the next decision or evidence needed.

If a Capability Gap exists, state the capability decision rather than prematurely naming an implementation.

### Proof

State the observable evidence that will show success or support/falsify the current hypothesis.

## Cognitive budget

Treat user attention as scarce.

Compression must be semantically lossless for the current decision surface:

> Compress language, not decision-relevant distinctions.

Do not remove a layer, relation, assumption, proof type, or boundary merely to
make an explanation shorter when its removal could change the user's
understanding of what failed, what should happen next, or what counts as proof.

When the user asks to see the model itself, prefer the simplest faithful
structure over a shorter but incomplete one.

Do not expose by default:

- full background;
- complete model;
- full solution landscape;
- all alternatives;
- full evidence history;
- detailed methodology;
- every assumption;
- every unknown;
- exhaustive traceability.

Expose deeper material only when it materially changes the decision, risk requires visibility, the user asks, or the top-line conclusion would otherwise be difficult to trust.

## Progressive disclosure

- "Why?" → Evidence / Rationale
- "How did you model it?" → Model
- "What tools/options exist?" → Capability Landscape
- "Why reuse/build this?" → Capability Source Decision
- "What other actions exist?" → Alternatives
- "What don't we know?" → Unknowns
- "Show the full analysis." → Relevant deep structure

Do not repeat the same conclusion under Summary, Conclusion, Recommendation, Next Action, and Final Takeaway.

Explore freely internally. Compress before presenting.
