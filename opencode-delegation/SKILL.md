---
name: opencode-delegation
description: Delegate bounded implementation, test, refactoring, or maintenance tasks to OpenCode CLI with a verified free model, then independently inspect and accept the result. Use for Codex/OpenCode collaboration and cost-conscious task delegation, including isolated parallel slices.
---

# OpenCode delegation

Use OpenCode's native CLI as the executor. Codex keeps task selection, interfaces, high-risk decisions, integration, and acceptance. Follow the target repository's own instructions, task tracker, branch model, and runtime evidence gates.

## Shape a short task

- Delegate small code fixes, single-module changes, focused tests, mechanical refactors, data checks, or documentation maintenance when an observable acceptance check exists. Do not restrict the executor to prose.
- Flash models can handle substantive code, but long chains need bounded slices. Split by independently verifiable outcome; provide only relevant source paths, interface constraints, examples, and checks. Inspect each slice before continuing.
- Specify goal, writable paths, forbidden changes, acceptance checks, commands, and a concise handoff. Do not ask for broad repository cleanup. Give each writer its own clean worktree; preserve user changes.
- Keep authentication, destructive changes, production writes, publishing, and ambiguous product decisions with the orchestrator unless the user specifically authorizes a suitable delegated slice. Delegation adds no permission to mutate external systems.

## Lock model and cost

1. Inspect `opencode --version`, `opencode run --help`, and `opencode models opencode --verbose`. Extract only the selected model's provider, ID, capabilities, pricing, and variants.
2. Prefer `opencode/deepseek-v4.1-flash-free` when currently available with zero input/output/cache pricing. Use the highest supported reasoning variant; the verified variant was `max`. If variants are absent, omit the flag rather than inventing one.
3. Override only the child process: pin both `model` and `small_model`, restrict `enabled_providers` and the provider's model whitelist, disable sharing, and allow only task-relevant tools/paths. Never rely on the TUI default or persist a task override globally.
4. Parse `opencode debug config` in-process and display only safe fields. Never print auth files, environment secrets, API keys, or raw effective configuration.
5. Free unavailable, nonzero pricing, authentication failure, or 429 means stop that path and report it. Do not silently substitute a paid model/provider. OpenRouter needs user authorization and a specific currently verified free ID; nominal zero pricing on `auto` routers is insufficient.

## Execute and supervise

Use `opencode run --model <locked-model> --format json`, with the supported reasoning flag, an explicit worktree, and separate per-task JSONL/stderr artifacts. See [native CLI details](references/native-cli.md) for the small PowerShell example and permission pitfalls.

- Do not add `--pure` by default: on the observed 1.18.24 setup it returned 403 while ordinary native CLI worked. That is an environment-specific observation, not proof that headless/free usage is unsupported or of the internal cause.
- Set a proportional wall-time budget and inspect progress at tool boundaries. On repeated permission denial, stop and fix the orchestrator's path/config mismatch rather than letting the model try alternate access routes. A process with no events is not evidence of work completed.
- One focused repair round is usually enough. After two unsuccessful attempts at the same slice, stop, preserve the evidence, and let Codex take over or re-scope. Do not launch paid fallbacks or keep retrying identical failures.

## Accept actual work

Inspect JSON tool events and their completed/error states, the final response, exit status, model/variant, and reported cost. Plain text containing tool tags, exit code zero alone, or a self-reported “done” does not establish completion. `reason=length` with no deliverable fails acceptance.

Then inspect file scope and the complete diff; independently run the relevant checks against real production modules. Confirm that acceptance criteria and existing invariants hold. Keep compile/build, artifact import, actual runtime, device interaction, and visual acceptance separate where the project does. Record what was not tested.

Report model/provider, task, actual result, independent verification, and cost evidence. Event cost zero is not a billing-ledger audit; do not claim measured quota savings without a baseline.

## Check the actual yield

Use the existing task notes for a compact record: accepted deliverable, wall time, orchestration/repair attempts, independent review and test outcome, and model tokens/cost when observed. Mark unknown Codex quota usage as unknown. Compare total coordination plus execution plus rework with direct completion; a free call with no usable result is overhead.

Broaden the task class or concurrency only after accepted examples show useful quality and reduced supervisor burden. Repeated startup stalls, permission spirals, fabricated tool use, or expensive review are reasons to fall back and fix the narrow demonstrated harness defect. Keep the business task moving; optional orchestration experiments must not hold it open.

## Bounded concurrency

When the user/project permits it, test two independent CLI sessions with disjoint worktrees, writable paths, artifacts, and task ownership. Never concurrently edit one file, share a mutable build directory, or race the same task-tracker record.

Verify overlapping request intervals, both deliverables, diffs, checks, costs, and absence of rate-limit or interference errors. Do not infer “unlimited parallelism” or “no negative effects” from one trial. Start sequentially if initialization or tool permission handling is not yet reliable; reduce concurrency on contention or 429. Codex integrates accepted slices in the repository's normal order.
