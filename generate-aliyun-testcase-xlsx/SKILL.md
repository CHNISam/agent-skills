---
name: generate-aliyun-testcase-xlsx
description: Generate Aliyun-compatible XLSX test case files for manual import from PRDs, prototypes, conversation logs, existing case sheets, or correction notes. Use when Codex needs to create or update a spreadsheet that the user will manually import into Aliyun test management and a fixed template, field order, naming style, or exhaustive coverage standard must be followed. Do not use for API-based imports or for directly operating Aliyun.
---

# Generate Aliyun Testcase Xlsx

## Overview

Generate a test case workbook that matches the bundled Aliyun import template. Treat the user as the person who performs the final Aliyun import; your job is to extract scope, structure the cases, and export a standards-compliant `.xlsx`.

## Workflow

### 1. Build the source of truth

- Read project artifacts in this order unless the user overrides it:
  1. Existing test cases and test reports in `agent-context/`
  2. Prototype files and prototype docs
  3. PRD or change notes
  4. Conversation logs and correction records
- Read [references/field-mapping.md](references/field-mapping.md) before drafting rows.
- Read [references/quality-bar.md](references/quality-bar.md) when the user asks for strict coverage, “最高标准”, “不要遗漏”, or gives ambiguous notes.
- Read [references/input-format.md](references/input-format.md) before generating the workbook.

### 2. Lock the boundary before writing rows

- State explicitly that the deliverable is an `.xlsx` for manual import into Aliyun.
- Do not claim to upload, sync, or call Aliyun APIs.
- If a flow, copy choice, business rule, or expected result is genuinely uncertain, ask the user before producing the final workbook. Do not invent behavior.
- Keep the scope tied to the actual source material. Do not expand beyond the current product slice just to make the sheet look fuller.

### 3. Draft importable cases

- Use one workbook row per independent importable case.
- Prefer `页面/模块-场景-断言` style titles such as `服务点页-拒绝定位-支持城市切换与搜索选点`.
- Split broad flows into separate happy-path, exception, empty-state, retry, permission, and boundary rows when they assert different outcomes.
- Keep optional fields blank instead of fabricating values.
- Reuse defaults from the template only when the source material does not provide something better.

### 4. Generate the workbook

- Write a JSON payload that matches [references/input-format.md](references/input-format.md).
- Run:
```bash
python scripts/generate_xlsx.py --input draft.json --output output.xlsx
```
- The script uses `assets/aliyun-manual-import-template.xlsx` by default and preserves the template sheet structure.
- Only switch templates if the user gives a different Aliyun import sheet and you have verified the header order.

### 5. Verify before delivery

- Confirm the first row still matches the template header order exactly.
- Confirm every required field is present and every row is importable as a standalone case.
- Check priorities, duplicate titles, and obvious omissions against the source scope.
- Keep wording in Chinese unless the source material explicitly requires English.
- In this repository, respect the red lines called out in the product materials, such as fully Chinese UI and offline/manual payment assumptions.

## Quick Triggers

Use this skill for requests like:

- “根据 PRD 和原型给我出一份阿里云导入测试用例表。”
- “把这份现有测试用例整理成阿里云能手动导入的 xlsx。”
- “按最高标准补齐遗漏测试点，然后生成导入模板。”
- “我手动导入阿里云，你只负责按标准生成 xlsx。”

## Bundled Resources

- `scripts/generate_xlsx.py`: Generate a workbook from structured JSON without external Python packages.
- `references/field-mapping.md`: Field-by-field mapping, defaults, and naming rules.
- `references/quality-bar.md`: Coverage and ambiguity rules derived from the user's strict review style.
- `references/input-format.md`: Input schema and command examples for the generator.
- `assets/aliyun-manual-import-template.xlsx`: Baseline import template copied from the provided sample sheet.

## Output Rules

- Deliver a real `.xlsx`, not markdown masquerading as a spreadsheet.
- Preserve the workbook as a plain manual-import sheet: no formulas, no merged cells, no extra worksheets unless the user explicitly asks for them.
- If the user gives an existing workbook to revise, preserve the field order and visible structure unless they explicitly ask for a new template.
