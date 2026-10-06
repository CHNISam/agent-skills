---
name: claude-code-multi-account
description: Configure isolated Claude Code account entry points in native Windows PowerShell with an official per-account CLAUDE_CONFIG_DIR, preserving the default account and current sessions.
---

# Claude Code multi-account

> **Status: Stable for this scoped Windows PowerShell pattern.** The account-directory
> isolation and environment-variable cleanup have been validated. This skill does not
> authenticate an account or make unrelated credential sources distinct.

Use this skill when a person wants separate Claude Code account entry points on one
Windows machine, such as the default claude command plus a claude2 command. Use only the
official Claude Code configuration-directory mechanism; do not install account switchers
or replace the Claude Code binary.

## Official basis

Read the current official documentation before changing configuration:

- [Authentication: Log in with multiple accounts](https://code.claude.com/docs/en/authentication)
- [Environment variables: CLAUDE_CONFIG_DIR](https://code.claude.com/docs/en/env-vars)
- [Windows setup](https://code.claude.com/docs/en/setup)

Claude Code reads CLAUDE_CONFIG_DIR at startup. Each directory has separate settings,
session history, plugins, and its own Claude Code credential file. On Windows, setting
the variable also moves .credentials.json under the selected configuration directory.

## Preserve the default account

- Leave the existing claude command and its installed binary unchanged.
- Leave the default $HOME\.claude directory, its credentials, and active sessions
  untouched.
- Do not run /logout, move credentials, create a global wrapper, or use setx.
- Set CLAUDE_CONFIG_DIR only inside the alternate command invocation. In finally, restore
  a caller-provided value or remove the variable when it was originally absent.
- Do not launch Claude Code or complete login on the person's behalf. First launch of the
  alternate command is the person's login boundary.

## Add an idempotent PowerShell entry point

First inspect the actual $PROFILE in the shell the person uses. Do not assume that
Windows PowerShell 5.1 and PowerShell 7 share a profile path: they normally use
Documents\WindowsPowerShell and Documents\PowerShell respectively. Add the function to
the actual profile, preserving all unrelated profile content. Back up an existing profile
before editing it and use clear begin/end markers so repeated work replaces one block.

For an alternate account in $HOME\.claude-b, use this function:

~~~powershell
function claude2 {
    $hadClaudeConfigDir = Test-Path Env:CLAUDE_CONFIG_DIR
    $previousClaudeConfigDir = $env:CLAUDE_CONFIG_DIR

    try {
        $env:CLAUDE_CONFIG_DIR = Join-Path $HOME '.claude-b'
        & claude @args
    }
    finally {
        if ($hadClaudeConfigDir) {
            $env:CLAUDE_CONFIG_DIR = $previousClaudeConfigDir
        }
        else {
            Remove-Item Env:CLAUDE_CONFIG_DIR -ErrorAction SilentlyContinue
        }
    }
}
~~~

The function deliberately invokes the pre-existing claude command. Do not create,
rename, copy, or modify a claude executable, script, alias, or shim. Do not pre-create
the alternate directory merely for this setup; Claude Code creates the account-specific
state when the person first runs claude2.

## Verify without changing authentication

Reload the active profile, then confirm:

1. Get-Command claude still resolves to the pre-existing official Claude Code CLI.
2. Get-Command claude2 resolves to the new PowerShell function.
3. User, machine, and process scopes have no permanent CLAUDE_CONFIG_DIR value after
   verification.
4. The default $HOME\.claude directory still exists and was not moved, renamed, or
   modified.
5. A stubbed claude command receives $HOME\.claude-b during claude2, receives forwarded
   arguments, and observes the original environment state after both success and failure.

Use a stub for lifecycle verification rather than starting an interactive Claude session.
The user can then run claude2 and follow Claude Code's official login flow.

## Credential precedence and limitations

Before diagnosing an account-selection problem, inspect whether environment credentials
such as ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, CLAUDE_CODE_OAUTH_TOKEN, or cloud-provider
selection variables take precedence over a Claude Code login. Report them and do not
change them without explicit authorization.

Separate configuration directories do not keep two Claude Console sign-ins without an API
key apart, because that credential type is stored outside the configuration directory.
Consult the current Authentication documentation if that login type is involved.
