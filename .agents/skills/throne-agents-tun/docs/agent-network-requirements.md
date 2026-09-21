# Agent network requirements

Diagnostic inventory for **Agents only** verification. This is **not** a Throne `ip_cidr_json` proxy list. Routing is process-based: a matched agent sends all public egress through the tunnel, including Git, MCP, and package downloads.

Do not treat vendor-published IP ranges as client destination allowlists. Re-check vendor docs when an endpoint fails.

## Cursor

Process match covers IDE Chat/Agent (`Cursor.exe`) and optional `cursor-agent\versions\*\node.exe`. App-proxy fallback (TUN off) is documented in [http-proxy-fallback.md](http-proxy-fallback.md). Cursor Network UI lists required domains such as `*.cursor.sh`, `*.cursor-cdn.com`, `*.cursorapi.com` — use those for diagnostics, not as the TUN policy.

## Claude (CLI + Desktop)

Official CLI table: [Claude Code enterprise network configuration](https://code.claude.com/docs/en/network-config).

Core (always needed for typical Claude Code login + API):

- `api.anthropic.com`
- `claude.ai`
- `claude.com`
- `platform.claude.com`

Opt-in / feature hosts (enable in diagnostics when the feature is used):

- `mcp-proxy.anthropic.com` (claude.ai connectors)
- `downloads.claude.ai` (native installer/updater)
- `storage.googleapis.com` (plugin metadata; older native updater)
- `registry.npmjs.org` (plugins, npx MCP, npm installs of the CLI)
- `bridge.claudeusercontent.com` (Claude in Chrome WebSocket)
- `*.frame.claudeusercontent.com` (artifacts)
- Desktop/web extra: `assets-proxy.anthropic.com` and other `*.claudeusercontent.com` ([same page, Desktop section](https://code.claude.com/docs/en/network-config))

Claude Code supports HTTP/HTTPS proxy env vars, **not SOCKS**. Desktop may follow one resolved OS proxy rather than re-evaluating PAC per destination. TUN process split is the coverage mechanism in this skill.

If the org uses Anthropic IP access control, the Chrome bridge must egress from the same approved path as `api.anthropic.com`. A shared proxy egress CIDR can admit other customers of that proxy — do not "fix" that by widening the org allowlist casually.

## Codex (CLI + App)

Control plane / ChatGPT-authenticated clients: [OpenAI network recommendations](https://help.openai.com/en/articles/9247338-network-recommendations-for-chatgpt-errors-on-web-and-apps).

Published hostname families include `*.auth.openai.com`, `*.chatgpt.com`, `*.openai.com`, `*.oaistatic.com`, `*.oaiusercontent.com`, `*.oaistatsig.com`, plus listed identity/CDN/challenge/telemetry hosts on that page (WorkOS, Cloudflare challenges, Sentry, Datadog, Intercom, Stripe, SendGrid).

WebSocket (do not block Upgrade on TCP/443; avoid idle-kill):

- ChatGPT: `wss://ws.chatgpt.com`
- Codex: `wss://chatgpt.com/`

Codex CLI sandbox domain rules are **separate** from this TUN profile. They constrain **commands Codex runs** when `features.network_proxy` is on; they do not replace Throne process matching. See [Codex permissions](https://developers.openai.com/codex/permissions).

OpenAI's published cloud **egress** IP ranges describe traffic **from** OpenAI, not client access **to** OpenAI. Do not copy them into Throne proxy CIDRs.

Windows process shapes (discovery, not assumed paths):

- CLI: `codex.exe` under `OpenAI\Codex` or `.codex\packages\standalone`
- App: `ChatGPT.exe` / bundled `codex.exe` under `WindowsApps\OpenAI.Codex*` — never every `ChatGPT.exe` on the machine

## Devin

### Workstation (this skill)

- Devin **CLI** is a local process (`devin.exe` under `.local\\bin` or `cognition\\cli`). TUN covers that process's public egress.
- Devin **Desktop** (Windsurf-lineage Electron) is also in scope when discovered: path-qualified `Devin\\Devin.exe`, bundled CLI under `extensions\\windsurf\\devin\\bin`, and `language_server_windows_x64.exe` only under `extensions\\windsurf\\bin`. Never a bare `language_server*.exe` process-name rule.
- CLI HTTP(S) can also use `proxy.mode` `system` / `manual` / `off` in `%APPDATA%\devin\config.json` ([Devin CLI config](https://docs.devin.ai/cli/reference/configuration/config-file)). That is not a substitute for TUN helpers.
- Browser/session tools for the product require `*.devinapps.com:443` on the workstation ([Devin enterprise deployment](https://docs.devin.ai/enterprise/deployment/overview)). Web app: `app.devin.ai`. Cognition does not publish a complete client FQDN inventory comparable to Claude/OpenAI.

### Not workstation TUN

Devin **Cloud** brain/devbox traffic does not ride this PC's TUN. Cloud-to-customer SCM/artifact allowlists use Cognition's published source IPs (they may change) or PrivateLink/IPsec/dedicated deployment ([Devin IP allowlist](https://docs.devin.ai/admin/common-issues), [deployment overview](https://docs.devin.ai/enterprise/deployment/overview)). Put those on the **server** boundary, not in this route profile.

Devin CLI `--sandbox` domain filter is documented as unstable; OS sandboxing is unsupported on Windows. Do not rely on it for this skill.

## How to use this list

1. After TUN is up, confirm agent processes → `outbound/socks[proxy]` in Throne logs.
2. If a feature fails (Chrome bridge, Codex stream, plugin install), compare the failing SNI/host to the tables above.
3. Add a **user allowlist** row only for intranet. Do not add vendor CDN IPs as proxy rules.
4. Keep long-lived WSS; do not enable TLS inspection on these control-plane hosts if the vendor forbids it.

## Sources

- [Claude Code: Enterprise network configuration](https://code.claude.com/docs/en/network-config)
- [OpenAI: Network recommendations for ChatGPT and Codex](https://help.openai.com/en/articles/9247338-network-recommendations-for-chatgpt-errors-on-web-and-apps)
- [OpenAI Codex: Permissions](https://developers.openai.com/codex/permissions)
- [Devin: Enterprise deployment](https://docs.devin.ai/enterprise/deployment/overview)
- [Devin: CLI configuration](https://docs.devin.ai/cli/reference/configuration/config-file)
- [Devin: IP allowlisting](https://docs.devin.ai/admin/common-issues)
