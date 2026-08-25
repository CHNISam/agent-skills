# 工具台账

记录格式：

```
工具：
用途：
安装方式：
状态：
```

---

# Installed

已采用，属于基线的一部分。

## Agent

```
工具：Codex CLI
用途：OpenAI 的终端 Coding Agent
安装方式：npm i -g @openai/codex
状态：v0.149.0 — 无 LSP，靠 CLI 诊断
```

```
工具：Claude Code
用途：Anthropic 的终端 Coding Agent
安装方式：npm i -g @anthropic-ai/claude-code
状态：v2.1.245 — LSP 已接 TypeScript + Python
```

```
工具：OpenCode
用途：开源多模型终端 Coding Agent
安装方式：npm i -g opencode-ai
状态：v1.18.22 — 内置 LSP 已开启（"lsp": true）
```

```
工具：Cursor
用途：AI IDE，Godot / 图形化调试的主力
安装方式：官网安装包（D:\cursor）
状态：v3.17.8 — LSP 为编辑器原生能力，无需开启
```

## MCP

```
工具：Context7 MCP
用途：查询库和框架的最新官方文档，避免模型用过期 API
安装方式：远程 HTTP，https://mcp.context7.com/mcp
  Codex     ~/.codex/config.toml           [mcp_servers.context7] url = "..."
  Claude    claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp
  OpenCode  ~/.config/opencode/opencode.jsonc   mcp.context7 { type: "remote", url: "..." }
  Cursor    ~/.cursor/mcp.json             mcpServers.context7 { url: "..." }
状态：四个 Agent 已一致
```

## Language Server

```
工具：typescript-language-server
用途：TypeScript / JavaScript 的 definition、references、diagnostics、symbols
安装方式：npm i -g typescript@5 typescript-language-server
状态：v5.3.0（typescript v5.9.3）
陷阱：全局 typescript 必须锁在 5.x。TypeScript 7 是 Go 重写版，只发 tsc、不含
  lib/tsserver.js，typescript-language-server 会 initialize 失败并退出，报
  "Could not find a valid TypeScript installation"。故意写死 @5。
  Claude Code  claude plugin install typescript-lsp@claude-plugins-official --scope user
  OpenCode     内置自动安装
  Cursor       内置 typescript-language-features
  Codex        无 LSP，用 npx tsc --noEmit
```

```
工具：pyright
用途：Python 类型检查与语言服务
安装方式：npm i -g pyright（提供 pyright-langserver）
状态：v1.1.413
  Claude Code  claude plugin install pyright-lsp@claude-plugins-official --scope user
  OpenCode     内置，检测到 .py 时触发
  Cursor       ms-python.python + anysphere.cursorpyright
  Codex        无 LSP，用 pyright <path>
```

```
工具：gdtoolkit（gdlint / gdformat / gdparse / gd2py）
用途：GDScript 的静态检查与格式化，给没有 LSP 通道的 Agent 兜底
安装方式：uv tool install "gdtoolkit==4.*"（装到 ~/.local/bin，需 uv tool update-shell）
状态：v4.5.0
```

```
工具：geequlim.godot-tools（Cursor 扩展）
用途：GDScript 的完整 LSP —— 连 Godot 编辑器内置的 TCP 语言服务器（127.0.0.1:6005）
安装方式：cursor --install-extension geequlim.godot-tools
状态：v2.7.1 — 仅在 Godot 编辑器打开时可用
```

## 共用命令行

```
工具：git
用途：版本控制，所有 Agent 共用
安装方式：Git for Windows
状态：v2.53.0.windows.1
```

```
工具：ripgrep (rg)
用途：全文代码搜索，Agent 内置搜索工具的底层
安装方式：winget install BurntSushi.ripgrep.MSVC
状态：v14.1.1
```

```
工具：fd
用途：按文件名/路径快速定位，比 find 快且默认尊重 .gitignore
安装方式：winget install sharkdp.fd
状态：v10.4.2
```

```
工具：fzf
用途：交互式模糊筛选，配合 rg / fd / git 做人工挑选
安装方式：winget install junegunn.fzf
状态：v0.74.3
```

```
工具：node / npm
用途：多数语言服务器和 MCP server 的运行时
安装方式：官网安装包
状态：node v22.22.1 / npm v10.9.4
```

```
工具：python
用途：脚本与 Python 项目运行时
安装方式：官网安装包
状态：v3.13.12
```

```
工具：uv
用途：Python 包与命令行工具管理，用它装 gdtoolkit
安装方式：winget install astral-sh.uv
状态：v0.12.5
```

---

# Watching

未来关注，**当前不主动维护**。

```
工具：Tree-sitter
用途：增量语法解析，代码结构理解
安装方式：不自行安装
状态：关注 — 编辑器和 Agent 内部已在用。只在某个 Agent 把它作为可配置能力开放时再评估
```

```
工具：Codebase RAG / Graph RAG
用途：大仓库的语义检索与依赖图
安装方式：不自建 vector DB / embedding pipeline / 依赖图
状态：关注 — 属于 Coding Agent 内部代码索引能力。等官方把索引质量做上来，而不是自己搭一套
```

```
工具：Codex CLI 的 LSP 支持
用途：让 Codex 拿到 definition / references / diagnostics
安装方式：暂无官方方案。社区有 LSP→MCP 桥接（EpicHigh/lsp-for-codex、code-yeongyu/codex-lsp、Latias94/lspi）
状态：关注 — 官方 feature request openai/codex#8745 仍开放。等官方实现，不装第三方桥接
```

```
工具：filesystem MCP
用途：标准化的文件读写接口
安装方式：npx -y @modelcontextprotocol/server-filesystem <roots>
状态：刻意不装 — 与四个 Agent 的原生文件工具重复，且能力更弱、开销更大
```

```
工具：新 MCP 标准 / 传输方式
用途：MCP 协议本身的演进（新 transport、apps、elicitation 等）
安装方式：—
状态：关注 — 协议变动时回来复核四个 Agent 的 MCP 配置写法是否还一致
```

```
工具：Structured Output / Guardrails
用途：约束 LLM 输出格式
安装方式：不安装
状态：不采用 — 面向 LLM 应用开发。Coding Agent 已有 tool calling / patch / schema 机制
```

```
工具：Sandbox Runtime（Docker 等）
用途：隔离执行环境
安装方式：不安装
状态：不采用 — Agent 已提供 permission / approval / execution control
```
