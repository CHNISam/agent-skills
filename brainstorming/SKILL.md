---
name: brainstorming
description: Explore an open-ended product or architecture idea when the user wants help deciding what to build and materially different directions remain. Do not use for routine implementation, localized fixes, or tasks whose outcome and constraints are already actionable.
---

# Product and Architecture Exploration

Use this only when discovery is the task, not as a mandatory prelude to coding.

1. Inspect the relevant product and repository context first.
2. Identify the smallest unresolved decision that blocks a coherent direction.
3. Ask one high-information question at a time when answers depend on the user's goals.
   Prefer concrete options and recommend one.
4. Compare two or three genuinely different approaches only when alternatives exist.
   Explain user impact, cost, reversibility, and risk.
5. Converge on observable intent, constraints, non-goals, and success criteria.
6. Produce a design artifact only if the user asks for one or the decision is broad enough
   that implementation would otherwise lose important context.

Stop exploring once the task is actionable. Do not require section-by-section approval,
a design document, an implementation plan, a worktree, or another Skill for a small
reversible change. If repository discovery resolves the ambiguity, proceed without
interviewing the user.
