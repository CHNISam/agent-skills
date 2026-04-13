---
name: root-cause-and-verification
description: 组合入口：信息不足先澄清，原因不明先做 5 Why/系统化排查，最后必须给出验证证据闭环。
---

# Root Cause And Verification

## Purpose

把三个原子能力串成一个稳定流程：

1. `clarification/pause-and-clarify-riper5` 或 `clarification/ask-questions-if-underspecified`
2. `problem-analysis/5-whys-root-cause-analysis` + `debugging/systematic-debugging`
3. `debugging/verification-before-completion`

## Execution Order

1. **Clarify First**
- 目标、范围、约束、完成标准不清时，先澄清，不实施。

2. **Root Cause Next**
- 使用 5 Why 向下钻取，不接受“症状即结论”。
- 使用 systematic-debugging 的证据链方法验证假设。

3. **Verify Before Claim**
- 没有新鲜验证证据，不得宣称“已修复/已完成”。

## Required Output

- `Problem Statement`
- `Why-Chain (>=3, ideally 5)`
- `Root Cause`
- `Fix/Decision`
- `Verification Evidence`（命令、结果、结论）
- `Residual Risk`

## Boundary

- 本 skill 只做编排，不替代原子 skill。
- 原子 skill 仍应保持独立可复用。
