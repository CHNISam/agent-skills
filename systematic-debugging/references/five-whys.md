# Five Whys as an optional causal probe

Use this technique for recurring process failures or causal chains that cross several
system boundaries. It is a prompt for evidence, not a requirement to produce exactly five
answers.

Start from one observable failure. For each proposed cause:

1. Ask what evidence shows it produced the previous event.
2. Distinguish a contributing condition from the earliest controllable cause.
3. Stop when another “why” would leave the system's ownership, become speculative, or no
   longer change the corrective action.
4. Prefer a guard at the earliest owned boundary: regression test, invariant check,
   validation, CI gate, or monitoring.

Avoid single-chain storytelling when several independent causes are plausible. Branch the
hypotheses and test them separately.
