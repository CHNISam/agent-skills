# 机器检查清单

新电脑初始化 / 定期体检时逐项跑。每项给了验证命令，输出为空或报错即为缺失。

## Agent

- [ ] **Codex CLI** — `codex --version`
- [ ] **Claude Code** — `claude --version`
- [ ] **OpenCode** — `opencode --version`
- [ ] **Cursor** — `node -p "require('D:/cursor/resources/app/package.json').version"`

一次性查全：

```bash
for c in codex claude opencode; do printf "%-10s " "$c"; command -v $c >/dev/null && $c --version 2>&1 | head -1 || echo MISSING; done
```

## MCP

基线只有 Context7。四个 Agent 必须一致。

- [ ] **Context7 — Codex** — `grep -A1 'mcp_servers.context7' ~/.codex/config.toml`
- [ ] **Context7 — Claude Code** — `claude mcp list | grep context7`
- [ ] **Context7 — OpenCode** — `grep -A3 '"context7"' ~/.config/opencode/opencode.jsonc`
- [ ] **Context7 — Cursor** — `node -e "console.log(Object.keys(require(process.env.USERPROFILE+'/.cursor/mcp.json').mcpServers))"`

- [x] **filesystem MCP — 刻意不装**。四个 Agent 的原生文件工具已覆盖且更强。理由见 `SKILL.md`。

> 检查 Claude Code 时顺带确认 `~/.claude/settings.json` **没有** `mcpServers` 键——那不是合法配置键，写了会被静默忽略：
> ```bash
> node -e "const j=require(process.env.USERPROFILE+'/.claude/settings.json'); console.log(j.mcpServers ? 'BAD: 删掉这个键' : 'OK')"
> ```

## Code Intelligence

### 语言服务器二进制

- [ ] **typescript-language-server** — `typescript-language-server --version`
- [ ] **全局 typescript 必须是 5.x** — `node -p "require(process.env.APPDATA+'/npm/node_modules/typescript/package.json').version"`
      TypeScript 7 是 Go 重写版，不含 `lib/tsserver.js`，会让 typescript-language-server
      启动失败（`Could not find a valid TypeScript installation`）。修：`npm i -g typescript@5`
- [ ] **pyright-langserver** — `npm ls -g pyright`
- [ ] **gdtoolkit（gdlint / gdformat）** — `gdlint --version`

### 各 Agent 接线

- [ ] **Claude Code — TypeScript** — `claude plugin list | grep typescript-lsp`
- [ ] **Claude Code — Python** — `claude plugin list | grep pyright-lsp`
- [ ] **OpenCode — LSP 总开关** — `grep '"lsp"' ~/.config/opencode/opencode.jsonc` 应为 `true`
- [ ] **Cursor — Python 扩展** — `cursor --list-extensions | grep -E "ms-python.python|cursorpyright"`
- [ ] **Cursor — Godot 扩展** — `cursor --list-extensions | grep godot-tools`
- [x] **Codex CLI — 无 LSP**。官方未支持（`codex features list` 里无相关 flag）。走 CLI 诊断，见下。

### Codex / CLI 侧的诊断替代

没有 LSP 的 Agent 靠命令行拿诊断：

```bash
npx tsc --noEmit          # TypeScript / JS
pyright <path>            # Python
gdlint <file.gd>          # GDScript
```

### 语言服务器烟雾测试

二进制存在 ≠ LSP 能起来。真正的验证是跑一次 initialize 握手并看诊断是否推送：

```bash
# 造两个有错的文件
printf 'const n: number = "x";
' > /tmp/bad.ts
printf 'def f(a: int) -> str:
    return a + 1
' > /tmp/bad.py

# CLI 侧（Codex 等无 LSP 的 Agent 走这条）
npx tsc --noEmit --strict /tmp/bad.ts    # 应报 TS2322
pyright /tmp/bad.py                       # 应报返回类型不匹配
gdlint <某个 .gd>                          # 变量名不合规等应被报出
```

LSP 侧的四项能力（definition / references / documentSymbol / hover）会在 initialize
响应的 `capabilities` 里出现；diagnostics 走 `textDocument/publishDiagnostics` 推送，
需要 didOpen 之后才能观察到。

## 共用命令行工具

- [ ] **git** — `git --version`
- [ ] **ripgrep** — `rg --version`
- [ ] **fd** — `fd --version`
- [ ] **fzf** — `fzf --version`

运行时（上面这些的前置）：

- [ ] **node / npm** — `node --version && npm --version`
- [ ] **python** — `python --version`
- [ ] **uv** — `uv --version`

一次性查全：

```bash
for t in git rg fd fzf node npm python uv; do printf "%-8s " "$t"; command -v $t >/dev/null && $t --version 2>&1 | head -1 || echo MISSING; done
```

## 四 Agent 验证

补齐后，在一个真实项目里对每个 Agent 确认这四件事：

1. **能访问项目文件** —— 让它读一个已知文件，核对内容
2. **能搜索代码** —— 让它找一个已知符号，核对命中位置
3. **能获得代码诊断** —— 故意写一个类型错误，看它是否在编辑后立刻发现
4. **MCP 一致** —— 让它用 Context7 查一个库的最新文档

第 3 项在 Claude Code 上会显示 `Found N new diagnostic issues in M files`，按 **Ctrl+O** 可以自己看。

> Claude Code 装完插件后**必须** `/reload-plugins` 或重启，当前会话不会自动加载。
> Cursor 装完扩展后需重启窗口。
> Godot 的 LSP 只在 **Godot 编辑器打开时**可用（TCP `127.0.0.1:6005`）。
