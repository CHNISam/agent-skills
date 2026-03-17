# Field Mapping

## Source priority

Use repository context in this order:

1. Existing test cases and test reports in `agent-context/`
2. Prototype files and prototype docs
3. PRD and change notes
4. Conversation logs and manual correction notes

When two sources conflict, prefer the more specific and more recent artifact. If the conflict changes expected behavior, ask before exporting the final workbook.

## Workbook columns

| Column | Required | How to fill |
| --- | --- | --- |
| 标题 | Yes | Use `页面/模块-场景-断言` or `模块-条件-结果`. Keep one assertion focus per row. |
| 目录 | Yes | Use the business slice or client type. In this repo, common values are `客户端微信小程序`, `司机端微信小程序`, `管理后台`. |
| 负责人 | Yes | Default to `aliyun5883078123` unless the user or existing sheet gives another owner. |
| 前置条件 | Yes | Describe the state required before the action. Keep it concise and testable. |
| 步骤描述 | Yes | Describe the primary action for this row. Split multi-assert journeys into separate cases. |
| 预期结果 | Yes | Describe the observable result for this row only. Avoid bundling multiple unrelated assertions. |
| 关联需求 | No | Fill with PRD section, story ID, change ID, or screen name when the source gives one. Otherwise leave blank. |
| 优先级 | Yes | Use `P0` for core paths, red lines, payments, permissions, delivery, and blocking failures; `P1` for common branches and exception handling; `P2` or `P3` for lower-frequency or polish cases. |
| 类型 | Yes | Default to `功能测试`. Use another type only when the user or source material clearly asks for it. |
| 标签 | No | Use only when the user already has a tagging scheme. Otherwise leave blank. |
| 预计工时汇总 | No | Leave blank unless the user explicitly provides estimates. |
| 实际工时汇总 | No | Leave blank unless the user explicitly provides actual effort. |

## Naming rules

- Keep titles unique within the workbook.
- Prefer Chinese wording.
- Avoid vague titles like `流程测试` or `异常校验`.
- If one page has multiple branches, encode the branch into the title.

## Case splitting rules

- Split happy path and exception path into separate rows.
- Split empty state, retry, permission failure, and boundary conditions into separate rows when they change the expected result.
- If a single UI action leads to two materially different outcomes based on state, create two rows with different preconditions.

## Project defaults from current sample

- The provided template is a single-sheet workbook named `测试用例导入模板`.
- The current sample sheet uses a single header row and a consistent body style.
- The current sample favors concise single-step rows rather than long numbered procedures.
