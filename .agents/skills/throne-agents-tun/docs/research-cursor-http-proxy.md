# Research notes: Cursor local proxy vs TUN

Sanitized synthesis from Parallel deep research on Cursor IDE networking with a local mixed SOCKS/HTTP inbound (Throne, sing-box, or similar local proxy clients). No subscription URLs. No org inventory.

## Conclusions

1. **Start with app-level routing** when only the IDE must use the tunnel: point Cursor at the **HTTP** side of the local mixed listener (`http://127.0.0.1:PORT`). Smallest blast radius, easiest to undo.
2. **HTTP/1.1 is a transport fix**, not a coverage fix. Cursor defaults to HTTP/2 bidirectional streaming; some proxies buffer SSE, force timeouts, or break H2. Use **HTTP Compatibility Mode → HTTP/1.1** and **fully restart Cursor**. Do not enable TUN merely because streaming stalls.
3. **`http.proxySupport` / `cursor.general.disableHttp2`** are useful compatibility attempts; Cursor enterprise docs may not document them. Treat the **Network UI** as authoritative for HTTP/1.1.
4. **Keep `http.proxyStrictSSL: true`**. Prefer excluding `*.cursor.sh`, `*.cursor-cdn.com`, `*.cursorapi.com` from SSL inspection/DLP over disabling TLS verification.
5. **Escalate to TUN process split** only when app-level misses helpers, extensions, CLI (`cursor-agent`), Claude, Codex, Devin, or other proxy-unaware paths. Match live process paths; keep RFC1918 / loopback / local listener direct; Strict off + no Tun-routing loops on Windows.
6. **Never paste a VPN subscription URL into Cursor settings** — only the local inbound URL.

## Recommended settings.json (starting point)

```json
{
  "http.proxy": "http://127.0.0.1:PORT",
  "http.proxySupport": "override",
  "http.proxyStrictSSL": true,
  "cursor.general.disableHttp2": true
}
```

SOCKS-only listener variant: `socks5://127.0.0.1:PORT`.

If HTTP/2 through the local client is reliable, drop the disableHttp2 / HTTP/1.1 fallback.

## Failure modes (short)

| Symptom | Likely cause | First action |
|---------|--------------|--------------|
| Agent output arrives all at once | Proxy buffers streaming | HTTP/1.1 + restart |
| ~5s stall; plain HTTPS works | No H2 bidirectional | HTTP/1.1 + restart |
| `SSLV3_ALERT_HANDSHAKE_FAILURE` | Path/regional H2 issue | HTTP/1.1 (incident class was mitigated; still a valid fallback) |
| Cannot connect to proxy | Wrong/stale port; client down | Fix listener port; clear leftover OS proxy |
| Agent timeouts under corp DLP | SSL inspection | Exclude Cursor domains; keep StrictSSL true |
| Chat works, agent CLI does not | App-proxy coverage gap | TUN + process path/regex |

## Decision procedure

1. Confirm local listener + port.
2. Short Chat / sign-in.
3. Cursor **Network → Run Diagnostics**.
4. Test Agent streaming separately.
5. Streaming broken → HTTP/1.1 + restart (not TUN).
6. Helpers still bypass → narrow TUN process split.
7. On TUN: exclude loopback, mixed inbound, private ranges as needed; never enable System Proxy as a substitute.

## How this maps to `throne-agents-tun`

- Skill default for **local agents with admin**: TUN + **Agents only** (coverage).
- Skill fallback without admin / broken TUN: this app-proxy path (**Cursor IDE only**).
- Do not invert: System Proxy off; subscription URL only in Throne UI.
