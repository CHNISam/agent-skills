# Native CLI notes

Verified starting point: Windows PowerShell, OpenCode 1.18.24, `opencode/deepseek-v4.1-flash-free`, `--variant max`, JSON tool events. Recheck installed help/model metadata; these are not permanent service guarantees.

## Process-scoped cost lock

Run in a dedicated child process, or restore the previous environment value in `finally`:

```powershell
$hadOverride = Test-Path Env:OPENCODE_CONFIG_CONTENT
$previousOverride = $env:OPENCODE_CONFIG_CONTENT
try {
    $env:OPENCODE_CONFIG_CONTENT = @'
{
  "model": "opencode/deepseek-v4.1-flash-free",
  "small_model": "opencode/deepseek-v4.1-flash-free",
  "enabled_providers": ["opencode"],
  "provider": {"opencode": {"whitelist": ["deepseek-v4.1-flash-free"]}},
  "share": "disabled"
}
'@
    # Add task-specific permissions before executing; this example only locks cost.
    $safe = opencode debug config | ConvertFrom-Json
    if ($safe.model -ne 'opencode/deepseek-v4.1-flash-free' -or
        $safe.small_model -ne $safe.model -or
        @($safe.enabled_providers).Count -ne 1 -or
        $safe.enabled_providers[0] -ne 'opencode' -or
        @($safe.provider.opencode.whitelist).Count -ne 1 -or
        $safe.provider.opencode.whitelist[0] -ne 'deepseek-v4.1-flash-free') {
        throw 'Free model lock did not take effect'
    }
    # The prompt file contains the explicit task contract, never credentials.
    opencode run --dir $taskWorktree --model opencode/deepseek-v4.1-flash-free `
        --variant max --format json (Get-Content -Raw $taskPromptFile) `
        1> $taskEventsFile 2> $taskErrorsFile
    $taskExitCode = $LASTEXITCODE
} finally {
    if ($hadOverride) { $env:OPENCODE_CONFIG_CONTENT = $previousOverride }
    else { Remove-Item Env:OPENCODE_CONFIG_CONTENT -ErrorAction SilentlyContinue }
}
```

If an existing process override contains needed task constraints, merge intentionally rather than discarding them. Define task paths outside the quoted JSON; use native structured argument passing, not string-built shell commands with untrusted prompt text. Prefer prompt files over complex shell escaping.

## Permission matching

OpenCode merges global/project/process configuration. Later matching rules win; specific inherited allows may survive an apparent catch-all deny. Inspect effective fields, not just the input file. Permissions are not an OS sandbox.

- Avoid a late top-level `"*": "deny"` that unintentionally hides all tools, including ones you attempted to allow.
- In each path/command map, place the catch-all deny first and allowed targets afterward. Include repository/worktree-relative paths where matching uses relative paths; absolute-only allowlists failed in linked Windows worktrees in the observed trial.
- Permit the repository's required startup instruction query and required read paths. Restrict edits to the slice and tests to specific commands; deny recursive delegation and unrelated network tools for ordinary local slices.
- On a denied call, inspect its actual tool name and path. Correct the authorized allowlist once and restart a short slice; do not tell the executor to bypass permissions through another tool.

## Minimal evidence

Capture JSONL and stderr separately, plus status/diff before and after. Summarize `tool_use` completed/error counts, `step_finish` reasons and costs, final report, process exit, and the independently run checks. Export a session only when needed; retain safe provider/model/variant/cost fields rather than unrelated conversation text or credentials.

For parallel trials record first/last event timestamps for each session, and verify their intervals overlap. Distinct session IDs and simultaneous process creation alone do not establish concurrent useful execution.

Official references: [configuration](https://opencode.ai/docs/config/), [permissions](https://opencode.ai/docs/permissions/). Verify alternative free models against their provider's current authoritative catalog before use.
