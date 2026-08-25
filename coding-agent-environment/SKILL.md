---
name: coding-agent-environment
description: |
  维护个人 AI Coding Agent 基础设施（Codex CLI / Claude Code / OpenCode / Cursor）：
  统一 MCP、Code Intelligence（LSP）与共用命令行工具。
  当用户说"新电脑初始化"、"配置 Agent 环境"、"检查 AI 开发环境"、
  "接入新 Agent"、"补齐 LSP / MCP"时使用。
  不要用于单个项目的依赖安装或业务功能开发。
---

# Coding Agent Environment

个人 AI 开发环境的**基础设施清单**，不是 Agent 框架。

目标只有三个：让四个 Agent 的实际编程能力对齐、让配置长期可维护、让换电脑能快速恢复。

## 何时用

- **新电脑初始化** —— 按 `checklist.md` 从零装一遍
- **新 Agent 接入** —— 对照"标准能力"把新 Agent 补齐到同一水位
- **定期体检** —— 每季度或某个 Agent 大版本更新后跑一遍 checklist

## 支持的 Agent

| Agent | 主配置文件 | MCP 配置位置 | LSP 机制 |
|---|---|---|---|
| **Codex CLI** | `~/.codex/config.toml` | 同文件 `[mcp_servers.<name>]` | ❌ 官方未支持 |
| **Claude Code** | `~/.claude/settings.json` | `~/.claude.json`（用 `claude mcp add`） | ✅ 官方插件市场 |
| **OpenCode** | `~/.config/opencode/opencode.jsonc` | 同文件 `mcp` 段 | ✅ 内置，`"lsp": true` |
| **Cursor** | `%APPDATA%\Cursor\User\settings.json` | `~/.cursor/mcp.json` | ✅ 编辑器原生（VS Code 内核） |

### 两个易踩的坑

1. **Claude Code 的 `mcpServers` 不能写在 `settings.json` 里。** 官方 settings 参考中没有这个键，写了会被静默忽略——不报错、也不生效。用 `claude mcp add --scope user ...`，落到 `~/.claude.json`。
2. **Claude Code 与 OpenCode 的 LSP 都只跑 stdio。** Claude Code 的 schema 接受 `transport: "socket"` 但实际仍以 stdio 运行。任何只提供 TCP 端口的语言服务器（典型：Godot）在这两者里都用不了。

## 标准能力

每个 Agent 都应具备下面四项。缺哪项按 `checklist.md` 补。

1. **访问项目文件** —— 用 Agent 原生文件工具，不装 filesystem MCP（见下）
2. **搜索代码** —— `ripgrep` + `fd`，所有 Agent 共用
3. **获得代码诊断** —— LSP 优先；没有 LSP 的走 CLI linter
4. **查询最新官方文档** —— Context7 MCP，四个 Agent 一致

### MCP 基线

只统一 **Context7**，用于查最新官方文档。四个 Agent 都要有。

**刻意不装 filesystem MCP。** 四个 Agent 都已内置原生文件工具，而且比 filesystem MCP 更强（行号偏移、图片/PDF/notebook 读取）。装它等于每个 Agent 多十几个重复工具、多一个常驻 npx 进程，还被限制在声明的 roots 内。这是重复实现 Harness 已有能力。

业务类 MCP（GitHub / 数据库 / Slack / CloudBase 等）**按需单独加，不进基线**。

### Code Intelligence 基线

| 语言 | Claude Code | Codex CLI | OpenCode | Cursor |
|---|---|---|---|---|
| TypeScript / JS | `typescript-lsp` 插件 | ❌ 走 CLI | 内置（自动安装） | 内置 `typescript-language-features` |
| Python | `pyright-lsp` 插件 | ❌ 走 CLI | 内置（检测到 `.py` 触发） | `ms-python.python` + `anysphere.cursorpyright` |
| GDScript | `gdlint` CLI | `gdlint` CLI | `gdlint` CLI | `geequlim.godot-tools`（连编辑器 TCP :6005） |

Claude Code 的 LSP 插件**只负责连接，不负责安装二进制**。二进制必须先装好并在 PATH 里，否则 `/plugin` 的 Errors 标签会报 `Executable not found in $PATH`。

**Godot 的特殊性**：GDScript 语言服务器是 Godot 编辑器内置的 TCP 服务（默认 `127.0.0.1:6005`），没有独立的 stdio 二进制。所以只有 Cursor 能拿到完整的 definition / references / diagnostics，且需要 Godot 编辑器处于打开状态。其余三个 Agent 退而用 `gdlint` 拿语法和风格诊断。

## 检查流程

1. 打开 `checklist.md`，逐项跑验证命令
2. 缺失项按 `tools.md` 的 **Installed** 段落里的安装方式补齐
3. 补完后跑 `checklist.md` 末尾的**四 Agent 验证**
4. 任何安装或配置变更，追加一条到 `update-log.md`

## 刻意不做的事

这些技术本身重要，但属于 Agent Harness 内部能力，**不自建**：

| 技术 | 为什么不做 | 态度 |
|---|---|---|
| **Tree-sitter** | 编辑器和 Agent 内部已在用 | 关注，不主动维护 |
| **Codebase RAG / Graph RAG** | 属于 Coding Agent 内部代码索引能力，不自建 vector DB / embedding pipeline / 依赖图 | 关注，不主动维护 |
| **Structured Output / Guardrails** | 面向 LLM 应用开发；Coding Agent 已有 tool calling / patch / schema 机制 | 不安装 |
| **Sandbox Runtime** | Agent 已提供 permission / approval / execution control，不额外引入 Docker sandbox | 不安装 |
| **通用 LSP 框架** | 只装实际用到的语言服务 | 不安装 |

原则：维护个人 AI 开发环境，不建设 Agent 平台。

## 文件

- `checklist.md` —— 机器检查清单（含验证命令）
- `tools.md` —— 工具台账：Installed / Watching
- `update-log.md` —— 变更记录

## 同步

本 skill 源目录是 `~/.agents/skills/`，备份仓库是 `~/agent-skills/`（origin=codeup，github=CHNISam/agent-skills）。改完用 `sync-global-skills` skill 推送。
