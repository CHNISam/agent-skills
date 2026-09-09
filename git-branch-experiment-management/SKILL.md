---
name: git-branch-experiment-management
description: Git 分支、实验与集成管理规范（项目无关）。在创建分支前判断是否需要隔离、创建或管理 exp/* 实验分支（Question/Success Criterion/Relationship/Disposition 四要素）、审查是否把实验合并进 main、结束实验时执行 accept/reject/continue 归档并创建 archive tag、清理已合并或已拒绝的分支、多人或多 Agent 并行协作时使用短命分支与 git worktree、决定何时使用 Feature Flag 或 Branch by Abstraction、以及避免 develop/永久 feature 分支等反模式。触发词："创建分支"、"实验分支"、"分支管理"、"合并决策"、"分支归档"、"清理分支"、"并行开发"、"feature flag"、"分支策略"。
---

# Git Branch Experiment Management

## Overview

默认只保留一个长期集成基线（main），其他机制按"为什么需要隔离"选择。实验统一用 `exp/*`，先回答未知问题，再决定是否、如何把学习结果和代码进入 main。目标是保护决策可逆性并降低认知成本，而不是套用 Git Flow / GitHub Flow / Trunk-Based 的完整教条。

**目标仓库自己的分支模型优先。** 先读仓库实际的分支、文档与历史。若它已经确定了自己的模型（例如长期 develop、GitFlow、release 列车），按它执行，不要静默替换；本文下面的基线默认值只适用于尚未确定分支模型的仓库。`exp/*` 的四要素契约与 accept/reject/continue 归档是与分支模型无关的可复用部分，在任何模型下都能用。

## Core Principles

1. 分支不是目的，而是隔离代码变化的机制。需要隔离先看原因，再定命名与生命周期。
2. 主要隔离原因：多人/多 Agent 并行；未验证的产品或技术假设；有明确依赖的连续改动；正式发布或维护需要。
3. **资产 vs 变化（目录 vs 分支）**：已完成、已接受的资产应作为主干（main）中的目录/模块长期共存；分支只用于隔离"正在发生的变化"。判断顺序：改动还在进行、未验证 → 用分支；已经接受、需要长期共存 → 落成主干。不要用分支长期管理多个已完成的资产（分支合并即消失，主干无法同时呈现全部已接受资产）；也不要把所有小改动都开分支（单人小步改动直接提交主干）。"分支里的探索 → main 里的目录"是正常流转路径。
4. 互斥假设不应机械合并（两套替代路线并行探索，最终择一）。正交能力应尽早组合到同一集成基线验证。
5. "接受实验结论"与"接受实验分支里的全部代码"是两件事。

## Default Baseline: main

- main 是唯一长期集成基线，不设永久 develop。
- main 不表示生产版本；它表示"当前已接受、已集成、基本可运行，适合作为下一轮默认起点"。
- main 准入三条件：当前方向已被接受；与现有基线可共同工作；至少能正常安装、构建并通过最小运行/smoke check。
- 未回答"是否应成为默认基线"的改动，不要仅因为做完就进 main。
- 实验结论成立但分支里充满临时 hack/写死参数：提取结论和可复用实现，从 main 重新做干净集成，而不是整条 merge。

## Branch Types

| 类型 | 用途 | 生命周期 |
|---|---|---|
| `main` | 唯一长期集成基线 | 永久 |
| `change/*`（可细分 `feat/*` `fix/*` `refactor/*`） | 多人/多 Agent 协作、PR、Review、CI | 完成后合并并删除 |
| `exp/*` | 所有"答案尚未确定"的探索，不区分 spike 与 prototype | 得到结论后 accept/reject/continue |
| `release/*` | 只有真实发布隔离需求时才创建 | 按需 |

不为"看起来更专业"创建永久 develop、永久 feature 分支或没有退出条件的实验分支。

## Creating Branches

创建分支前回答（见 references 的 checklist）：

1. 为什么需要隔离：协作、实验、依赖、还是发布？
2. 默认起点是否为 main？
3. 是否与其他实验互斥、正交、依赖或可切换？
4. 退出条件是什么？

规则：
- 默认从 main 分叉。
- 仅当新工作明确依赖一个未进入 main 的实验时，才从实验分支继续分叉（依赖式分叉必须是有意识的）。
- 有依赖关系但希望保持 Review 粒度时，使用 stacked PR / stacked branch。
- 多 Agent / 多并行任务时使用 `git worktree`：一个 Agent / 一个任务对应一个 branch + 一个独立 working tree，避免 checkout/stash 互相污染。

## exp/* 实验契约

每个 `exp/*` 至少写清楚四件事：

- **Question**：这条分支要回答什么未知问题。
- **Success Criterion**：什么事实出现时可以认为实验成立。
- **Relationship**：与当前 main、其他实验是互斥、正交、依赖还是可运行时切换。
- **Disposition**：实验结束后准备 accept、reject 还是 continue。

exp/* 代码可以非常快、非常脏，只要它能有效回答问题。"实验成功"不等于"整条实验分支应该 merge"。

## Relationship Types

- **互斥**：两套替代方案不能同时成为最终默认答案。允许并行到足够做决定，最终择一；失败方向归档后删除活跃分支。
- **正交**：变化解决不同维度、可以共存。可独立协作，但应尽早组合到集成环境验证整体行为。
- **依赖**：后一个实验只有在前一个成立时才有意义。允许从前一个实验分支分叉，但必须明确依赖关系。
- **可切换**：两套实现可暂时共存在同一代码库并运行时选择时，优先 Feature Flag 或 Branch by Abstraction，而不是长期维护两个巨大分支。

## Feature Flag 边界

- 适用：新旧实现切换、算法/服务版本开关、灰度发布、A/B 比较、可共存但暂不默认启用的能力。
- 不适用：把两套根本互斥、长期并存成本很高的产品/架构路线永久塞进同一份代码。
- 所有 flag 都有 carrying cost（条件逻辑、测试组合、认知负担），必须有删除条件和负责人。

## Large Replacements (Branch by Abstraction)

旧实现到新实现的大型迁移，若二者可通过共同接口共存：

1. 先建立稳定抽象接口。
2. 在短命分支开发新实现，尽早合回 main。
3. 用 flag 或配置在新旧实现间切换。
4. 验证新实现后，删除旧实现、旧 flag 和迁移代码。

若无法合理共存，或探索可能被整体否决，则用 `exp/*` 隔离更合适。

## Merging Into main (Pre-Merge Checklist)

合并前检查：

1. 结论是否已被接受（是否回答清楚"应成为默认基线"）？
2. main 是否仍能基本运行（install + build + smoke check）？
3. 实验实现是否值得直接进入 main？
4. 是否需要先清理、重建、拆分或只提取部分提交？
5. 合并后是否应删除 branch、flag 或旧实现？

若结论成立但代码脏：记录结论 → 从 main 干净实现 → main。不要"因为方向被认可就无条件 merge 整条原型分支"。

## Ending an Experiment

- **Reject**：保存可追溯墓碑后删除活跃分支。推荐 annotated tag（如 `archive/exp-storage-v2`）+ 简短 decision note，不依赖裸 commit hash。
- **Accept 且代码干净**：走正常集成流程进 main，再删除实验分支。
- **Accept 但代码很脏**：保留实验结论，从 main 重建或 cherry-pick/提取真正需要的部分。
- **Continue**：只有仍存在明确未知问题时才继续，不允许无限期保留"以后可能有用"的分支。

结束实验时自动生成或更新 decision note；需要保留历史时创建 archive tag。Tag 的目的不是维护旧路线，而是让以后能低成本恢复历史资产、实现和决策上下文。

## Anti-Patterns

- 因为熟悉 Git Flow 就默认创建 develop。
- 把每个 bug、UI 调整或素材变更都包装成长期实验。
- 把所有实验都强行 Feature Flag 化。
- 让 exp/* 没有明确问题和退出条件。
- 实验方向被认可就无条件 merge 整条原型分支。
- 从随机当前分支继续叠加无关工作。
- 让 main 变成"什么都能进"的垃圾场，或把它定义成原型阶段不存在的"生产稳定线"。

## Decision Priorities

1. 保护决策可逆性（避免探索 A 被 B 覆盖后只能整体回滚）。
2. 维持一个可作为默认起点的 main。
3. 降低并行协作冲突，让工作可独立 Review 和集成。
4. 限制长期分支、Feature Flags 和旧实现的认知成本。
5. 只有真实需求出现时才增加 release/develop 等额外结构。

## References

- `references/spec.md`：完整规范原文（18 节，含推荐工作流与参考实践链接）。
- `references/checklists.md`：创建分支前 / 合并前 / 结束实验的三份可执行 checklist。
