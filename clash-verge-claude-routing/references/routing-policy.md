# Claude routing policy

## Required suffix coverage

Route these suffixes to the dedicated fixed Claude group:

- `anthropic.com` — API, telemetry, assets, and Anthropic web properties.
- `claude.ai` — Claude web application, assets, downloads, and CDN hosts.
- `claude.com` — Claude platform and newer product endpoints.
- `claudeusercontent.com` — bridge, frame, and user-content hosts.

Add `PROCESS-NAME,claude.exe,<group>` after private-network exclusions to cover Claude Code or Claude Desktop connections to third-party endpoints without globally redirecting shared domains used by unrelated applications.

## Rule order

Place rules in this order:

1. localhost and private-network exclusions to `DIRECT`;
2. the four Anthropic suffixes to the fixed Claude group;
3. `PROCESS-NAME,claude.exe` to the fixed Claude group;
4. the subscription's original rules.

This order keeps local MCP servers reachable while ensuring external Claude process traffic cannot fall through to a different subscription policy.

## Fixed-exit behavior

Use a selector containing exactly one leaf proxy. Resolve nested selectors to their current leaf before creating the group. Reject `DIRECT`, `REJECT`, and unresolved selector groups. Do not configure URL testing, load balancing, or fallback for the Claude group.

If the subscription removes or renames the fixed node, treat configuration validation failure as fail-closed and require the user to select a replacement explicitly.

## Validation evidence

Require all of the following:

- Mihomo reports the generated configuration test as successful.
- Runtime, persistent, and generated modes are `rule`.
- `find-process-mode` is `always`.
- The Claude group contains one candidate and selects that candidate.
- All five managed Claude rules exist in the generated configuration.
- Actual service-log lines for Anthropic traffic end with `using Claude[<fixed node>]`.

An HTTP status such as 401, 403, 404, or 426 still proves routing when the connection appears in the Clash log. A model response proves end-to-end Claude operation but can consume quota, so obtain user authorization before sending one.

## Account-risk statement

Describe the policy as reducing mixed-exit routing. Never claim that a stable proxy guarantees protection from suspension, because account state, node reputation, provider policy, and other signals remain outside Clash routing control.
