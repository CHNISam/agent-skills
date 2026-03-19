---
name: sync-global-skills
description: |
  同步全局 skills 到远程 Git 仓库进行备份。当用户说"备份 skills"、
  "同步到远端"、"推送到代码库"、"上传全局 skills"时使用。
  不要在其他情况下使用此 skill。
---

# 同步全局 Skills 到远程仓库

## 使用场景

仅在以下情况使用：
- 用户明确要求备份/同步全局 skills
- 用户说"推送 skills"、"上传到远端"等

## 路径速查

| 路径 | 说明 |
|------|------|
| `C:/Users/Administrator/.agents/skills/` | 源目录（本地全局 skills） |
| `C:/Users/Administrator/agent-skills/` | Git 工作区 |
| `origin` | 阿里云 Codeup（`https://codeup.aliyun.com/...`） |
| `github` | GitHub（`git@github.com:CHNISam/agent-skills.git`） |

## 操作步骤

### Step 1: 进入工作区

```bash
cd /c/Users/Administrator/agent-skills
```

### Step 2: 确保 GitHub remote 已配置

```bash
git remote get-url github >/dev/null 2>&1 || git remote add github git@github.com:CHNISam/agent-skills.git
git remote set-url github https://github.com/CHNISam/agent-skills.git 2>/dev/null
git remote get-url origin >/dev/null 2>&1 || git remote add origin https://codeup.aliyun.com/692d3a12bb64aae551974346/agent-skills.git
```

### Step 3: 同步 skills（处理特殊情况）

逐一复制，防止 cp 覆盖目录失败：

```bash
for skill in $(ls "C:/Users/Administrator/.agents/skills/"); do
  rm -rf "/c/Users/Administrator/agent-skills/$skill"
  cp -r "C:/Users/Administrator/.agents/skills/$skill" "/c/Users/Administrator/agent-skills/"
done
```

清理嵌入式 git 仓库：

```bash
rm -rf /c/Users/Administrator/agent-skills/research-writing-assistant/.git
```

### Step 4: 提交

```bash
cd /c/Users/Administrator/agent-skills
git add .
git commit -m "sync: update skills from local"
```

### Step 5: 同时推送到阿里云和 GitHub

```bash
git push origin master && git push github master
```

## 完整一键脚本

```bash
cd /c/Users/Administrator/agent-skills
git remote get-url github >/dev/null 2>&1 || git remote add github https://github.com/CHNISam/agent-skills.git
for skill in $(ls "C:/Users/Administrator/.agents/skills/"); do
  rm -rf "/c/Users/Administrator/agent-skills/$skill"
  cp -r "C:/Users/Administrator/.agents/skills/$skill" "/c/Users/Administrator/agent-skills/"
done
rm -rf /c/Users/Administrator/agent-skills/research-writing-assistant/.git
cd /c/Users/Administrator/agent-skills
git add .
git commit -m "sync: $(date '+%Y-%m-%d')"
git push origin master && git push github master
```

## 注意事项

- 仅同步 `.agents/skills/` 下的 skills 目录，不包含其他文件
- `research-writing-assistant` 带有嵌入 git 仓库，必须移除 `.git` 目录
- `superpowers` 本身是聚合目录，在 skills 列表中无需特殊处理
- 优先使用 HTTPS（`https://`）推送，避免 SSH key 配置问题
- 提交信息格式：`sync: YYYY-MM-DD`
