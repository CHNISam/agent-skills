---
name: clash-verge-claude-routing
description: Configure or repair Claude, Claude Code, and Anthropic traffic routing in Clash Verge Rev on Windows when domains take mixed exits or the user needs a fixed exit or manual country-restricted proxy choices.
---

# Clash Verge Claude Routing

Route Claude traffic through a dedicated selector in Rule Mode. Default to one fixed leaf; when requested, provide multiple explicitly approved leaf nodes for manual switching. Never add automatic fallback or a general proxy group.

## Workflow

1. Read [routing-policy.md](references/routing-policy.md) for endpoint coverage, official sources, and validation criteria. Recheck official sources when updating coverage.
2. Preview the active subscription and resolved exit without writing:

```powershell
& '<skill-dir>\scripts\configure_clash_verge_claude.ps1' -WhatIf
```

3. Record the reported profile UID before the user switches subscriptions. Apply with `-ExpectedProfileUid '<uid>'` to refuse changes to the wrong subscription. The script operates on the active profile only. If the intended profile is now inactive, do not modify the replacement subscription: use the already identified enhancement files with backup and offline validation, or wait for an authorized switch back.
4. For a fixed exit, pass `-ProxyName '<exact node name>'`. For requested manual alternatives, pass an explicit list of leaf names:

```powershell
& '<skill-dir>\scripts\configure_clash_verge_claude.ps1' -ExpectedProfileUid '<uid>' -ProxyNames @('<verified US node 1>', '<verified US node 2>') -WhatIf
```

When a country restriction applies, verify each candidate's actual egress country before adding it; a flag or node label is insufficient. Probe through a separate local-only Mihomo instance with each listener pinned to one leaf, no TUN, no system proxy changes, no controller, and unmatched traffic rejected. Never rotate the live GLOBAL selector to run tests. Record source, timestamp, IP and country; distinguish independent geolocation failures from contradictory results. Exclude unverified or contradictory candidates. Tests describe the observed exit, not its future location or provider reputation.

5. Once routing changes are authorized, repeat the exact reviewed command without `-WhatIf`, adding `-Confirm:$false`. The default backs up and writes profile enhancements without restarting or reloading Clash.
6. Reload only after explicit authorization for a brief network interruption. Otherwise report `PendingReload: true`; an inactive profile loads enhancements when the user selects it. Do not restart the user's replacement subscription merely to refresh an inactive one.
7. Report the backup path. After loading, test the generated configuration with Mihomo, verify Rule Mode and the allowed selector candidates, then inspect fresh service logs for actual traffic using `Claude[<approved node>]`. A 4xx HTTP response can establish routing with corresponding logs; do not send quota-consuming model requests without authorization.

## Invariants

- Modify subscription enhancement files, not generated `clash-verge.yaml`; preserve unrelated entries and keep managed blocks idempotent.
- Keep local/private exclusions ahead of the process fallback for local MCP access. Set `find-process-mode: always`.
- Cover all six official suffixes, documented API networks, precise telemetry hosts, and Claude executable names from the reference. Do not route entire shared telemetry/CDN providers indiscriminately.
- Candidates must be real leaf proxies. Reject DIRECT, REJECT, PASS, missing nodes and unresolved groups. Use manual `select`, never fallback, load balancing or URL testing for Claude.
- A configured rule covers traffic reaching Clash; inspect the requested client's proxy/TUN path and verify runtime logs before claiming end-to-end coverage. Node selection and country checks cannot establish nationality or guarantee protection from account enforcement.

## Validation and rollback

Run `scripts/test_claude_routing.ps1` after script changes; it uses temporary fixtures and mock controller responses without touching live configuration.

Restore the script's backup without interrupting traffic:

```powershell
& '<skill-dir>\scripts\configure_clash_verge_claude.ps1' -RestoreBackup '<backup-directory>' -Confirm:$false
```

Add `-ReloadNow` only with explicit interruption authorization. Report pending reload otherwise.
