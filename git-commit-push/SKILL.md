---
name: git-commit-push
description: 完整的Git工作流：检查状态、添加文件、提交并推送到远程仓库。当用户说"检查、提交并推送最新代码"、"git提交"、"提交代码"或类似表达时使用此技能。
---

# Git 提交推送技能

此技能自动化完整的Git工作流：检查状态 → 添加文件 → 提交 → 推送。

## 工作流程

### 1. 检查Git状态

首先运行以下命令检查当前仓库状态：

```bash
git status
```

分析输出：
- 如果显示 `nothing to commit, working tree clean` → 无需提交，推送前检查是否有待推送的提交
- 如果有 untracked files 或 modified files → 继续下一步
- 如果显示 `Your branch is ahead of origin/X by N commits` → 有待推送的提交，直接推送

### 2. 添加文件

根据状态添加文件：

- 如果有未跟踪的新文件：使用 `git add .` 添加所有文件
- 如果只想添加特定文件：使用 `git add <file-path>`
- 如果有需要忽略的文件已添加到暂存区：使用 `git reset HEAD <file>` 取消暂存

### 3. 提交更改

运行提交命令：

```bash
git commit -m "<提交消息>"
```

提交消息规范：
- 使用中文简洁描述
- 常用格式：`feat: 添加新功能` / `fix: 修复问题` / `docs: 更新文档` / `chore: 杂项更改`
- 如果是常规代码同步，可使用：`同步最新代码` / `更新材料` / `补充内容`

### 4. 推送到远程

最后推送到远程仓库：

```bash
git push
```

如果是首次推送新分支：
```bash
git push -u origin <branch-name>
```

## 输出格式

完成任务后，向用户报告：
- 提交前状态（有多少文件变更）
- 提交哈希和消息
- 推送结果
- 当前分支状态

## 注意事项

- 始终先运行 `git status` 了解当前状态
- 不要跳过状态检查直接提交
- 如果有敏感文件（如 .env、credentials），提醒用户检查 .gitignore
- 遇到合并冲突时，报告问题并停止，等待用户指示
