---
name: codex-network-permissions
description: Diagnose and persist Codex CLI GitHub network permissions, including isolated Codex2 profiles on Windows, while retaining workspace-write and on-request. Use when sandbox requests fail or temporary startup flags work but normal new sessions cannot connect.
---

# Codex 网络权限修复

目标：在指定 Codex 配置目录中最小修复网络权限，并证明正常新会话中的 Git 和 API 请求实际成功。

## 确认配置归属

检查启动入口、CLI 版本、`CODEX_HOME`、实际配置文件和项目/托管配置覆盖。
Codex2 通常由独立启动器设置 `CODEX_HOME=~/.codex2`，但应读取入口确认，不能根据名称猜测。
不要输出认证文件、令牌或完整进程环境。不要改主账号、代理、系统权限、项目代码或其他 Session。

读取当前版本的[官方配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)；权限字段和新式权限配置的优先级可能随版本变化。

## 先实际验证

在当前沙盒默认权限下分别执行只读请求，记录命令、退出码和输出：

```powershell
git ls-remote https://github.com/openai/codex.git HEAD
gh api --include repos/openai/codex --jq .full_name
```

成功证据是 Git 返回 HEAD 且退出码为 0，以及 API 返回 HTTP 200、仓库名且退出码为 0。
`gh` 不可用时可用现有 HTTPS 客户端请求同一公开 API，保留 HTTP 状态和响应字段；不要为此安装额外工具。

若失败，区分沙盒网络策略、本机代理可达性、TLS、认证和上游错误。必要时，在已有授权或通过环境审批后，仅在沙盒外重试同一只读请求作对照；对照成功不等于沙盒验证成功。

Windows 的 `SEC_E_NO_CREDENTIALS` / `AcquireCredentialsHandle` 是 Schannel 凭据获取错误，不能直接判为 GitHub 认证失败。可临时用 `git -c http.sslBackend=openssl ls-remote ...` 比较 TLS 后端，但不修改 Git 全局配置、不关闭证书验证，也不把临时后端成功当成普通 Git 已修复。

如果普通 Git/API 验证仍失败，定位并报告剩余阻塞；不通过关闭沙盒、全局完全访问或改系统权限绕过。

## 最小持久化

验证通过后，只更新用户指定的配置文件，保留其他字段、注释及现有 Windows 沙盒实现。
适用传统配置且无冲突覆盖时，使用以下官方字段：

```toml
# 顶层，必须放在任何 [table] 之前
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
```

存在同名字段或表时原位修改，避免重复表、重复键或把顶层键写入其他表。
已有命名权限配置或托管约束时按当前官方文档解决实际优先级，不叠加互相冲突的配置。
配置在可写目录之外时走环境的文件系统审批。不要加代理、启动钩子、额外守护进程或修改启动器来代替持久配置。

## 验证新会话实际生效

另起独立会话，使用同一启动入口和 `CODEX_HOME`，不传 `-c`、`-s`、`-a`、`--approve-for-me` 或其他权限覆盖参数。不 resume、停止或操作已有 Session。

验证有效策略为 `on-request`、`workspace-write`、网络开启，然后在新会话默认沙盒权限下重新执行普通 Git 和 API 请求。TOML 解析成功或沙盒外成功均不足以完成验证。

重要：`codex exec` 可能强制采用 `never`，即使配置中是 `on-request`。不要据此覆盖持久配置，也不要把 exec 当成审批策略的完整验证。
需要程序化验证时，可按[官方 app-server 协议](https://learn.chatgpt.com/docs/app-server)启动独立 stdio app-server：

- 使用当前版本支持的 `--no-daemon`，避免接入共享 daemon。
- 完成 `initialize` / `initialized`，通过 `config/read` 检查有效配置。
- `thread/start` 只指定工作目录和临时会话，不覆盖权限；检查返回的 `approvalPolicy` 和 sandbox 网络策略。
- `turn/start` 要求只读 Git/API 测试，检查实际命令完成事件的输出和退出码，不只相信模型总结。
- 只关闭自己创建的测试进程；临时验证脚本不属于常驻修复机制。

Windows `.cmd` 启动器可能改变含 `%` 的参数，PowerShell 的原生命令参数也需正确引用。curl 若进入意外密码提示，停止该测试，不输入凭据；保留异常证据，使用参数明确的公开 API 请求区分调用问题与网络失败。

## 完成报告

只报告是否修复、具体配置文件、无权限覆盖的新会话有效策略、Git HEAD/退出码、API HTTP 状态/退出码和未解决问题。
当前旧会话的权限不会因文件修改自动刷新；未来新会话成功不应被旧会话失败否定，也不能宣称旧会话已同步修复。
