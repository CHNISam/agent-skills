---
name: sync-global-skills
description: |
  同步全局 skills 到多个 AI 代码编辑器和远程 Git 仓库进行备份。
  当用户说"备份 skills"、"同步到远端"、"推送到代码库"、"上传全局 skills"、
  "同步 skills 到所有编辑器"时使用。
  不要在其他情况下使用此 skill。
---

# 同步全局 Skills

## 支持的 AI 代码编辑器

| 编辑器 | 技能目录 | 优先级 |
|--------|----------|--------|
| **CodeBuddy** | `C:/Users/Administrator/.codebuddy/skills/` | 高 |
| OpenCode/Agents | `C:/Users/Administrator/.agents/skills/` | 源目录 |
| Codex | `C:/Users/Administrator/.codex/skills/` | 中 |
| Agent-Skills | `C:/Users/Administrator/agent-skills/` | Git 工作区 |

## 远程仓库

| 名称 | URL |
|------|-----|
| `origin` | 阿里云 Codeup（`https://codeup.aliyun.com/...`） |
| `github` | GitHub（`git@github.com:CHNISam/agent-skills.git`） |

## 同步脚本

CodeBuddy 提供自动同步脚本：

```bash
node "C:/Users/Administrator/.codebuddy/skills/sync-skills.js"
```

## 操作步骤

### Step 1: 运行同步脚本（推荐）

```bash
node "C:/Users/Administrator/.codebuddy/skills/sync-skills.js"
```

这会自动将所有源目录的技能同步到 CodeBuddy。

### Step 2: 同步到 Git 工作区

```bash
cd /c/Users/Administrator/agent-skills
for skill in $(ls "C:/Users/Administrator/.agents/skills/"); do
  rm -rf "/c/Users/Administrator/agent-skills/$skill"
  cp -r "C:/Users/Administrator/.agents/skills/$skill" "/c/Users/Administrator/agent-skills/"
done
rm -rf /c/Users/Administrator/agent-skills/research-writing-assistant/.git
```

### Step 3: 提交并推送

```bash
git add .
git commit -m "sync: $(date '+%Y-%m-%d')"
git push origin master && git push github master
```

## 完整一键脚本

```bash
# 同步到 Git 工作区
cd /c/Users/Administrator/agent-skills
for skill in $(ls "C:/Users/Administrator/.agents/skills/"); do
  rm -rf "/c/Users/Administrator/agent-skills/$skill"
  cp -r "C:/Users/Administrator/.agents/skills/$skill" "/c/Users/Administrator/agent-skills/"
done
rm -rf /c/Users/Administrator/agent-skills/research-writing-assistant/.git

# 提交推送
git add .
git commit -m "sync: $(date '+%Y-%m-%d')"
git push origin master && git push github master
```

## 注意事项

- CodeBuddy 是新添加的目标编辑器，已包含在自动同步脚本中
- 仅同步 `.agents/skills/` 下的 skills 目录，不包含其他文件
- `research-writing-assistant` 带有嵌入 git 仓库，必须移除 `.git` 目录
- 优先使用 HTTPS（`https://`）推送
- 提交信息格式：`sync: YYYY-MM-DD`
