# From Clean UX to Professional Product Craft

> 本文为原文全文，逐字保留，不得精简或改写。skill 的操作指引见 ../SKILL.md。

A screen can be usable, accessible, and free of obvious interaction defects yet still fail to feel like a product shaped by a mature commercial team. The reason is that users judge more than task success: they form aesthetic impressions extremely quickly, prefer pages that are easier to classify and parse, infer credibility from design quality, and then interpret tone, interaction quality, and visual consistency as signals of professionalism. Research summarized by Gitte Lindgaard[1] and later first-impression studies shows that people can form stable attractiveness judgments of websites within very brief exposures, and interfaces with lower visual complexity and higher prototypicality are judged as more appealing. [2]

That pattern is visible in mature design systems as well. Across urlApple Human Interface Guidelinesturn1search4, urlMaterial Design 3turn1search13, urlFluent 2turn2search3, urlCarbon Design Systemturn1search31, urlAtlassian Design Systemturn3search16, urlAnt Designturn3search3, urlGOV.UK Design Systemturn5search19, and , “polish” is treated as a system problem: typography, spacing, color roles, shape, elevation, iconography, motion, and content presentation are defined as reusable rules or tokens rather than solved ad hoc screen by screen. [3]

## Why polished UX can still feel unfinished

A basic UX checklist answers questions like “Can users complete the task?”, “Can they recover from errors?”, and “Is the interface accessible enough to operate?” Those are essential, but they do not answer the questions that create a professional feel: “Does the page explain itself at a glance?”, “Does it look like the right kind of product for this category?”, “Does it signal trust and care?”, and “Do all the visual details feel like they came from one coherent system?” First-impression research, the aesthetic-usability effect, and credibility research all show that these judgments alter perceived usability, trust, and willingness to engage. [4]

In practice, “差点意思” usually means that the product has cleared the floor but not reached the ceiling. It has removed obvious mistakes, but it has not yet created a strong visual hierarchy, a disciplined spatial rhythm, a recognizable shape and color language, or a brand-consistent interaction tone. Research from the urlNielsen Norman Grouphttps://www.nngroup.com also shows that tone of voice and interaction design change perceptions of friendliness, trustworthiness, desirability, and brand. So the missing layer is not just “better visuals”; it is the combination of perception, system coherence, and behavioral finish. [5]

A useful working definition is this: a product feels “professional” when it combines low unnecessary visual complexity, high familiarity with the correct platform or category patterns, strong internal consistency, trustworthy content presentation, and restrained but deliberate interaction feedback. That is why the difference between a merely usable page and a polished one is often not one dramatic redesign, but dozens of quiet decisions that all point in the same direction. [6]

## A framework for diagnosing “almost there”

The most reusable diagnosis framework is to treat “almost there” as seven distinct gaps.

Perception gap — The page is understandable after inspection, but not legible at first glance. Users cannot quickly infer what the page is, what it is for, or which action matters most. This often comes from excess visual complexity, weak focal hierarchy, or a layout that does not look sufficiently like the category it belongs to. [7]

Rhythm gap — Spacing is technically acceptable but visually arbitrary. Related things are too far apart; unrelated things are too close together; every gap is slightly different; density changes from block to block without intent. Mature systems explicitly encode spacing ramps because spatial rhythm is one of the main ways interfaces communicate relationships. [8]

Hierarchy gap — Everything speaks at the same volume. Headings, labels, secondary metadata, cards, badges, tabs, and CTAs all compete, so the page has no strong reading order. Visual hierarchy is built through scale, contrast, spacing, and placement, not through adding more boxes or colors. [9]

Surface gap — The page uses cards, shadows, borders, radii, and fills, but not semantically. Surfaces feel decorative rather than meaningful, so the UI looks cheap or template-like. Official systems treat elevation, materials, color roles, card types, and shape as structured signals for depth and emphasis rather than ornamental effects. [10]

Language gap — The type, icons, and copy do not share one voice. Typography lacks a clear editorial hierarchy, icon styles are mixed, and microcopy sounds generic or inconsistent with the desired brand. Tone of voice and interaction details materially affect brand perception, so this gap is often what makes a product feel “not premium” even when layouts are competent. [11]

Behavior gap — The page works, but it does not react with precision. Hover, pressed, selected, loading, success, and error states either feel abrupt, too subtle, or visually disconnected from the base component. Motion is one of the places where polished products signal causality, responsiveness, and confidence. [12]

System gap — Each screen is locally fine, but the product does not feel globally unified. One page uses one shadow, another page uses a different radius, a third page uses a third spacing pattern. Design systems and token systems exist precisely to prevent this kind of gradual drift by turning “taste” into repeatable standards. [13]

## UI Craft and visual polish checklist

This checklist is intentionally separate from UX QA. It assumes the screen already works. Its purpose is to ask whether the screen feels deliberate, coherent, and commercially polished. Each item below is written so that a PM, designer, or AI agent can turn it into concrete edits. [14]

First impression and focal point — Inspect whether someone can tell the page purpose, the object being worked on, and the primary next action after a 5-second view. Typical failure: the page reads as a wall of equivalent modules. Modify by promoting one dominant zone and reducing the prominence of secondary blocks. Accept when reviewers consistently identify the page purpose and main CTA in a quick-glance test. [15]

Composition and balance — Blur or squint at the page. The silhouette should still show a clear reading path and a stable balance of large, medium, and small masses. Typical failure: checkerboard layouts, excessive equal-width cards, or a screen that feels either top-heavy or centerless. Modify by establishing a primary axis, limiting competing blocks, and intentionally balancing visual weight. Accept when the blurred view still reveals the intended hierarchy. [9]

Spatial rhythm and density — Check whether spacing values map to a small, deliberate set of distances rather than one-off numbers. Typical failure: 18px here, 22px there, 14px elsewhere, creating a “nearly aligned” feeling. Modify by remapping spacing to a 4px or 8px-based token ramp and choosing a page density mode rather than mixing compact and airy blocks arbitrarily. Accept when most spacing values can be named by token and section density feels intentional. [16]

White space and grouping — Check whether related elements are perceptually grouped by proximity and whether unrelated groups have enough separation. Typical failure: PMs add extra cards or dividers because grouping is weak, when the real problem is spacing. Modify by moving headings closer to subordinate content, increasing separation between chunks, and using containers only when whitespace alone is not enough. Accept when group boundaries are obvious without extra chrome. [17]

Typography hierarchy — Inspect whether the page uses a disciplined type system with clear semantic roles. Typical failure: too many font sizes, too many weights, or body text that competes with labels and metadata. Modify by assigning each text element to a role, reducing visible styles, and using size and weight to signal importance rather than compensating with color. Accept when the page can be read in order without careful parsing. [18]

Vertical rhythm and line length — Inspect paragraph width, line height, and how text blocks stack vertically. Typical failure: desktop text runs too wide, mobile text crams too tightly, or headings float without enough supporting rhythm. Modify by constraining main text columns and calibrating line height to the type scale. Accept when long-form text stays roughly within the 60–80 character guidance, or around the GOV.UK ceiling of about 75 characters per line, and the page remains scannable at zoom. [19]

Content packaging — Inspect whether information is presented as meaningful chunks rather than as raw fields, sentences, and badges. Typical failure: everything is correct, but nothing is editorialized. Modify by grouping metadata, promoting the one or two facts that matter most, turning long explanations into stacked chunks, and separating core from secondary data. Accept when a user can skim the page and still understand its structure. [20]

Color-role discipline — Check whether color is assigned by role and emphasis, not by local taste. Typical failure: brand color appears in too many places, semantic colors are reused as decoration, or text contrast tiers are inconsistent. Modify by mapping UI colors to a role system such as primary, secondary, container, surface, success, warning, danger, and info. Accept when color explains emphasis and meaning at a glance rather than merely adding decoration. [21]

Surface depth and card treatment — Inspect how many simultaneous surface types are used and why. Typical failure: every block is wrapped in an outlined card with a different radius or shadow, creating fake structure. Modify by choosing a small repertoire of surfaces, for example plain background, outlined container, and elevated container, and using each for a clear reason. Accept when cards only group a single subject or decision area and depth levels are easy to explain. [22]

Shape language — Inspect whether buttons, cards, inputs, pills, and dialogs share a coherent corner-radius and stroke logic. Typical failure: mixed roundedness that makes the UI feel assembled from multiple kits. Modify by defining one corner system and one stroke strategy per family of components. Accept when a screenshot can be recognized as one product even after blacking out the text. [23]

Iconography — Check whether all icons belong to one family with consistent weight, metaphor style, and fill/outline logic. Typical failure: mixing line icons, filled icons, emoji-like symbols, and third-party illustrations in the same viewport. Modify by standardizing on one icon family, aligning icon size to text size, and adding labels when meaning may be ambiguous. Accept when icons support comprehension without becoming decorative clutter. [24]

Component consistency — Inspect whether repeated patterns stay repeated. Typical failure: one table toolbar has 12px internal padding, another has 16px; one filter chip uses pill corners, another uses rounded rectangles; one primary button is tonal, another fully filled. Modify by collapsing local variations into approved component variants and documenting the rule. Accept when similar tasks use the same component anatomy and state treatment across screens. [25]

State polish and interaction feedback — Check hover, focus, pressed, selected, disabled, loading, success, warning, and error states. Typical failure: the resting component looks designed, but the states look default, abrupt, or incomplete. Modify by ensuring every important component has a complete visual state set and that state changes preserve the same visual language as the resting component. Accept when interaction feels continuous rather than patched together. [26]

Motion and wait experience — Inspect whether motion reinforces cause and effect or merely adds flair. Typical failure: ornamental animation delays the task, or loading states say only “something is happening” without preserving context. Modify by using subtle microinteraction feedback, starting causality-relevant animation within about 0.1 seconds of the trigger, and matching wait-state patterns to duration. Accept when loading under a few seconds uses light contextual indicators, longer waits use more explicit progress, and repeated animation never feels like a roadblock. [27]

Brand voice and trust signals — Check whether copy, metadata, status labels, and interaction tone express the intended brand adjectives, such as precise, calm, capable, or premium. Typical failure: the visual design says “serious,” while the copy sounds generic; or the product looks modern but its timestamps, states, and disclosures feel thin or outdated. Modify by aligning microcopy tone, surfacing current and relevant context, and removing filler language. Accept when the overall screen evokes the target adjectives and strengthens trust rather than merely avoiding error. [28]

Pixel finish and implementation QA — Inspect alignment, baseline consistency, clipping, truncation, icon centering, border sharpness, responsive behavior, and theme parity. Typical failure: handcrafted design intent gets lost in implementation, creating tiny “cheapness” cues. Modify by running visual QA at key breakpoints and states, not just the default screenshot. Accept when there are no visible one-off misalignments, broken edge cases, or token violations in the final build. [29]

## A PM workflow for converting taste into tasks

The most effective workflow is not “make it prettier.” It is a constrained refinement pipeline that keeps business logic still while raising visual craft.

Freeze scope first — Before talking about aesthetics, explicitly lock the information architecture, task flow, field list, permissions, business rules, and analytics behavior. Visual polish work should begin with a statement of non-goals, or the task will drift into unintended redesign. This is especially important when using reusable component systems and tokens as the source of truth. [13]

Diagnose the page with evidence — Capture the real page at the relevant breakpoints and states, then run three rapid diagnostics: a 5-second impression test, a blur or squint test for hierarchy, and a component-token inventory. The output should not be “looks messy”; it should be “primary action not obvious in 5 seconds,” “grouping collapses in blur view,” or “page uses seven different vertical gaps.” [30]

Classify issues by craft bucket — Tag each issue using the diagnosis framework above: perception, rhythm, hierarchy, surface, language, behavior, or system. This matters because different feelings lead to different fixes. A hierarchy issue is solved with scale and spacing; a surface issue is solved with container logic and depth; a behavior issue is solved with states and motion. [31]

Collect the right benchmarks — Benchmark against products with the same job-to-be-done, the same information density, and the same platform conventions. A B2B admin list page should not be benchmarked against a marketing landing page. Prototypicality research implies that users respond better when a product is recognizable as the right kind of product, not merely “beautiful in the abstract.” Use platform references from systems like urlApple Human Interface Guidelinesturn1search4, urlMaterial Design 3turn1search13, urlFluent 2turn2search3, urlAnt Designturn3search3, and to keep the benchmark set native to the medium. [32]

Write a visual direction statement — Reduce the subjective feeling into one sentence of intent. For example: “Make this page feel calmer, more trustworthy, and more enterprise-grade by reducing visual noise, strengthening type hierarchy, and using one surface system.” This step is important because it converts “差点意思” into target adjectives and a bounded improvement direction. Desirability and tone-of-voice research both support using explicit adjectives rather than vague taste language. [33]

Translate direction into delta edits — Every proposed change should be written as before → after, tied to a component or token. Example: “Section headers 20/28 semibold → 16/24 semibold; section gap 20 → token space.300; secondary cards outlined → plain sections with only one elevated summary card; mixed icons → one outline family.” This prevents polish work from becoming an uncontrolled redesign. [34]

Validate with fast visual checks — After the update, rerun the 5-second test, a light desirability study, and, when relevant, a first-click check on the critical task. Visual refinement should improve first impression and brand fit without hurting findability or task success. [35]

When handing work to an AI agent, the key is to ask for a constrained delta plan, not a redesign. The agent should be instructed to preserve structure and business logic, diagnose by craft dimension, propose token-level changes, and explain why each change improves hierarchy, consistency, or trust. That kind of structure makes AI much less likely to improvise new features or rewire flows. [36]

## A task template for AI agents and designers

A good task brief turns a subjective complaint into a bounded production spec. Use this structure.

·       Page context — Page name, user type, core task, device class, and key breakpoints.
·       Business goal — The workflow this page must support and the metric that must not regress.
·       Target adjectives — Three to five words such as trustworthy, sharp, calm, expert, modern, premium, efficient.
·       Frozen constraints — Do not change IA, step count, field list, navigation model, permissions, business rules, analytics events, API behavior, or core copy meaning.
·       Diagnosed craft issues — List the top five issues using the diagnosis framework, for example “weak focal hierarchy,” “mixed surface treatments,” “random spacing,” “generic iconography,” “loading state feels default.”
·       Benchmark set — Two or three reference pages from the same category and platform, plus the house system or token library to follow.
·       Allowed visual levers — Spacing, alignment, typography, color roles, icon family, radius, stroke, elevation, content chunking, state styling, loading placeholders, and subtle motion.
·       Required deliverables — Annotated diagnosis, before → after change list, exact token/value edits, updated mock or implementation diff, and a self-check against acceptance criteria.
·       Non-goals — No new features, no new info architecture, no added steps, no hidden controls, no change to decision logic.
·       Acceptance checks — Must pass the 5-second test, preserve first-click performance, map to approved tokens, and show no functional regression.

A reusable instruction can read like this:

“Refine the attached page for visual craft only. Preserve current structure, flow, business logic, and content meaning. Do not add or remove features, steps, fields, or actions. Diagnose the page using the craft checklist. Then propose only visual refinements to spacing, hierarchy, typography, color roles, surfaces, iconography, state styling, perceived performance, and motion. Output all changes as before → after deltas with rationale, token references, and acceptance checks.”

This works best when the team already has a token system or documented component rules, because tokens are the bridge between PM intent, design decisions, and implementation constraints. Official systems describe tokens precisely as the mechanism for storing design decisions and keeping design and code consistent. [37]

## Acceptance criteria for visual refinement

Visual polish should be accepted the same way functional work is accepted: with explicit criteria before work starts and explicit evidence after it lands.

### Before optimization

·       Scope freeze exists — The brief explicitly states what may not change.
·       Baseline captures exist — Desktop, tablet, mobile, empty, loading, error, and dense-data states are all captured before edits.
·       Current craft diagnosis exists — The team has a written issue list by craft bucket, not just a general feeling.
·       Benchmark references are chosen — Two to three same-category references plus one house system.
·       Baseline impression data exists — Even lightweight data is enough: two or three internal 5-second reactions, a primary CTA identification check, and a short adjective list describing the current feel. [38]

### After optimization

·       No functional regression — Same IA, same steps, same fields, same business outcomes.
·       Purpose and primary action are obvious fast — In an internal 5-second test, most reviewers can state what the page is and what to do next. [39]
·       Adjective profile shifts in the intended direction — A shortened reaction-word list based on the method introduced by Joey Benedek[40] and Trish Miner[41] should move away from words like busy, generic, cluttered, cheap, or confusing and toward words like trustworthy, capable, focused, elegant, or clear. [42]
·       First-click performance does not get worse — If the page has a single critical task, the polished version should preserve or improve initial click accuracy. [38]
·       Token compliance is high — Spacing, colors, type, stroke, radius, and elevation all map to approved tokens except for explicitly justified exceptions. [43]
·       State coverage is complete — Hover, focus, pressed, selected, disabled, loading, success, warning, and error states are visually defined where applicable. [44]
·       Motion is useful, not ornamental — Interaction motion starts quickly enough to preserve causality and does not slow repeated tasks. [45]
·       Wait states match duration — Actions taking more than about a second show visible progress; long waits use explicit duration cues rather than endless spinners. [46]
·       Responsive and theme QA passes — No alignment drift, truncation, contrast collapse, or state inconsistency across breakpoints and themes. [47]

## Cross-platform guidance for mini programs, admin consoles, and mobile apps

The same craft checklist works across surfaces, but the weighting changes by medium. Platform-native polish matters because users partly judge interfaces by familiarity and fit with expected patterns, not by novelty alone. [48]

### Mini programs

For mini programs, bias strongly toward single-column clarity, obvious task chunks, restrained surface layering, and fast perceived performance. The official Tencent guidance provides WeUI as a baseline style library specifically to ensure a more consistent experience, which is a strong signal that mini-program polish should come from disciplined reuse rather than custom ornamental styling. Use fewer visual levels than you would on desktop, keep the primary action unmistakable, and make loading states contextual rather than flashy. [49]

### Web admin backends

For web admin products, density is not the enemy; undisciplined density is. This is where spacing scales, grid systems, list/detail/table templates, and restrained color usage matter most. urlAnt Designturn3search3 explicitly grounds enterprise layouts in an 8-based grid and proximity rules, while urlAtlassian Design Systemturn3search16 and urlCarbon Design Systemturn1search31 define spacing and type as system foundations. The right goal for admin screens is “dense but breathable,” with a visible reading path, one dominant action area, and strongly packaged secondary metadata. [50]

### Mobile pages

For mobile pages, polish usually comes from ruthless emphasis: one dominant task, two or three effective text levels per screen, native-feeling iconography, and motion that clarifies transitions rather than decorating them. The official guidance from urlApple Human Interface Guidelinesturn1search4, urlMaterial Design 3turn1search13, and urlFluent 2turn2search3 all treat typography, color roles, shape, icons, layout, and motion as core parts of product quality. On mobile, the fastest way to lose the “professional” feel is to let too many elements compete in a small viewport. [51]

The most general method, across all three surfaces, is simple: keep basic UX as the floor, diagnose polish problems through perception, rhythm, hierarchy, surface, language, behavior, and system coherence, then assign only constrained craft edits that preserve the workflow and business logic. When a team does that consistently, “差点意思” stops being a vague taste complaint and becomes a repeatable product-improvement practice. [52]

## References

[1] [42] https://www.nngroup.com/articles/microsoft-desirability-toolkit/
https://www.nngroup.com/articles/microsoft-desirability-toolkit/
[2] [6] [7] [32] [48] https://research.google.com/pubs/archive/38315.pdf
https://research.google.com/pubs/archive/38315.pdf
[3] [18] [51] Typography | Apple Developer Documentation
https://developer.apple.com/design/human-interface-guidelines/typography?utm_source=chatgpt.com
[4] https://www.nngroup.com/articles/aesthetic-usability-effect/
https://www.nngroup.com/articles/aesthetic-usability-effect/
[5] [33] https://www.nngroup.com/articles/tone-voice-users/
https://www.nngroup.com/articles/tone-voice-users/
[8] [17] https://www.nngroup.com/articles/form-design-white-space/
https://www.nngroup.com/articles/form-design-white-space/
[9] [31] https://www.nngroup.com/articles/principles-visual-design/
https://www.nngroup.com/articles/principles-visual-design/
[10] Materials | Apple Developer Documentation
https://developer.apple.com/design/human-interface-guidelines/materials?utm_source=chatgpt.com
[11] [19] [40] https://atlassian.design/foundations/typography/applying-typography
https://atlassian.design/foundations/typography/applying-typography
[12] [26] [44] https://www.nngroup.com/articles/animation-purpose-ux/
https://www.nngroup.com/articles/animation-purpose-ux/
[13] [14] [36] [52] https://www.nngroup.com/articles/design-systems-101/
https://www.nngroup.com/articles/design-systems-101/
[15] [30] [35] [38] [39] https://www.nngroup.com/articles/testing-visual-design/
https://www.nngroup.com/articles/testing-visual-design/
[16] https://atlassian.design/foundations/spacing
https://atlassian.design/foundations/spacing
[20] https://www.nngroup.com/articles/chunking/
https://www.nngroup.com/articles/chunking/
[21] Color roles - Material Design 3
https://m3.material.io/styles/color/roles?utm_source=chatgpt.com
[22] Cards – Material Design 3
https://m3.material.io/components/cards/specs?utm_source=chatgpt.com
[23] Shapes - Fluent 2 Design System
https://fluent2.microsoft.design/shapes?utm_source=chatgpt.com
[24] SF Symbols | Apple Developer Documentation
https://developer.apple.com/design/human-interface-guidelines/sf-symbols?utm_source=chatgpt.com
[25] https://www.nngroup.com/articles/consistency-and-standards/
https://www.nngroup.com/articles/consistency-and-standards/
[27] [45] https://www.nngroup.com/articles/animation-usability/
https://www.nngroup.com/articles/animation-usability/
[28] https://www.nngroup.com/articles/trustworthy-design/
https://www.nngroup.com/articles/trustworthy-design/
[29] [37] [43] https://atlassian.design/components/tokens/all-tokens
https://atlassian.design/components/tokens/all-tokens
[34] https://fluent2.microsoft.design/design-tokens
https://fluent2.microsoft.design/design-tokens
[41] [50] https://ant.design/docs/spec/layout/
https://ant.design/docs/spec/layout/
[46] https://www.nngroup.com/articles/progress-indicators/
https://www.nngroup.com/articles/progress-indicators/
[47] https://design-system.service.gov.uk/styles/spacing/
https://design-system.service.gov.uk/styles/spacing/
[49] https://intl.cloud.tencent.com/document/product/1219/60346
https://intl.cloud.tencent.com/document/product/1219/60346
