---
name: product-to-spec
description: This skill should be used when the user wants to turn product ideas, PRDs, roadmap items, user stories, or prototype plans into AI-native product iteration workflow artifacts and Agent-Ready Specs for Cursor, Claude Code, Codex, v0, or similar coding agents. It covers roadmap granularity, prototype-first delivery, scope boundaries, API/data contracts, state machines, BDD acceptance criteria, and implementation handoff constraints.
---

# Agent-Ready Spec Workflow

## Purpose

Create AI-native product iteration artifacts that remove ambiguity before code generation. Convert strategy, product ideas, high-fidelity prototype intent, or user stories into a deterministic contract that a coding agent can plan, implement, and verify.

Use this skill to help a full-stack builder, product manager, or independent product owner move from product intent to a structured specification for agentic development.

## Core Principles

1. **Use the right product granularity**
   - Use `Epic` for strategic themes and long-running business outcomes.
   - Use `Feature` for independently releasable product capabilities.
   - Use `User Story` as the daily execution boundary for AI coding agents.
   - Let the coding agent derive implementation `Task` items after the User Story, acceptance criteria, and contracts are clear.

2. **Keep roadmap capacity explicit**
   - Allocate roughly 60-70% to new features.
   - Allocate roughly 20-30% to UX debt and technical debt.
   - Allocate roughly 10-15% to bug fixes.
   - Treat UX debt as strategic product work, not polish. Flag cycles where bug work exceeds 20% as a stability warning.

3. **Put high-fidelity prototypes before detailed specs**
   - Start from the business problem and success metric.
   - Generate or design a high-fidelity prototype before writing a detailed implementation spec when UI behavior is central.
   - Freeze visible UI hierarchy, states, copy, and interaction expectations in the prototype before asking the coding agent to build.
   - Use low-fidelity wireframes only for early brainstorming or macro workflow exploration, not as coding-agent input.

4. **Write specs as contracts, not essays**
   - Define scope, non-goals, data model, API contract, state machine, BDD scenarios, and quantitative non-functional requirements.
   - Remove agent freedom around core architecture, data fields, illegal states, and side effects.
   - Ask a blocking question when the contract lacks required business logic, permissions, data ownership, or state transitions.

5. **Minimize visual noise in diagrams**
   - Use Mermaid or PlantUML only when the graph improves reasoning.
   - Keep diagrams monochrome and style-free.
   - Avoid icons, colors, gradients, custom CSS, complex layout directives, or decorative styling in diagrams meant for LLM parsing.

## Workflow

### 1. Classify The Work Item

Determine whether the user's request is an `Epic`, `Feature`, `User Story`, or `Task`.

- If the request is strategic or spans many iterations, produce an Epic or Feature breakdown.
- If the request is ready for implementation, force it into one or more User Stories.
- If the user provides only technical tasks, recover the missing user value and acceptance boundary before writing the spec.

### 2. Establish Roadmap And Capacity Context

When prioritization or scheduling is involved:

- Tag work as `feature`, `ux-debt`, `tech-debt`, or `bug`.
- State which capacity lane it belongs to.
- Identify whether the item should appear on a public roadmap, operational roadmap, sprint board, or bug queue.
- Call out hidden UX debt or technical debt created by the requested feature.

### 3. Require Prototype Clarity For UI Work

For UI-heavy work:

- Ask for existing screenshots, product pages, design system rules, or prototype files when available.
- If no high-fidelity prototype exists, produce a prototype-generation prompt first.
- Cover visible states: empty, loading, populated, validation error, permission denied, success, failure, and return path.
- Do not let a coding agent infer visual hierarchy, component states, or interaction feedback from a vague wireframe.

### 4. Produce An Agent-Ready Spec

Use the template in `references/agent-ready-spec-template.md`.

Include:

- Agent directives and source-of-truth rules.
- Business value and user value.
- In-scope and out-of-scope boundaries.
- Technical constraints and quantitative NFRs.
- Entity schema and API contracts.
- State diagram and transition matrix.
- BDD acceptance criteria.
- Test and verification expectations.

### 5. Add Contract Checks Before Implementation

Before handing off to a coding agent, verify:

- Every API field used by the UI exists in the contract.
- Every entity status has legal transitions and illegal transitions are explicit.
- Every non-goal blocks a common overbuild path.
- Every vague quality requirement has a numeric threshold or a verifiable check.
- Every BDD scenario maps to either an E2E, unit, integration, or contract test.

## Output Modes

Choose the smallest useful output:

- **Roadmap decomposition**: Epic -> Feature -> User Story with labels and capacity lane.
- **Prototype prompt**: High-fidelity prompt for UI prototype tools, including states and visual constraints.
- **Agent-Ready Spec**: Full Markdown contract for coding agents.
- **Spec review**: Findings-first critique of an existing PRD/spec for ambiguity, hallucination risk, missing contracts, and untestable acceptance criteria.

## References

Read only what is needed:

- `references/agent-ready-spec-template.md`: full reusable spec template for product iteration handoff to AI coding agents.
