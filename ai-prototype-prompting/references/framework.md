# AI Prototype Prompting Framework

## Core Principles

### Intent First

Treat AI prototype tools as semantic translators, not drawing tools. Convert product intent into explicit constraints:

- Replace vague adjectives with physical or behavioral constraints.
- Say who the user is, what they are trying to do, and what must happen next.
- Include the conversion path or completion path.

### Context Complete

Provide the context the generator cannot infer:

- Business domain and scenario
- Target users and accessibility needs
- Existing page structure, screenshots, real field names, and copy
- Platform and component constraints
- Data scale and edge cases

### Design-System Driven

Stabilize output by declaring reusable design primitives:

- Primary and secondary colors
- Typography scale or minimum readable size
- Border radius
- Component library or platform convention
- Icon style
- Spacing density

### Progressive Fidelity

For complex work, do not ask for everything in one pass:

1. Low fidelity: layout, information architecture, and flow.
2. High fidelity: visual treatment and design tokens.
3. Interactive: states, transitions, validation, empty/loading/error handling.

## Input Taxonomy

Ask or infer these dimensions before writing the final prompt:

| Dimension | Include | Purpose |
|---|---|---|
| Business context | industry, user pain, goal, trigger | Determines IA and interaction depth |
| Information architecture | navigation, zones, first-screen priority | Determines visual path and hierarchy |
| Functional components | fields, buttons, states, errors | Prevents incomplete flows |
| Visual system | tokens, library, platform, aesthetic limits | Preserves consistency |
| Technical constraints | framework, screen size, native APIs, accessibility | Keeps output feasible |

## Decomposition Strategy

### By State

Use for forms, publishing flows, onboarding, login, review pages:

- Empty/default
- Partially filled
- Fully valid
- Invalid input
- Loading/submitting
- Success
- Failure with retry
- Permission denied
- Confirmation dialog
- History/list state

### By Flow

Use for multi-screen experiences:

- Entry point
- Task screen
- Confirmation/review
- Result
- Recovery
- Return path

### By Layer

Use when visual quality is unstable:

1. Layout layer: nav, grid, content zones, sticky areas.
2. Content layer: real fields, lists, cards, controls.
3. Detail layer: status, microcopy, spacing, contrast, motion.

## Meta-Prompt Template

```text
You are a senior [domain/product/design role] who is designing for [platform/tool].

Create a [fidelity level] prototype for [page/flow name].

Product context:
- Domain:
- Existing product/page:
- Target users:
- Core user goal:
- Trigger/entry point:
- Success outcome:

Current constraints:
- Existing fields/components:
- Existing navigation:
- Technical/platform constraints:
- Things not to add:

Information architecture:
- Top:
- Main:
- Secondary:
- Bottom/fixed actions:

Required states:
- Default:
- Filled/active:
- Loading:
- Success:
- Failure:
- Empty:
- Permission/validation:

Interaction rules:
- When user clicks [A], [B] happens.
- Disabled states:
- Validation:
- Return/cancel behavior:

Visual system:
- Style:
- Primary color:
- Background:
- Radius:
- Typography:
- Icon style:
- Spacing/density:

Accessibility:
- Minimum touch target:
- Contrast:
- Labels:
- Error feedback:
- Do not rely on color alone.

Output:
- Generate [screens/states].
- Include brief interaction annotations.
- Preserve all existing business fields and logic.
```

## Quality Rubric

Score the prototype prompt or AI output from 1 to 5:

| Dimension | Weight | 5-point standard |
|---|---:|---|
| Instruction following | 30% | All required fields, states, copy, constraints, and business rules are covered |
| Logic robustness | 30% | Happy path, validation, loading, failure, and recovery states are complete |
| Visual quality | 20% | Hierarchy is clear, style is consistent, no clutter or overlap |
| Technical feasibility | 10% | Uses plausible components, platform conventions, and realistic interactions |
| Accessibility | 10% | Large targets, labels, contrast, error feedback, and text status are present |

Use the rubric to revise prompts: missing states usually require decomposition; visual inconsistency usually requires stronger design tokens; business drift usually requires stronger "do not add" constraints.

