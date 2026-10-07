---
name: codex-account-profiles
description: Configure or maintain separate local OpenAI Codex CLI account profiles on Windows using documented credential storage and a minimal scoped launcher. Use when adding, checking, or removing a secondary Codex profile; do not use for token migration, cross-agent profile systems, or ordinary project configuration.
---

# Codex Account Profiles

Set up an additional local Codex CLI account without changing the default `codex`
account. This skill is for Windows; do not copy its launcher details to another
operating system without checking that platform's current Codex behavior.

Keep the design small:

- leave the existing `codex` command and its default home alone;
- give each added command its own home, such as `codex2` → `%USERPROFILE%\.codex2`;
- authenticate each extra profile through the official `codexN login` browser flow.

Do not build an account manager, OAuth flow, service, or custom credential store.

## Discover before changing anything

Check the installed CLI and current official configuration documentation first. At a
minimum, inspect `codex --version`, `codex --help`, `codex login --help`, the current
login status, `CODEX_HOME`, and the non-secret configuration that selects credential
storage. Check only paths and file existence for authentication data; never print its
contents.

Do not assume a different `CODEX_HOME` alone isolates an account. Codex supports
`cli_auth_credentials_store` values such as `file`, `keyring`, `auto`, and
`ephemeral`; `keyring` can use operating-system credential storage. Consult the
[current configuration reference](https://developers.openai.com/codex/config-reference)
and, when behavior is unclear, the matching
[authentication storage implementation](https://github.com/openai/codex/blob/main/codex-rs/login/src/auth/storage.rs).

## Choose credential storage deliberately

When the current official CLI supports file storage, make the *new* profile explicit
before login by placing this in its own `config.toml`:

```toml
cli_auth_credentials_store = "file"
```

With that setting, the new profile's credentials belong under that profile's
`CODEX_HOME` (including its `auth.json`). Do not modify the default profile's config,
credentials, or login state.

If the active store is `keyring`, `auto`, or uncertain, do not claim isolation just
because two directories exist. First find the current official, supported configuration
for the new profile and confirm its login state. Never simulate separation by copying,
editing, or sharing `auth.json`, refresh tokens, access tokens, cookies, or API keys.

## Use a thin Windows launcher

Locate the real `codex` command before adding a launcher so it cannot recursively call
itself. When Codex is installed through the standard npm shims, a `codex2.cmd` placed
beside the real `codex.cmd` can use this pattern:

```bat
@ECHO off
SETLOCAL DisableDelayedExpansion

SET "CODEX_HOME=%USERPROFILE%\.codex2"
SET "OPENAI_API_KEY="
SET "CODEX_API_KEY="
SET "CODEX_ACCESS_TOKEN="

CALL "%~dp0codex.cmd" %*
EXIT /b %ERRORLEVEL%
```

The cleared variables matter only when this profile is meant to use its own ChatGPT
OAuth identity: they prevent a parent-shell API-key or access-token override. `SETLOCAL`
keeps those changes scoped to the child invocation. Preserve all arguments and the exit
code. Do not put this behavior in a PowerShell profile, set a persistent/global
`CODEX_HOME`, or alter the original `codex` shim.

For `codex3` and later, use a new command name and a matching new home such as
`.codex3`; create and log into each profile independently.

## Login and routine use

Let the user complete browser OAuth themselves:

```powershell
codex2 login
codex2
codex2 exec "..."
codex2 resume
```

Do not automate the browser flow or request credentials in chat.

## Keep verification proportionate

For an ordinary personal setup, confirm the original `codex login status` remains
normal, then check `codex2 login status`, one `codex2 exec` call, and a new terminal
session. If the user has an existing secondary session, `codex2 resume` should see it.
Running the installer/configuration a second time should not create duplicate launcher
or configuration entries.

Before reporting success, make sure credentials and profile homes are outside Git
worktrees and no secret-bearing file is staged or printed. A real `logout` or deletion
of the secondary profile removes its credentials, so obtain explicit confirmation first.
Removing a secondary launcher alone is the least invasive rollback; never log out,
reset, or rewrite the default account as part of that rollback.
