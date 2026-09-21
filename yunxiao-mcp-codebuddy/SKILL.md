---
name: yunxiao-mcp-codebuddy
description: 在 CodeBuddy IDE 中配置、验证和排查阿里云云效（Yunxiao）MCP。当需要接入 `https://openapi-rdc.aliyuncs.com/ai/mcp`、MCP 面板出现 `Needs authentication` / `OAuth authorization required` / `streamableHttp connect failed` / `missing Yunxiao access token`、昨天已 PASS 今天又连不上、CLI 注册成功但 IDE Agent 看不到 server、server 可见但 tools 数为 0，或浏览器显示 `Authentication Successful` 而 IDE 仍不连通时使用。
---

# Yunxiao MCP × CodeBuddy IDE

只解决一件事：让 CodeBuddy IDE 内置 Agent 真正连上云效 MCP，并能区分「配置来源 / 认证 / 会话快照 / 服务端」四类故障。

**不覆盖**：云效项目管理、测试用例与测试计划的业务操作、需求导入。那些属于业务 Skill。

## 1. 推荐配置：纯 OAuth，不带任何 header

```json
{
  "yunxiao": {
    "type": "http",
    "url": "https://openapi-rdc.aliyuncs.com/ai/mcp"
  }
}
```

- 中心站 Endpoint：`https://openapi-rdc.aliyuncs.com/ai/mcp`，Streamable HTTP。
- 服务端标识：`alibabacloud-devops-mcp-server`。不加 toolsets 过滤时暴露全部 7 个 toolset（organization / project / test / code / pipeline / packages / application-delivery），实测约 203 个 tools。
- **不要写 `Authorization` header，不要写 `Bearer ${YUNXIAO_PAT}`**。

原因（已验证）：静态 Bearer header 与 IDE 的 OAuth 流程冲突。IDE 认为「已配置鉴权」但仍收到 401，于是卡在 `Needs authentication` —— 浏览器 OAuth 即使显示 `Authentication Successful`，callback 后的 token 也不会落盘，最终报
`streamableHttp connect failed: OAuth authorization required for yunxiao, please connect manually`。
删掉 header 后 IDE 即可完成 OAuth 绑定并取到 tools。

两份配置必须**同时**保持无 header。只改 IDE 读的那份、漏掉 `.mcp.json`，残留的 `Bearer ${VAR}` 在环境变量缺失时会展开成空 token，表现为 `Unauthorized: missing Yunxiao access token`，很容易误判成「OAuth 又坏了」。

## 2. 配置来源：先确认 IDE 真正读哪份文件

同一台机器可能同时存在多份 user-scope 配置，**不要凭 CLI 默认路径猜 IDE 用哪份**。

| 文件 | 已验证行为（当前 CodeBuddy 环境） |
|---|---|
| `~/.codebuddy/mcp.json` | IDE 内置 Agent 实际据以注册 server 的那份 |
| `~/.codebuddy/.mcp.json` | CLI `--scope user` 曾写入的那份（含点号） |
| `~/.codebuddy.json` | 本例不存在 |

这不是不可变事实，版本可能变。**每次都按下面的方法确认**：

1. 找一个 IDE **已成功加载** 的 MCP（如 `context7`），读它的 `configSource` / 所在文件。
2. 以那份文件的 `mcpServers` 作为 Source of Truth。
3. 把 `yunxiao` 加进**同一份** `mcpServers`。

典型症状：CLI 报 `Added http MCP server yunxiao to user config` 且 `mcp list` 显示 Connected，但 IDE Agent 仍报 `Server 'yunxiao' not found or not connected` —— 写进了 IDE 不读的那份文件。

## 3. 症状 → 根因判定表

| 现象 | 故障层 | 判据 | 动作 |
|---|---|---|---|
| `Server 'x' not found or not connected` | 配置来源 / 会话快照 | server 未注册进 IDE 读的那份文件 | 加进正确文件 → Reload Window |
| `Tool 'y' not found in server 'x'`（server 可见） | 连接未完成或鉴权失败 | 已注册但 tools 数为 0 | 走 OAuth 排查（第 4 节） |
| `Needs authentication` + 浏览器 `Authentication Successful` | OAuth token 未持久化 | 日志无 callback/token，凭据库无该 server | 删 header → 重新 Connect |
| `streamableHttp connect failed: OAuth authorization required ..., please connect manually` | OAuth 未绑定 | 同上 | 同上 |
| `invalid or expired Yunxiao access token`（-32001） | PAT 无效或过期（仅 PAT 模式） | MCP 错误体 | 换 PAT。**不要**据此推断 token 属于哪种类型，只陈述「被 MCP 拒绝」 |

Server visible + 401 → 认证/环境变量问题；Server completely absent → 配置来源或格式问题。**两类不要混为一谈。**

## 4. 定位 OAuth 失败发生在哪一步

浏览器 Success ≠ token 交换/落盘成功。按顺序取证：

1. **是否收到 callback** — 日志里搜 `oauth|callback|authorization_code|pkce`。
2. **是否 exchange 成 token** — 搜 `access_token|refresh_token|exchange`。
3. **是否写入凭据** — 搜 `credential|store|cache`，并直接查 `~/.codebuddy/security`、`~/.codebuddy/local_storage`、IDE 用户数据目录下的 `Local Storage/leveldb` 是否出现该 server 名。
4. **reconnect 是否读到** — 日志里该 server 是否进入 connected 列表。

日志位置：

| 位置 | 内容 |
|---|---|
| `~/.codebuddy/logs/<date>/<workspace>__<hash>.log` | CLI/agent 进程，含 `[MCP][envExpand]`、`getConnectedServers()` 等真实连接记录 |
| IDE 用户数据目录 `logs/<timestamp>/window1/**` | GUI 进程；**会回显你自己执行的命令**，检索时要排除 `Select-String` / `TerminalExecutor` / `StreamParser` 之类噪声行 |

`[MCP][envExpand] ... headers=[Authorization=Bear…(len=71)]` 说明 `${VAR}` 已被展开（71 = `Bearer ` + 64）；凭据库里查不到该 server 名，就证明 token 从未落盘。

## 4.1 OAuth 登录态不持久化：PASS 之后也会再挂

已验证：yunxiao 的 OAuth token 只存在于 MCP client 进程内存，凭据库里查不到。IDE 或 MCP 进程重启、reconcile 重连后 token 即失效，症状是昨天刚 PASS、今天每个调用都报：

```
{"code":-32001,"message":"Unauthorized: missing Yunxiao access token"}
```

此时 `mcp_get_tool_description` 仍能返回 tool schema（registry 有缓存），**不要据此认为已连通** —— 只有实际 `tools/call` 成功才算连通。

能自己做的（通常无效，但可排除配置因素）：touch 配置 mtime 触发重载、`disabled: true → false` 重连循环。
真正有效的只有一条：**Settings → MCP → yunxiao → Connect，重新走浏览器 OAuth**。工具调用无法代替浏览器授权（错误原文 `please connect manually`）。

## 5. 最小修复动作（按序，不要跳步）

1. 确认 `yunxiao` 位于第 2 节确定的那份 `mcp.json`。
2. 只删该条目的 `headers`（`Authorization` / `${YUNXIAO_PAT}` / 手工 Bearer），保留 `type` + `url`。
3. 在 MCP 面板对 `yunxiao` 点 Connect，完成浏览器 OAuth。
4. 仍不通 → Reload Window（新会话会重新初始化 MCP）。

禁止：清除其他 MCP 的认证状态、全局重置配置、把 PAT 写回配置、批量迁移其他 server。

## 6. 只读验证（判定 PASS 的唯一标准）

```text
get_current_organization_info              → 取到 lastOrganization / userId
search_projects { organizationId, perPage } → 返回项目列表
```

要求：MCP 面板 Connected、tools 数 > 0、Agent 能直接看到 yunxiao tools、两个调用都返回真实数据。到此即停，不要扩散测试。

## 7. 凭据安全

- 优先 OAuth；PAT 只作为无法 OAuth 时的备选。
- PAT 不写进项目文件、不写进仓库、不打印完整值、不进 Git。
- 验证阶段只做只读调用，不创建/修改工作项、用例、MR、流水线、部署。

## 8. 写入云效时的 API 级事实（避免 400 反复重试）

只记 API 行为，不记业务流程 —— 项目管理/测试用例的业务操作不属于本 Skill。

- `create_work_item` 的 `assignedTo` **必填**。没有真实负责人时只能填当前用户，并在报告里标注「非真实指派」，不要编造。
- 缺陷（Bug）类型额外**必填 `seriousLevel`**，否则 400 `字段【严重程度】不能为空`。枚举 id 因项目而异，先 `get_work_item_type_field_config` 取。
- 优先级走 `customFieldValues: {"priority": "<optionId>"}`，枚举同样取自字段配置（紧急/高/中/低）。
- **状态枚举随工作项类型走不同工作流**：Task/需求默认「待处理」，缺陷默认「待确认」。不要用 Task 的状态 id 去写缺陷，用 `get_work_item_workflow` 按类型取。
- `search_workitems` 返回的 `description` 是空串，**读详情要用 `get_work_item`**。
- `create_version` / `update_version` **不暴露 status 字段** —— 版本「已发布 / 归档」只能在云效 UI 操作，不要试图用 API 伪造。
- 没有创建标签（label）的 API。需要保留 P0–P3 之类语义时，写进描述首行，不要假设能建 label。

## 9. 已验证的服务端事实（避免重复探索）

- 7 个 toolset 默认全开，无需 `toolsets` 参数。
- `search_projects` / `search_workitems` 等返回 HTTP 200 但列表为空时，是数据为空，不是功能不可用。
- `get_testcase` 对 `testSteps` 为空的用例返回 `-32603`（服务端响应校验），读单条用例改用 `search_testcases`。
- `search_workitems` 的 `category` 枚举是 `Req` / `Task` / `Bug`；传小写不报错但返回 0 条。
