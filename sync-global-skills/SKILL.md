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

## 操作步骤

### 1. 确定路径

| 路径 | 说明 |
|------|------|
| `C:/Users/Administrator/.agents/skills/` | 源目录（本地全局 skills） |
| `C:/Users/Administrator/agent-skills/` | Git 本地仓库 |
| `origin` | codeup：`https://codeup.aliyun.com/692d3a12bb64aae551974346/agent-skills.git` |
| `github` | GitHub：`https://github.com/CHNISam/agent-skills.git` |

### 2. 克隆仓库（如不存在）

```bash
cd /c/Users/Administrator
git clone https://codeup.aliyun.com/692d3a12bb64aae551974346/agent-skills.git
cd agent-skills
git remote add github https://github.com/CHNISam/agent-skills.git
```

### 3. 同步 skills

```bash
cp -r "C:/Users/Administrator/.agents/skills/"* "C:/Users/Administrator/agent-skills/"
```

### 4. 提交并推送到两个远端

```bash
cd /c/Users/Administrator/agent-skills
git add .
git commit -m "sync: update skills from local"
git push origin master
git push github master
```

## 注意事项

- 仅同步 `.agents/skills/` 下的 skills，不包含其他文件
- 如果有嵌入式 git 仓库（如 research-writing-assistant），需要先移除
- 如果有 symlink（如 superpowers），需要先移除
- 提交信息格式：`sync: update skills from local`
- 两个远端都要推：`origin`（codeup）和 `github`（GitHub）
