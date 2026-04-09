---
name: tcb-connect
description: 连接腾讯云开发（CloudBase/TCB）并操作数据库、云函数、存储等服务。当需要查询或写入云开发数据库、调用云函数、管理云存储，或排查 CloudBase MCP 连接问题时使用。适用于 Claude Code、OpenAI Codex CLI 等所有 AI agent。
---

# 连接腾讯云开发（TCB/CloudBase）

## 项目环境

| 项目 | 值 |
|------|-----|
| 云环境 ID | `dev-5gzz7rxdbcf5d7dc` |
| AppID | `wx05415d4201a4c7c8` |
| 区域 | ap-shanghai |

---

## 核心原则：用 mcporter 而非原生 MCP

Claude Code 的原生 MCP 工具加载不稳定（`ToolSearch` 可能找不到 `mcp__cloudbase__*`）。**统一用 `mcporter` CLI 调用**，在任何 agent 环境都可靠。

### 验证 mcporter 能看到 cloudbase

```bash
npx mcporter list
```

预期输出包含 `cloudbase (36 tools)`。如果没有，检查 `~/.claude/settings.json` 的 `mcpServers.cloudbase` 配置。

---

## 关键规则：每条命令必须带环境变量

每次 mcporter 调用是独立进程，**登录态不跨命令持久化**。解决方案是通过环境变量自动绑定，**所有命令都加前缀**：

```bash
CLOUDBASE_ENV_ID=dev-5gzz7rxdbcf5d7dc npx mcporter call cloudbase.<tool> <params> --output json
```

不需要每次手动 `set_env`，这个前缀会自动完成环境绑定。

---

## 最小化验证连接

```bash
CLOUDBASE_ENV_ID=dev-5gzz7rxdbcf5d7dc npx mcporter call cloudbase.auth action=status --output json
```

`auth_status` 为 `READY` 即表示连接正常。

---

## 常用操作

### SQL 查询数据库

```bash
CLOUDBASE_ENV_ID=dev-5gzz7rxdbcf5d7dc npx mcporter call cloudbase.querySqlDatabase \
  action=runQuery \
  sql="SELECT * FROM map_poi LIMIT 5" \
  --output json
```

> ⚠️ action 必须是 `runQuery`，不是 `getEnvInfo` 或其他文档中可能出现的旧名称。

### 查看环境信息

```bash
CLOUDBASE_ENV_ID=dev-5gzz7rxdbcf5d7dc npx mcporter call cloudbase.envQuery action=info --output json
```

> ⚠️ action 必须是 `info`，不是 `getEnvInfo`。

### 列出所有可用工具（遇到工具名不确定时）

```bash
npx mcporter describe cloudbase --all-parameters 2>&1 | head -100
```

---

## 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| `ToolSearch` 找不到 cloudbase 工具 | 原生 MCP 加载失败 | 改用 `npx mcporter call cloudbase.*` |
| `ENV_REQUIRED` 错误 | 没传环境变量 | 命令前加 `CLOUDBASE_ENV_ID=dev-5gzz7rxdbcf5d7dc` |
| `invalid_enum_value` 错误 | action 名称错误 | 用 `npx mcporter describe cloudbase --all-parameters` 查正确名称 |
| `auth_status` 不是 READY | 登录态失效 | 执行 `npx mcporter call cloudbase.auth action=start_auth authMode=device --output json`，按提示完成设备码登录 |
| mcporter list 看不到 cloudbase | MCP server 未配置 | 检查 `~/.claude/settings.json` 是否有 cloudbase mcpServer 配置 |

---

## settings.json 参考配置

如需在新机器上配置，在 `~/.claude/settings.json` 的 `mcpServers` 里加：

```json
"cloudbase": {
  "command": "npx",
  "args": ["-y", "@cloudbase/cloudbase-mcp@latest"],
  "env": {
    "INTEGRATION_IDE": "ClaudeCode",
    "CLOUDBASE_ENV_ID": "dev-5gzz7rxdbcf5d7dc"
  }
}
```

登录用 device-code 方式，不需要明文 SecretId/SecretKey。
