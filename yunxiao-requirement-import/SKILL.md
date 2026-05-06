---
name: yunxiao-requirement-import
description: Create Yunxiao/Alibaba Cloud DevOps product requirement import spreadsheets from screenshots, release maps, bullet lists, or rough requirement notes. Use when the user wants to copy/fill a 产品类需求导入模板.xlsx for 云效 demand/import workflows, especially when converting versioned requirement trees with priority groups such as 高/中/低 into Excel rows.
---

# Yunxiao Requirement Import

## Workflow

1. Locate the user's Excel template. If none is provided, use `assets/产品类需求 导入模板.xlsx`.
2. Extract requirement rows from the user input.
   - Treat each leaf requirement item as one Excel row.
   - Do not create rows for grouping nodes such as version, `Bugfixes`, or `UI/UX 优化`.
   - Preserve exact Chinese wording from the source where possible.
3. Fill only fields that are explicitly known or defined by this skill.
   - `标题`: requirement title.
   - `负责人`: default to `潘洪森` unless the user says otherwise.
   - `优先级`: use the nearest priority group: `高`, `中`, or `低`.
   - `迭代`: use the version shown in the source, such as `v1.4.0`; if no version is present, ask or leave blank.
   - `描述`: leave blank unless the user explicitly asks to include descriptions.
   - `标签`: leave blank unless the user explicitly asks for tags.
   - `状态`, `参与者`, `抄送`, `计划开始时间`, `计划完成时间`, `预计工时`: leave blank unless supplied.
4. Generate a copied workbook, never overwrite the user's original template unless explicitly requested.
5. Re-read the output workbook and verify row count and key columns.

## Script

Use `scripts/fill_template.py` for deterministic Excel writing:

```bash
python scripts/fill_template.py --items requirements.json --output output.xlsx
```

The input JSON may be either a list of items or an object with an `items` list:

```json
[
  {"title": "登录页面增强引导 - ④", "priority": "高", "iteration": "v1.4.0"},
  {"title": "我的收藏和我的贡献页面统计数呈现效果统一", "priority": "低", "iteration": "v1.4.0"}
]
```

Optional item keys match template columns: `description`, `status`, `owner`, `participants`, `cc`, `tags`, `start_date`, `due_date`, `estimate_hours`.

Useful flags:

- `--template <path>`: use a specific template instead of the bundled asset.
- `--owner <name>`: override the default owner.
- `--include-description`: write `description` values when present.
- `--include-tags`: write `tags` values when present.

## Verification

After writing, inspect the workbook with `openpyxl`:

- Confirm the active sheet still has the original 12 template headers.
- Confirm all expected rows are present.
- Confirm `负责人` is populated, `描述` and `标签` are blank unless requested, and priorities/iterations match the source.
- Confirm there are no Excel error strings.
