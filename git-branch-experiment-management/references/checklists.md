# 可执行 Checklist

## 创建分支前

回答以下问题，任一答案不明确就先停下来澄清：

- [ ] 为什么需要隔离？（协作 / 实验 / 依赖 / 发布）
- [ ] 这是一个需要多 Agent 或多人的短命协作分支（`change/*`），还是"答案尚未确定"的探索（`exp/*`）？
- [ ] 默认起点是 main 吗？如果不是，依赖的是哪个尚未进入 main 的分支？该依赖是否有意识且必要？
- [ ] 与其他进行中的工作关系是：互斥 / 正交 / 依赖 / 可运行时切换？
- [ ] 退出条件是什么？（实验必须有 Question + Success Criterion + Disposition）
- [ ] 是否考虑过更轻的方案：直接在主线上小步做、Feature Flag、Branch by Abstraction，而不是开分支？
- [ ] 如果多个并行任务：是否为每个任务分配独立的 `git worktree`？

## 合并进 main 前

- [ ] 结论是否已被接受？（改动是否已回答"是否应成为默认基线"）
- [ ] main 合并后是否仍能基本运行（install + build + 项目约定的最小运行/smoke check）？
- [ ] 实验实现是否值得直接进入 main？还是需要先清理、重建、拆分、只提取部分提交？
- [ ] 是否有临时 hack、写死参数、验证性代码需要留在分支而非进入 main？
- [ ] 合并后是否应删除该分支、对应 flag 或旧实现？
- [ ] 若是互斥路线，被否决的一侧是否已归档（decision note + archive tag）？

## 结束实验时

- [ ] 结论是否已写入 decision note（Question 的答案、Success Criterion 是否达成、为什么 accept/reject/continue）？
- [ ] 选择处置方式：
  - Reject：创建 annotated archive tag（如 `archive/exp-<name>`）+ 删除活跃分支。
  - Accept 且代码干净：正常集成进 main → 删除实验分支。
  - Accept 但代码脏：保留结论，从 main 重建或 cherry-pick 真正需要的部分 → 删除实验分支。
  - Continue：确认仍有明确未知问题，设定下一轮退出条件；不允许"以后可能有用"式无限保留。
- [ ] 需要保留历史资产时，是否已创建 archive tag？（用 tag 而非裸 commit hash 提供稳定名字）
- [ ] 是否有 Feature Flag / 旧实现需要删除或设删除期限与负责人？
