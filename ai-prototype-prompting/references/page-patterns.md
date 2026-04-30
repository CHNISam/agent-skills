# Page Pattern Templates

## Form / Publishing Page

Use for content publishing, feedback, reporting, review submission, profile editing.

Must define:

- Entry source and return path
- Required and optional fields
- Field validation and disabled state
- Draft/autosave behavior if relevant
- Submit loading, success, failure, retry, and save-for-later states
- Image/file upload states if relevant
- Permission states for location, camera, media, or identity

Prompt additions:

```text
Design this as a focused task page. Keep the user's primary action visible and stable.
Show all required fields with explicit labels and helper text.
Include empty, partially filled, validation error, submitting, submit failed, and success states.
Preserve entered content after failure.
```

## Login / Onboarding Page

Use when login guidance is weak or users do not know why they need to authenticate.

Must define:

- Why login is needed
- What abilities unlock after login
- Exact required steps
- What happens after completion
- Whether the user can skip or return
- Existing technical login constraints

Prompt additions:

```text
Make this feel like completing a lightweight identity setup, not a cold form.
The first screen must answer: why login, what to do first, and what happens after success.
Do not introduce new login methods beyond the current product scope.
```

## Dashboard / Data Page

Use for metrics, admin panels, operations pages.

Must define:

- KPI card count and fields
- Chart types and data time range
- Table columns, row count, status logic
- Filters, search, pagination, sorting
- Empty, loading, error, and partial-data states

Prompt additions:

```text
Prioritize scannability and repeat use over decorative presentation.
Use dense but readable information hierarchy.
Include realistic data scale and status colors with text labels.
```

## Feed / Grid / Listing Page

Use for content plazas, discovery feeds, media grids, card lists.

Must define:

- Card anatomy
- Thumbnail ratio
- Metadata fields
- Sorting/filtering
- Empty/loading/error/end-of-list states
- Interaction on card tap and quick actions

Prompt additions:

```text
Preserve card consistency and avoid layout shift as content loads.
Include realistic long text, missing image, and empty list cases.
```

## WeChat Mini Program Page

Use for WXML/TDesign/WeUI/Vant oriented mobile prototypes.

Must define:

- Navigation bar behavior
- Tabbar behavior
- Whether the page is a tab page or independent page
- Native API capabilities such as avatar, nickname, media upload, location, phone call
- Safe area and bottom fixed action behavior

Prompt additions:

```text
Keep the design aligned with WeChat Mini Program conventions.
Use mobile-first hierarchy, stable bottom actions, large tap targets, and clear native permission states.
If using TDesign, keep components visually consistent with TDesign MiniProgram.
```

