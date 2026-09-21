# TUN + process routing

Throne TUN captures packets, then `find_process` picks the first matching `route_rules` row. Unmatched traffic uses the profile default.

**Agents only** sets that default to **direct** (`-1` is proxy, `-2` is direct). The split is "which processes leave via the subscription node", not "which destinations are on a vendor IP list".

## Owners

| Layer | Owner |
|-------|--------|
| Packet capture | Throne TUN (`172.19.0.x/24` is an implementation detail) |
| Process match | `route_rules` type 4 (name), 7 (path), 0 (path regex) |
| Intranet / RFC1918 | Direct rules **above** process rules |
| Node / subscription | Throne UI only |
| App-level `http.proxy` | Cursor IDE fallback only |

Do not enable a second interceptor (system proxy, extra TUN, `tun.auto-route` elsewhere) on the same host.

## First-match order

1. DNS hijack → direct (split-horizon uses the OS resolver; `dns_final_out=direct`).
2. Private / LAN CIDRs → direct.
3. User allowlist (suffixes, hosts, extra CIDRs, keywords on **separate** rules) → direct.
4. Discovered agent process name **and** path/regex → proxy.
5. Default → direct.

A name rule without a path or regex for that family is rejected by `scripts/render_agents_only_rules.py`.

## Why not destination-IP allowlists

Vendor control-plane FQDNs change; published IP ranges often describe **vendor egress**, not client access. This profile matches **processes**. The FQDN inventory in [agent-network-requirements.md](agent-network-requirements.md) is for log verification and firewall tickets, not `ip_cidr_json` proxy rules.

Because the match is the process, Git/MCP/npm traffic from that process also uses the tunnel unless an earlier direct rule hits.

## Child processes

Throne matches the image that opened the socket. A parent `Claude.exe` rule does not automatically cover a helper `node.exe`. Allowed helper: versioned `cursor-agent\...\node.exe` via regex. Bare `node.exe` is forbidden (npm, system Node, random MCP servers would follow the VPN).

Electron trees (Cursor, Claude Desktop, Codex App as `ChatGPT.exe` under `OpenAI.Codex`) usually keep network in the named exe. Re-run discovery after updates.

## Modes that invert the design

| Control | Required | If inverted |
|---------|----------|-------------|
| TUN | On | Process rules never see foreign sockets |
| System Proxy | Off | WinINET for the whole OS |
| Strict Route | Off | LAN / multi-homed DNS breaks on Windows |
| Tun routing | Off | Loops with process rules (Throne #1365) |
| Profile Default + TUN | Never | Whole PC on VPN |

## WebSockets

Claude Chrome bridge and Codex sampling use long-lived WSS on TCP/443. Do not TLS-rewrite those flows; keep idle timeouts large enough on the node. See vendor notes in [agent-network-requirements.md](agent-network-requirements.md).

## Fallback

[http-proxy-fallback.md](http-proxy-fallback.md) is **Cursor IDE only**. It cannot implement Agents-only for Claude, Codex, Devin, or `cursor-agent`.
