---
name: ai-prototype-prompting
description: Create high-quality prompts for AI prototype tools such as Google Stitch, Figma AI, Claude Artifacts, v0, Uizard, and similar generators. Use when the user wants to generate, improve, critique, or systematize prototype prompts; convert PRD/user stories/screenshots/current product context into prototype-generation instructions; define page states, flows, visual constraints, accessibility requirements, or quality scoring for AI-generated UI prototypes.
---

# AI Prototype Prompting

## Goal

Turn vague product intent into a structured, tool-ready prototype prompt that preserves business logic, current product context, visual constraints, interaction states, and evaluation criteria.

## Workflow

1. **Anchor in real context**
   - Inspect provided screenshots, files, PRDs, user stories, routes, components, and existing product docs when available.
   - Reuse real field names, page names, tab names, copy, statuses, validation rules, and platform constraints.
   - If the user asks for Google Stitch or another visual prototype tool, output a paste-ready prompt.

2. **Clarify only blocking gaps**
   - Make a reasonable assumption when the missing detail is low risk.
   - Ask before inventing business rules, target users, brand constraints, or major flows when the source context cannot answer them.

3. **Decompose before prompting**
   - Define the target user, scenario, core task, and happy path.
   - Split complex pages by state: empty, filled, loading, success, failure, permission denied, validation error, confirmation, and return path.
   - Split complex flows by screen: entry, task execution, review/confirmation, result, history/list, detail.

4. **Write deterministic prototype instructions**
   - Prefer concrete language over vague aesthetics.
   - Include information architecture, component hierarchy, field-level requirements, visual tokens, accessibility constraints, and interaction feedback.
   - Explicitly say what not to add when product/technical scope is constrained.

5. **Add quality gates**
   - Include a short checklist or scoring rubric when useful.
   - Require the generated prototype to preserve business logic, cover critical states, avoid visual clutter, and remain technically plausible.

## Prompt Structure

Use this order unless the user asks for a different format:

1. Product background
2. Current page or flow context
3. Problem statement
4. Target users and user stories
5. Design goals
6. Required screens or states
7. Information architecture and component requirements
8. Interaction rules and validation states
9. Visual style and design-token constraints
10. Accessibility requirements
11. Negative constraints
12. Requested output format
13. Quality checklist

## Tool-Specific Guidance

- **Google Stitch / Figma AI / Uizard**: describe mobile screens, visible hierarchy, states, and interaction notes. Avoid implementation code.
- **v0 / Claude Artifacts / code-first tools**: include framework, UI library, layout constraints, mock data, responsive behavior, and component states.
- **WeChat Mini Program prototypes**: mention WeChat Mini Program conventions, TDesign/WeUI/Vant if relevant, tabbar/navigation behavior, native capabilities such as `chooseAvatar`, `nickname`, `chooseMedia`, and `getLocation`.

## Standards

- Avoid generic claims such as "beautiful", "modern", or "easy to use" unless paired with concrete constraints.
- Do not introduce new login methods, fields, pages, or permissions that conflict with existing product scope.
- For older adults and disabled users, require larger touch targets, clear text labels, high contrast, stable layout, visible feedback, and text-based status labels.
- For status labels, never rely on color alone.
- For mobile prototypes, keep the first screen focused on the user's core task, not a marketing hero.

## References

Read only what is needed:

- `references/framework.md`: full reusable prompt framework, decomposition strategy, and AI prototype quality rubric.
- `references/page-patterns.md`: page-type templates for dashboards, forms, onboarding/login, feeds, and mobile mini-program pages.

