# Claude Code 项目级 MCP 启用

当一个项目在根目录放了 `.mcp.json` 声明 MCP 服务器后，Claude Code 还需要在用户态的项目级设置中显式启用这些服务器，它们才会真正连接。这个 skill 自动完成这个桥接。

## 背景

Claude Code 的 MCP 启用机制分两层：

1. **项目声明** — 项目根目录的 `.mcp.json`，定义有哪些 MCP 服务器及其启动方式
2. **用户启用** — `~/.claude/projects/<project-slug>/settings.local.json` 中的 `enabledMcpjsonServers` 数组，记录用户已批准启用的服务器名

两层都到位，MCP 服务器才会在会话中可用。这个 skill 处理的就是第二层。

## 操作步骤

### 1. 定位项目的 `.mcp.json`

从当前工作目录（或用户指定的项目路径）找到 `.mcp.json`，读取其中 `mcpServers` 的所有 key 作为服务器名列表。

如果找不到 `.mcp.json`，告知用户当前项目没有 MCP 声明文件，无需操作。

### 2. 计算项目 slug

Claude Code 用项目绝对路径生成 slug 作为设置目录名。规则是把路径中的 `:`、`/`、`\`、`.` 全部替换为 `-`。

例如：
- `D:/HW/litemall` → `D--HW-litemall`
- `C:\Users\me\my-app` → `C--Users-me-my-app`

设置目录路径为：`~/.claude/projects/<project-slug>/`

### 3. 读取或创建项目级设置

目标文件：`~/.claude/projects/<project-slug>/settings.local.json`

- **文件不存在**：创建新文件，内容为 `{ "enabledMcpjsonServers": [<服务器名列表>] }`
- **文件存在但没有 `enabledMcpjsonServers` 字段**：在现有 JSON 中添加该字段
- **文件存在且已有 `enabledMcpjsonServers`**：将 `.mcp.json` 中的服务器名合并进去（去重），保留已有的其他服务器

合并时保留文件中的其他所有字段不变，只动 `enabledMcpjsonServers`。

### 4. 确认结果

完成后告知用户：
- 启用了哪些服务器
- 设置文件写在了哪里
- 提醒用户需要重启 Claude Code 会话（或重新打开 `/mcp` 对话框）才能生效
