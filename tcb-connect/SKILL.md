---
name: tcb-connect
description: 连接腾讯云开发（CloudBase/TCB）并操作数据库、云函数、存储等服务。当需要查询或写入云开发数据库、调用云函数、管理云存储、切换环境（dev/prod），或排查 CloudBase MCP 连接问题时使用。适用于 Claude Code、OpenAI Codex CLI 等所有 AI agent。
---

# 连接腾讯云开发（TCB/CloudBase）

## 项目环境

| 别名 | 环境 ID | 用途 |
|------|---------|------|
| dev  | `dev-5gzz7rxdbcf5d7dc`  | 开发测试 |
| prod | `prod-6gv6kwxe65437245` | 生产（谨慎操作）|

AppID: `wx05415d4201a4c7c8`，区域: ap-shanghai

---

## 核心原则：用 mcporter 而非原生 MCP

Claude Code 的原生 MCP 工具加载不稳定（`ToolSearch` 可能找不到 `mcp__cloudbase__*`）。**统一用 `mcporter` CLI 调用**，在任何 agent 环境都可靠。

```bash
npx mcporter list   # 预期输出包含 cloudbase (36 tools)
```

---

## ⚠️ 切换环境的正确方式

**最关键的坑：** `CLOUDBASE_ENV_ID` 环境变量前缀（如 `CLOUDBASE_ENV_ID=prod-xxx npx mcporter call ...`）**不能真正切换环境**。原因是 `~/.claude/settings.json` 里的 `mcpServers.cloudbase.env.CLOUDBASE_ENV_ID` 在 MCP server 启动时已注入，会覆盖命令行前缀。

**正确切换方式：修改 `~/.claude/settings.json`**

```json
"cloudbase": {
  "command": "npx",
  "args": ["-y", "@cloudbase/cloudbase-mcp@latest"],
  "env": {
    "INTEGRATION_IDE": "ClaudeCode",
    "CLOUDBASE_ENV_ID": "prod-6gv6kwxe65437245"   ← 改这里
  }
}
```

修改后无需重启，下一条 mcporter 命令立即生效。

### 验证当前连接的是哪个环境

```bash
npx mcporter call cloudbase.auth action=status --output json
```

看 `current_env_id` 字段，必须与目标环境一致再继续操作。**任何写操作前都要先做这个验证。**

---

## 常用操作

### SQL 查询（只读）

```bash
npx mcporter call cloudbase.querySqlDatabase action=runQuery "sql=SELECT * FROM map_poi LIMIT 5" --output json
```

> ⚠️ action 必须是 `runQuery`（文档有时写 `getEnvInfo` 等旧名称，是错的）

### SQL 写入 / 删除

```bash
npx mcporter call cloudbase.manageSqlDatabase action=runStatement "sql=DELETE FROM map_poi WHERE ..." --output json
```

### SQL 很长时（如 IN 几百个值）：写文件再传

直接把长 SQL 写入文件，用 `$(cat file.sql)` 传参，避免 shell 参数长度限制：

```bash
echo "SELECT COUNT(*) FROM map_poi WHERE name IN ('名称1','名称2',...)" > /tmp/query.sql
SQL=$(cat /tmp/query.sql)
npx mcporter call cloudbase.querySqlDatabase action=runQuery "sql=$SQL" --output json
```

### 查看环境信息

```bash
npx mcporter call cloudbase.envQuery action=info --output json
```

### 列出所有可用工具

```bash
npx mcporter describe cloudbase --all-parameters 2>&1 | head -100
```

---

## 生产环境操作规范

对 prod 做任何写操作前，必须按顺序完成：

1. **确认环境** — `auth action=status` 确认 `current_env_id` 是 prod
2. **备份数据** — 分页导出全表到本地 JSON（见下方备份脚本）
3. **COUNT 验证** — 用 SELECT COUNT 确认即将影响的行数符合预期
4. **抽样核对** — SELECT 几条样本数据，人工确认字段内容符合预期
5. **执行写操作** — 分批执行（每批 ≤500 条），记录每批 `rowsAffected`
6. **最终验证** — 写操作后再次 COUNT，确认结果与预期一致

### 分页备份脚本（bash）

```bash
offset=0; page=500; total=0
mkdir -p /tmp/tcb_backup_parts

while true; do
  SQL="SELECT * FROM <table> LIMIT $page OFFSET $offset"
  result=$(npx mcporter call cloudbase.querySqlDatabase action=runQuery "sql=$SQL" --output json 2>&1)
  cnt=$(echo "$result" | grep -o '"_id"' | wc -l)
  [ "$cnt" -eq 0 ] && break
  echo "$result" > "/tmp/tcb_backup_parts/part_${offset}.json"
  total=$((total + cnt)); echo "offset=$offset cnt=$cnt total=$total"
  offset=$((offset + page))
  [ "$cnt" -lt "$page" ] && break
done
echo "备份完成，共 $total 条"
```

然后用 Node.js 合并 parts：

```javascript
const fs = require('fs');
const parts = fs.readdirSync('/tmp/tcb_backup_parts').sort((a,b) =>
  parseInt(a.replace('part_','')) - parseInt(b.replace('part_','').replace('.json',''))
);
const allRows = parts.flatMap(p => {
  const j = JSON.parse(fs.readFileSync('/tmp/tcb_backup_parts/' + p, 'utf8'));
  return j.data?.rows || [];
});
fs.writeFileSync('backup.json', JSON.stringify({ total: allRows.length, rows: allRows }, null, 2));
```

---

## 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| `ToolSearch` 找不到 cloudbase 工具 | 原生 MCP 加载失败 | 改用 `npx mcporter call cloudbase.*` |
| `envQuery` 返回的 EnvId 与预期不符 | settings.json 里 CLOUDBASE_ENV_ID 未改 | 修改 `~/.claude/settings.json` 对应字段 |
| `set_env` 成功但下一条命令还是旧环境 | settings.json 注入的 env var 覆盖了 set_env | 同上，改 settings.json 才是根本解法 |
| `invalid_enum_value` 错误 | action 名称错误（文档过时） | 用 `npx mcporter describe cloudbase --all-parameters` 查正确名称 |
| SQL 参数太长报 EINVAL | Windows 命令行参数长度限制 | 把 SQL 写入文件，用 `$(cat file.sql)` 传参 |
| `auth_status` 不是 READY | 登录态失效 | `npx mcporter call cloudbase.auth action=start_auth authMode=device --output json` |
