# Claude routing policy

## Endpoint coverage

Reviewed against official documentation on 2026-10-26:

- [Desktop network requirements](https://code.claude.com/docs/en/desktop#network-access-requirements)
- [Claude Code network requirements](https://code.claude.com/docs/en/network-config#network-access-requirements)
- [Anthropic API IP addresses](https://platform.claude.com/docs/en/api/ip-addresses)

Route these root domains and all subdomains with `DOMAIN-SUFFIX`:

- `anthropic.com`: API, Console legacy hosts, assets, feature flags, telemetry and MCP proxy.
- `claude.ai`: chat, authentication, assets, downloads and live previews.
- `claude.com`: platform, OAuth, SSO, support, documentation and status.
- `claude.app`: live previews and application hosts.
- `claudeusercontent.com`: Chrome bridge, frames and artifact content.
- `claudemcpcontent.com`: desktop MCP content.

Also route the documented inbound API ranges `160.79.104.0/23` and `2607:6bc0::/48` using IP-CIDR/IP-CIDR6 with `no-resolve`. The separately documented outbound range is for requests initiated by Anthropic servers, not the client API destination; do not substitute it for the inbound ranges.

Claude Code documents two optional operational telemetry endpoints; route these exact hosts rather than the whole shared providers:

- `http-intake.logs.us5.datadoghq.com`
- `browser-intake-us5-datadoghq.com`

Add `PROCESS-NAME,claude.exe,<group>` and `PROCESS-NAME,Claude.exe,<group>` after local/private exclusions. This catches external executable traffic to third-party endpoints. Shared hosts such as npm, GitHub, Google storage and Sentry are not Anthropic-owned suffixes. Browser traffic to shared third-party hosts needs separate observed evidence; do not claim a Claude executable rule covers the entire browser, WSL, remote sessions, or a client bypassing Clash.

## Rule order and candidates

1. Localhost, loopback, RFC1918, CGNAT and IPv6 local exclusions to DIRECT.
2. The six Anthropic suffixes, precise telemetry hosts and API IP ranges to Claude.
3. Claude executable rules to Claude.
4. Original subscription rules.

Default to one fixed leaf node. If the user requests alternatives, use one manual selector containing only individually approved leaves. For a US-only request, verify every candidate through a node-pinned probe before adding it. Never use a general group, DIRECT, automatic country regex, fallback, URL testing or load balancing. An unavailable node must fail rather than silently pick a different country. Missing candidates must be addressed explicitly; don't infer that a replacement with a similar name has the same exit.

## Evidence levels

- **Written:** correct enhancement files, backup, complete rules and approved candidates. This does not establish runtime activation.
- **Configuration validated:** Mihomo accepts the generated/candidate configuration. An offline candidate is not evidence that Verge has regenerated or loaded it.
- **Runtime loaded:** generated, persistent and runtime modes are rule, process lookup is always, and the selector contains exactly the approved candidates and selects one of them.
- **Traffic verified:** fresh service-log lines for the requested client's Anthropic connections show `using Claude[<approved node>]`. Pair these with timestamped exit country evidence. An HTTP 401/403/404/426 does not disprove routing when the connection log is present.

Never promise that routing makes the user appear American in every respect or prevents suspension. It limits mixed-exit routing; account state, browser signals, proxy reputation and provider policy remain outside these rules.
