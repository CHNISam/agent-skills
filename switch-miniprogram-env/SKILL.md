---
name: switch-miniprogram-env
description: Switch and validate environments for WeChat miniprogram projects that use Tencent CloudBase/TCB cloud functions, project.config.json appid/cloud env settings, cloudbaserc.json envId, and app config files such as config.js. Use when the user asks to switch dev/test/prod environments, create or repair scripts/env-config.json or scripts/switch-env.ps1, check for mixed CloudBase env IDs/appids/domains after switching, or generalize environment switching for similar miniprogram stacks.
---

# Switch Miniprogram Env

## Core Workflow

1. Inspect the repository before editing:
   - Confirm the intended base branch and remote freshness if project instructions require it.
   - Locate `project.config.json`, `cloudbaserc.json`, app-level config files such as `config.js`, and cloud function roots such as `cloudfunctions/`.
   - Search for existing environment identifiers with `rg -n "envId|resourceEnv|appid|cloudDomin|cloudfunctions|CloudBase|tcb|云开发|环境"`.

2. Prefer a manifest-driven switch:
   - Use `scripts/env-config.json` as the source of truth.
   - Use `scripts/switch-env.ps1` as the deterministic switcher when the project is PowerShell-friendly.
   - If either file is missing, scaffold from `references/env-config-schema.md` and `scripts/switch-env.ps1`.

3. Never hard-code one project's IDs into the skill output:
   - Read actual `appid`, CloudBase env IDs, resource domains, and cloud function roots from the target repository.
   - Keep dev/test/prod names configurable. Do not assume only `dev` and `prod`.

4. Switch in check mode first when possible:
   - Run `powershell -ExecutionPolicy Bypass -File scripts/switch-env.ps1 <target> -CheckOnly`.
   - If running the bundled script without copying it into the project, pass `-RepoRoot <repo>` and `-ConfigPath <repo>/scripts/env-config.json`.
   - Review changed files and residual non-target values.
   - Only run without `-CheckOnly` after the check result is understood.

5. Validate after switching:
   - Re-run check mode for the target environment.
   - Search for non-target appids, env IDs, and resource domains.
   - Treat residuals in runtime files as blockers. Treat documentation residuals as report-only when configured.

## Files To Update

For this stack, environment switching usually touches:

- `project.config.json`: `appid`, `cloud.env`.
- `cloudbaserc.json`: `envId`.
- `config.js` or equivalent app config: `resourceEnv`, `cloudDomin`, optional resource appid fields.
- Cloud function files under configured roots: `.js`, `.json`, `.env` files that embed env IDs or appids.

Do not rewrite unrelated formatting. Use structured JSON parsing where practical; preserve app config style when it is JavaScript rather than JSON.

## Bundled Resources

- `scripts/switch-env.ps1`: reusable PowerShell switcher. Copy it into a target project when the project lacks a switcher or needs a known-good baseline.
- `references/env-config-schema.md`: manifest format, field meanings, and adaptation notes.

## Implementation Notes

- Write switched text as UTF-8 without BOM so WeChat Developer Tools and Node scripts do not see unexpected bytes.
- Build the list of known values from all configured environments, then replace only known non-target values.
- Scan projected content, not only on-disk content, so check mode can report residuals without writing files.
- Support `reportOnlyFiles` for docs or historical references that may legitimately mention other environments.
- Keep `scripts/env-config.json` excluded from residual scans because it intentionally stores every environment.
