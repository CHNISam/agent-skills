---
name: pause-and-clarify-riper5
description: 持续澄清需求，先问清再执行；信息不足时通过分阶段提问与确认收敛目标。基于 wubin28/pause-and-clarify-prompts 的 RIPER-5 提示模板做最小包装。
---

# Pause And Clarify (RIPER-5)

## Purpose

在任务不清晰、需求多解、输入不完整时，强制执行“先澄清后行动”。

## Upstream

- Source repo: `wubin28/pause-and-clarify-prompts`
- Source file: `prompt-templates/pt3-riper-5-system-prompt.zh-CN.md`
- Local upstream copy: `upstream-prompt.zh-CN.md`

## Workflow

1. 先识别当前请求是否存在歧义、缺失约束或验收标准不清。
2. 使用短问题分批澄清（优先 1-5 个必须问题）。
3. 在未获得必要答案前，不进入实施动作。
4. 获得答案后，先复述“目标/范围/约束/完成标准”，再继续。

## Output Contract

- `Clarified Goal`：一句话目标
- `Scope`：包含/不包含
- `Constraints`：技术/时间/兼容性/风险约束
- `Definition of Done`：可验证完成标准
- `Open Questions`：仍待确认项（若有）

## Notes

- 本 skill 为对上游 prompt 的最小包装，不改动其核心方法论。
- 如需完整原文，直接读取 `upstream-prompt.zh-CN.md`。
