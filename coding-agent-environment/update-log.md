# 变更记录

新增一条时置顶。格式：日期 / 变化 / 原因。

---

## 2026-08-25

**变化：建立基线，四个 Agent 首次统一**

环境盘点（全部已装）：Codex CLI 0.149.0、Claude Code 2.1.245、OpenCode 1.18.22、Cursor 3.17.8。

安装：

| 项目 | 版本 | 方式 |
|---|---|---|
| typescript-language-server | 5.3.0 | `npm i -g typescript@5 typescript-language-server` |
| pyright | 1.1.413 | `npm i -g pyright` |
| gdtoolkit | 4.5.0 | `uv tool install "gdtoolkit==4.*"` |
| fd | 10.4.2 | `winget install sharkdp.fd` |
| fzf | 0.74.3 | `winget install junegunn.fzf` |
| Claude Code `typescript-lsp` 插件 | 1.0.0 | `claude plugin install typescript-lsp@claude-plugins-official --scope user` |
| Claude Code `pyright-lsp` 插件 | — | `claude plugin install pyright-lsp@claude-plugins-official --scope user` |
| Cursor `geequlim.godot-tools` | 2.7.1 | `cursor --install-extension` |
| Cursor `ms-python.python` | 2025.6.1 | `cursor --install-extension`（连带 cursorpyright 1.0.12、debugpy） |

配置变更：

- Context7 MCP 补齐到 Claude Code（`~/.claude.json`）、OpenCode（`opencode.jsonc`）、Cursor（`~/.cursor/mcp.json`）。Codex 原本就有。四个 Agent 现在一致。
- 删除 `~/.claude/settings.json` 里的 `mcpServers` 块（stitch、weapp-dev、cloudbase）。
- `uv tool update-shell` 把 `~/.local/bin` 加进用户 PATH。

**原因：**

- git 和 ripgrep 本来就有，fd 和 fzf 缺失，补齐四件套。
- TypeScript / Python / Godot 是当前三个主力方向，只装这三种语言服务，不装通用 LSP 框架。
- `mcpServers` 不是 `settings.json` 的合法键，官方 settings 参考里没有，写了会被静默忽略——`claude mcp list` 里从来没出现过这三个。确认是死配置，删掉而不是迁移，因为它们一直没生效也没影响使用，说明并无实际依赖。
- 只统一 Context7 一个 MCP。业务类 MCP 按需单加，不进基线。

**刻意不做：**

- **不装 filesystem MCP。** 四个 Agent 的原生文件工具已覆盖且更强（行号偏移、图片/PDF/notebook），装它是重复实现 Harness 能力，还多十几个工具和一个常驻进程。
- **不装 Codex 的第三方 LSP 桥接。** 官方无 LSP（`codex features list` 里无相关 flag，`[features]` 文档也没有），社区桥接项目都很新。等官方（openai/codex#8745）。
- **不自建** Tree-sitter / Codebase RAG / Guardrails / Docker sandbox，理由见 `tools.md` 的 Watching 段。

**过程中发现并修掉的问题：**

- 初装时 `npm i -g typescript` 拉到了 **TypeScript 7.0.2**（Go 重写版）。它只发 `tsc`，
  不含 `lib/tsserver.js`，导致 `typescript-language-server` 的 initialize 直接失败退出：
  `Could not find a valid TypeScript installation`。二进制装上了、`--version` 也正常，
  但 LSP 根本起不来——只跑 `--version` 检查不出来。改装 `typescript@5`（5.9.3）后
  握手通过。checklist 已加上版本校验和握手烟雾测试。

**验证结果：**

- `typescript-language-server` 与 `pyright-langserver` 的 initialize 均返回
  definition / references / documentSymbol / hover 四项能力，didOpen 后均正常推送
  `publishDiagnostics`（TS 报出 TS2322，pyright 报出返回类型不匹配）。
- `gdlint` 能报出 GDScript 命名不合规。
- Context7 在四个 Agent 均已配置，Claude Code 侧 `claude mcp list` 显示 ✔ Connected。

**已知边界：**

- Godot 的 GDScript 语言服务器是编辑器内置 TCP 服务（:6005），没有 stdio 二进制。Claude Code 和 OpenCode 的 LSP 都只跑 stdio（Claude Code 的 schema 接受 `socket` 但实际仍以 stdio 运行），所以只有 Cursor 能拿到完整 GDScript LSP，且需 Godot 编辑器打开。其余三个用 `gdlint` 兜底。
- Codex CLI 全程无 LSP，诊断只能走 `npx tsc --noEmit` / `pyright` / `gdlint`。
