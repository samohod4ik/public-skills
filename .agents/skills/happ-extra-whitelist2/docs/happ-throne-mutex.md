# Variant: Happ full-proxy vs Throne Agents only

Two mutually exclusive primary install paths on Windows. Pick one owner of System Proxy / TUN. Never enable two System Proxies.

| | **1. Happ (full-proxy)** | **2. Throne Agents only** |
|---|-------------------------|---------------------------|
| Who is tunneled | Whole OS (Happ System Proxy + TUN) | Discovered local agent clients (Cursor, Claude, Codex, Devin; see that skill) |
| Rest of OS | Through Happ | **Direct** (Throne System Proxy off) |
| Routing | RoscomVPN **WHITELIST** | Per throne-agents-tun |
| Exits | Extra Whitelist2 DE then NL **when those remarks exist** | Per that skill / last used Throne outbound |
| Persistence | `Happ.exe --autostart` + autoconnect `lastused` | Per throne-agents-tun (do not copy Happ `--autostart` here) |
| Skill | [SKILL.md](../SKILL.md) | [throne-agents-tun](../../throne-agents-tun/SKILL.md) |

The old split named "Cursor-only" is now the Throne profile **Agents only**.

## When to choose Happ

- Need the whole machine on the proxy (browser, agents, other apps).
- Remote access to the host depends on the VPN.
- Want WHITELIST split + Extra Whitelist2 DE/NL when those remarks exist.
- Need logon autostart and autoconnect (`lastused` / soft `happ://connect`).

Pipeline: [install-pipeline.md](install-pipeline.md) · [autoconnect.md](autoconnect.md).

## When to choose Throne Agents only

- Only local agent clients must use the VPN.
- Everything else should stay on the ISP path.
- Happ is not the primary OS proxy on this machine (or Happ is unused).

Follow [throne-agents-tun](../../throne-agents-tun/SKILL.md). Do not invent a second System Proxy.

## Hard rules (both variants)

1. **Never** enable Throne System Proxy and Happ System Proxy at the same time.
2. If Happ is primary: Throne TUN **off**, Throne System Proxy **off**.
3. If Throne Agents only is primary: Happ System Proxy **off**, Happ TUN **off**. Do not install Happ `--autostart` + connect nudge on that machine.
4. Never kill Happ (or drop `happ://disconnect`) while a remote session depends on the Happ tunnel.
5. No subscription URLs, tokens, or host-specific paths in this repository.

## Watch (Happ primary)

Process up, TUN/proxy down → soft `happ://connect`. Not kill.

## Watch (Throne Agents only)

If matched agent processes are not going through the intended tunnel, follow throne-agents-tun pitfalls. Do not "fix" it by turning on Happ System Proxy beside Throne.
