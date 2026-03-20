---
name: generate-aliyun-testcase-xlsx
description: Generate Aliyun-compatible XLSX test case files for manual import from PRDs, prototypes, conversation logs, existing case sheets, or correction notes. Use when Codex needs to create or update a spreadsheet that the user will manually import into Aliyun test management and a fixed template, field order, naming style, controlled directory values, or exhaustive coverage standard must be followed. Do not use for API-based imports or for directly operating Aliyun.
---

# Generate Aliyun Testcase Xlsx

## Overview

Generate a test case workbook that matches the bundled Aliyun import template. Treat the user as the person who performs the final Aliyun import; the job is to extract scope, structure the cases, and export a standards-compliant `.xlsx`.

## Workflow

### 1. Build the source of truth

- Read project artifacts in this order unless the user overrides it:
  1. Existing test cases and test reports in `agent-context/`
  2. Prototype files and prototype docs
  3. PRD or change notes
  4. Conversation logs and correction records
- Read [references/field-mapping.md](references/field-mapping.md) before drafting rows.
- Read [references/directory-mapping.md](references/directory-mapping.md) whenever the workbook contains a `目录` column or the repo has fixed business directories.
- Read [references/quality-bar.md](references/quality-bar.md) when the user asks for strict coverage, “最高标准”, “不要遗漏”, or gives ambiguous notes.
- Read [references/input-format.md](references/input-format.md) before generating the workbook.

### 2. Lock the boundary before writing rows

- State explicitly that the deliverable is an `.xlsx` for manual import into Aliyun.
- Do not claim to upload, sync, or call Aliyun APIs.
- If a flow, copy choice, business rule, or expected result is genuinely uncertain, ask before producing the final workbook. Do not invent behavior.
- Keep the scope tied to the actual source material. Do not expand beyond the current product slice just to make the sheet look fuller.

### 3. Draft importable cases

- Use one workbook row per independent importable case.
- Prefer `页面/模块-场景-断言` style titles such as `服务点页-拒绝定位-支持城市切换与搜索选点`.
- Split broad flows into separate happy-path, exception, empty-state, retry, permission, and boundary rows when they assert different outcomes.
- Keep optional fields blank instead of fabricating values.
- Reuse defaults from the template only when the source material does not provide something better.
- Treat `目录` as a controlled field, not free text. If the repo defines allowed values, derive them from title, precondition, or module mapping.
- Treat `类型` as a template-controlled field. If the import sample shows a fixed value such as `功能测试`, keep that value consistent unless the user explicitly gives a different valid scheme.

### 4. Generate the workbook

- Write a JSON payload that matches [references/input-format.md](references/input-format.md).
- Run:
```bash
python scripts/generate_xlsx.py --input draft.json --output output.xlsx
```
- If the repo provides controlled directory rules, normalize and validate before delivery:
```bash
python scripts/normalize_ai_testcase_directory.py --input draft.json --rules rules.json
python scripts/validate_ai_testcase_directory.py --input output.xlsx --rules rules.json
```
- The script uses `assets/aliyun-manual-import-template.xlsx` by default and preserves the template sheet structure.
- Only switch templates if the user gives a different Aliyun import sheet and the header order has been verified.

### 5. Verify before delivery

- Confirm the first row still matches the template header order exactly.
- Confirm every required field is present and every row is importable as a standalone case.
- Check priorities, duplicate titles, and obvious omissions against the source scope.
- Check controlled fields such as `目录` and `类型` against the template or repo rules instead of relying on memory.
- Keep wording in Chinese unless the source material explicitly requires English.
- In this repository, respect the red lines called out in the product materials, such as fully Chinese UI and offline/manual payment assumptions.

## Bundled Resources

- `scripts/generate_xlsx.py`: Generate a workbook from structured JSON without external Python packages.
- `scripts/normalize_ai_testcase_directory.py`: Normalize controlled `目录` and `类型` fields for JSON and XLSX inputs.
- `scripts/validate_ai_testcase_directory.py`: Validate controlled `目录` and `类型` fields before delivery.
- `references/field-mapping.md`: Field-by-field mapping, defaults, and naming rules.
- `references/directory-mapping.md`: Controlled directory and type rules for repos that constrain these columns.
- `references/quality-bar.md`: Coverage and ambiguity rules derived from the user's strict review style.
- `references/input-format.md`: Input schema and command examples for the generator.
- `assets/aliyun-manual-import-template.xlsx`: Baseline import template copied from the provided sample sheet.

## Output Rules

- Deliver a real `.xlsx`, not markdown masquerading as a spreadsheet.
- Preserve the workbook as a plain manual-import sheet: no formulas, no merged cells, no extra worksheets unless explicitly requested.
- If the user gives an existing workbook to revise, preserve the field order and visible structure unless they explicitly ask for a new template.
