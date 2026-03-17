# Quality Bar

## Non-negotiables

- Treat the request as rigorous work. Do not fill gaps with guesses.
- Separate facts confirmed by source material from assumptions that need user confirmation.
- When key behavior is uncertain, ask concise follow-up questions before final export.
- Produce the final workbook only after the critical ambiguities are resolved.

## Coverage standard

At minimum, audit the source material for these surfaces:

- Entry points and role boundaries
- Login, authorization, and permission outcomes
- Happy path for each core flow
- Exception, retry, timeout, and rejection paths
- Empty states and no-data states
- Boundary rules and “only here/only this role” constraints
- Cross-page state carry-over
- Offline or manual operational assumptions
- Explicit red lines from the PRD or prototype

## Omission check

Before exporting, review the drafted rows and ask:

1. Does every visible entry point have at least one case?
2. Does every critical branch have an explicit expected result?
3. Did any source mention a restriction, warning, or prohibition that is still missing?
4. Did any row silently depend on an unstated assumption?
5. Are there duplicate rows that only differ in wording?

## Ambiguity handling

If the user asks for a “最终版” but the source is still ambiguous:

- Draft the deterministic rows.
- List only the minimal unresolved questions.
- Do not silently “hard fix” the uncertain parts.

## Style rules

- Use Chinese UI wording unless the source explicitly requires another language.
- Keep each row focused enough that a tester can execute it without rereading the entire PRD.
- Prefer precise expected results over generic statements like `功能正常`.
