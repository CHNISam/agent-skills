# Claude Code 多账号（Windows）

本流程只管理 **Claude Code 终端 CLI** 的账号隔离；不配置 Codex，也不承诺 VS Code
扩展宿主或其他 GUI 客户端会沿用同一会话选择。

## 采用的官方机制

Anthropic 官方将 [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/en/env-vars#claude_config_dir)
定义为覆盖默认 `~/.claude` 的配置目录，并明确列为“多个账号并行”的用途。其[多账号登录文档](https://code.claude.com/docs/en/authentication#log-in-with-multiple-accounts)
也采用同一模式：保留普通 `claude`，以设置该变量的第二入口启动另一账号。

Windows 上，这意味着每个目录分别保存 settings、历史、插件和登录状态；认证由
`/login` 与 `/logout` 管理，而不是复制认证文件或 token。参见[凭证管理](https://code.claude.com/docs/en/authentication#credential-management)
与 [Claude 目录说明](https://code.claude.com/docs/en/claude-directory)。这些目录包含明文历史，
应放在用户目录、受操作系统权限保护，且永远不放进 Git。

不要把 `CLAUDE_CONFIG_DIR` 写成用户级环境变量：那会同时改变原有 `claude`。本 Skill
创建的 `.cmd` launcher 用 `setlocal`，仅把变量传给其子进程，退出后不会改调用者环境。
验证前也不能在调用进程设置 `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN` 或
`CLAUDE_CODE_OAUTH_TOKEN`；这些[认证覆盖项的优先级](https://code.claude.com/docs/en/authentication#authentication-precedence)
高于目录内的登录状态，会使两个入口实际使用同一身份。`Verify` 还拒绝云提供商选择
`CLAUDE_CODE_USE_BEDROCK`、`CLAUDE_CODE_USE_VERTEX`、`CLAUDE_CODE_USE_FOUNDRY`，以及
profile / federation 选择 `ANTHROPIC_PROFILE`、`ANTHROPIC_FEDERATION_RULE_ID`、
`ANTHROPIC_ORGANIZATION_ID`。

这是对**已知进程级选择变量**的保守检查：不要为了通过验证而删除组织强制的配置。若机器还使用
`apiKeyHelper`、未命名的 active Anthropic profile、gateway 或受管理登录策略，脚本不会读取或修改
这些外部状态，不能把本 Skill 的目录检查当成账号隔离证明；按官方说明在交互式 `/status` 中确认
实际认证来源。

## 适用边界

此方法适用于 Claude.ai 的 OAuth/订阅账号，或各自使用 API key 的 Console 流程。官方特别
说明：两个**没有 API key 的 Claude Console 登录**不能只靠不同目录隔离，因为该登录位于
目录之外。发现该情形时不要声称多账号已隔离；先按官方认证文档选择适用的方案。

不要设置、复制或提交 `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、
`CLAUDE_CODE_OAUTH_TOKEN`、OAuth token 或任何认证文件。

## Discovery

先在含本 Skill 的 worktree 中定位脚本，并检查将要使用的名字、目录和 launcher 状态：

```powershell
$script = '<skill-dir>\scripts\manage_claude_code_account.ps1'
& $script -Action Discover -Name claude2 -ConfigDirectory (Join-Path $HOME '.claude-b')
```

`Discover` 只报告路径、是否在 `PATH`、是否已有受管理 launcher、调用进程的认证覆盖变量**名称**，
以及主目录和目标目录是否不同；它不会输出或持久化认证内容或变量值。Windows 默认主账号目录是
`$HOME\.claude`；若调用进程临时设置了 `CLAUDE_CONFIG_DIR`，以结果中的
`PrimaryConfigDirectory` 为准。若已存在第二账号目录（例如旧方案的 `$HOME\.claude-b`），
迁移时必须显式传入该路径，而不是创建另一个空目录。

默认不传 `-ConfigDirectory` 时，未来账号使用 `$HOME\.claude-profiles\<name>`；因此
`claude3`、`claude4` 可以沿用同一机制。

## Apply

为现有第二账号创建一个任意 shell 都能找到的 `claude2.cmd`：

```powershell
& $script -Action Apply -Name claude2 -ConfigDirectory (Join-Path $HOME '.claude-b') -Confirm:$false
```

脚本从当前 `claude.cmd` 的目录创建同级 launcher，透传所有参数和退出码。它要求该目录已在
`PATH`，拒绝替换 `claude` 本身、拒绝覆盖未受管理的同名 launcher，并且同一映射重复运行时不改文件。
它只创建空配置目录和受管理的 launcher；首次运行 `claude2` 后，再用官方 `/login`
完成该目录的登录。不要从主账号复制登录状态。

为避免 Windows PowerShell 与 PowerShell 7 的文件编码差异，launcher 只写入 ASCII 的 Windows
环境变量路径表达式（通常是 `%USERPROFILE%\...` 或 `%APPDATA%\...`）。因此把账号目录放在用户
目录中；如果一个外部路径含无法安全写进 `.cmd` 的非 ASCII 字符，脚本会在写入前拒绝，而不是生成
会指向错误目录的入口。

如果 profile 中已经存在同名 PowerShell 函数，它会优先于 `.cmd`。`.cmd` 仍为 CMD、无
profile shell、或因执行策略未加载 profile 的 PowerShell 提供稳定入口；`Verify` 会实际检查
当前 PowerShell 所解析的入口是否也报告目标配置目录。不要手改函数去复制凭证。

## Verify

```powershell
& $script -Action Verify -Name claude2 -ConfigDirectory (Join-Path $HOME '.claude-b')
```

验证会检查受管理 launcher、配置目录分离、原有 `claude`、`cmd.exe` 和当前 PowerShell 实际
解析的 `claude2` 入口、caller 环境未被 launcher 改变，以及各入口通过 `auth status --json`
报告的有效目录。它要求已登录，且在存在认证覆盖变量时直接失败；不会输出该 JSON（其中可能
含个人账号信息）。
成功结果中的 `LoggedIn` 为 `True`。如需排查设置，使用官方的只读
[`claude doctor`](https://code.claude.com/docs/en/debug-your-config)；`/status` 只应在交互终端
中查看，避免把邮箱、组织或订阅信息复制到日志或 Git。

在实际 shell 中也分别启动 `claude` 和 `claude2`。`claude` 必须仍指向结果中的
`PrimaryConfigDirectory`（通常是 `$HOME\.claude`），`claude2` 必须指向它的独立目录。对
新账号重复 `Apply` 时只替换名称，例如：

```powershell
& $script -Action Apply -Name claude3 -Confirm:$false
claude3
```

## Rollback

```powershell
& $script -Action Rollback -Name claude2 -ConfigDirectory (Join-Path $HOME '.claude-b') -Confirm:$false
```

Rollback 只删除内容仍与所给 `Name` / `ConfigDirectory` 映射完全一致的受管理 `claude2.cmd`，
并保留独立配置目录和登录状态，避免误删认证或历史。它拒绝删除同名但非本 Skill 创建或已被改动
的 launcher。要停用一个账号，只需删除入口；仅在用户
明确决定丢弃该账号状态时，再由用户自行处理其目录。
