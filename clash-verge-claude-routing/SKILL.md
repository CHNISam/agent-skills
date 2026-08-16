---
name: clash-verge-claude-routing
description: This skill should be used when configuring or repairing Claude, Claude Code, or Anthropic traffic routing in Clash Verge Rev on Windows, especially when Rule Mode fails, Claude domains take mixed exits, or a fixed proxy node is required for IP consistency.
---

# Clash Verge Claude Routing

## Overview

Configure the active Clash Verge Rev profile so Anthropic traffic uses one dedicated, fixed proxy group in Rule Mode. Preserve local and private-network access, cover current Anthropic domains, add a Claude process fallback, validate the generated Mihomo configuration, and roll back automatically on failure.

## Workflow

1. Read `references/routing-policy.md` before changing routing policy or endpoint coverage.
2. Locate the bundled script at `scripts/configure_clash_verge_claude.ps1`.
3. Run a discovery-only preview first:

```powershell
& '<skill-dir>\scripts\configure_clash_verge_claude.ps1' -WhatIf
```

4. Review the reported active profile, enhancement files, and resolved fixed proxy. Pass `-ProxyName '<exact node name>'` when the current Global selection is not the intended long-term Claude exit.
5. Apply only after the user has authorized the routing change. The default writes and backs up profile enhancements without reloading Clash Verge, so active connections remain untouched:

```powershell
& '<skill-dir>\scripts\configure_clash_verge_claude.ps1' -ProxyName '<exact node name>' -Confirm:$false
```

6. Use `-ReloadNow` only when the user explicitly authorizes a brief Clash Verge interruption. Without it, report `PendingReload: true`; an inactive profile will pick up its enhancements when the user later selects it.
7. Report the backup path printed by the script. Keep backups under the Clash Verge configuration directory, never at a drive root.
8. After an authorized reload, verify real traffic from Claude Code or the requested Claude client. Prefer a harmless authenticated status check; use a minimal model request only when the user authorizes a request that may consume quota.
9. Inspect the latest Clash service log and require Anthropic connections to show `using Claude[<fixed node>]`. Treat route logs as proof of routing even when an unauthenticated HTTP probe returns 4xx or times out after the connection is established.

## Safety Rules

- Edit the active profile enhancement files, not the generated `clash-verge.yaml`, so subscription refreshes preserve the policy.
- Keep reload and mode switching opt-in. Never restart Clash Verge merely to validate while the user depends on its connection.
- Create a single-node `Claude` selector. Do not add automatic fallback; fail closed when the fixed node disappears.
- Keep localhost, loopback, RFC1918, CGNAT, and IPv6 local ranges ahead of the process rule so local MCP servers remain reachable.
- Route the four Anthropic-owned suffixes plus `claude.exe`; avoid routing all of `sentry.io` or unrelated shared telemetry domains globally.
- Set `find-process-mode: always` to make the Windows process fallback deterministic.
- Refuse `DIRECT`, `REJECT`, or an unresolved group as the fixed Claude node.
- Preserve unrelated enhancement entries and make managed blocks idempotent.
- Do not promise that fixed routing prevents account enforcement. State that it reduces mixed-exit risk only.

## Rollback

Restore a backup created by the script:

```powershell
& '<skill-dir>\scripts\configure_clash_verge_claude.ps1' -RestoreBackup '<backup-directory>' -Confirm:$false
```

Restore files without a reload by default. Add `-ReloadNow` only when the user authorizes interruption; otherwise report that the restored profile will take effect on its next normal load.
