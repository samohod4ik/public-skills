---
name: throne-agents-tun
description: >-
  Use when installing or configuring Throne (throneproj) on Windows so only
  local AI agent clients (Cursor IDE/Agent, Claude Code/Desktop, Codex CLI/App,
  Devin CLI/Desktop plus path-qualified Windsurf language server) use a
  VPN/subscription tunnel, or when TUN process rules break intranet, SSO, or
  split-horizon DNS. Do not use for whole-OS proxying, Devin Cloud workstation
  routing, or evading workplace controls. Replaces throne-cursor-only-public.
---

# Throne: Agents-only tunnel

Windows-only. Portable Throne. Config is SQLite `<THRONE_DIR>/config/throne.db`, not loose JSON. Profile **Agents only**: default outbound **direct**. Proxy the discovered local agent processes. TUN on, System Proxy off.

Replaces `throne-cursor-only-public` (profile **Cursor only**). Migration: [docs/MIGRATION.md](docs/MIGRATION.md).

This skill ships **no organization domains**. RFC1918 bypass is not enough for named intranet.

Matched processes send **all public egress** through the tunnel, including Git, MCP, and package registries. Keep internals on the user allowlist.

## Hard gate (do this first)

Agents are matched **by process name + path/regex**. After that, every destination that is not already a direct rule goes through the VPN.

If the user does not provide an allowlist, models and agent tools **cannot reach internal hosts**: SSO, issue trackers, package registries, intranet names, split-horizon names that resolve to private IPs only on corporate DNS. Typical symptom: timeout or WAF/SSO 403 from a datacenter IP.

**Before writing `throne.db` or telling the user to enable TUN:**

1. State that gap in one sentence.
2. Ask for the allowlist. Do not invent hostnames.
3. Apply only what they confirmed in **this conversation**.

Ask for:

- domain suffixes (PAC `*.corp.example` → `.corp.example`)
- exact hosts (short names and FQDNs)
- extra CIDRs beyond RFC1918, if any
- optional keywords (separate rule; AND if mixed with domain fields)

Allowlist source is **only** what the user pasted or attached in this chat. Do not read PAC, WPAD, WinINET, proxy settings, other skills, or files on disk to discover domains unless the user attached those files here. Empty allowlist is valid only after they confirm RFC1918-only.

Do **not** put subscription URLs, tokens, usernames, or absolute home paths into the skill, git, or chat logs. Paste the subscription only in the Throne UI.

Use only with the device owner's approval. Do not use split tunnel to evade monitoring or filtering.

## Coverage

| Client | TUN process split | Notes |
|--------|-------------------|--------|
| Cursor IDE + cursor-agent | Yes | Chat/Agent is often `Cursor.exe`; helper `node.exe` only via versioned path |
| Claude Code CLI + Claude Desktop | Yes | Resolve both if the WindowsApps alias shadows the CLI |
| Codex CLI + Codex App | Yes | App may be `ChatGPT.exe` under `OpenAI.Codex`; never all `ChatGPT.exe` |
| Devin CLI | Yes | `devin.exe` under `.local/bin` or `cognition/cli` |
| Devin Desktop + Windsurf language server | Yes, path-qualified | `Devin\\Devin.exe`; CLI under `extensions\\windsurf\\devin\\bin`; LS only under `extensions\\windsurf\\bin`. Never a bare `language_server*.exe` name |
| Devin Cloud / Devbox | **No** | Not this PC's TUN. See [docs/agent-network-requirements.md](docs/agent-network-requirements.md) |

Do **not** add bare `processName:node.exe`. Names are case-sensitive. Do not match `%LOCALAPPDATA%` as a directory.

## Download and install

1. https://throneproj.github.io/get_started/installation/ — Windows **Portable ZIP**, not the EXE installer.
2. Extract so `Throne.exe` is `<THRONE_DIR>/Throne.exe` (directory the user chose).
3. First run creates `config/throne.db`.

## Import subscription

1. `Ctrl+V` on the main window, or Settings → Groups → type Subscription → URL.
2. Update / Refresh the group.
3. Keep the URL in the UI only.

## Autostart (elevated) and subscription refresh

Do this after Agents-only routing works and a node has been started once (`remember_id` filled). Throne ≥1.1.2 **start with Windows** creates an elevated Task Scheduler logon task that only launches `Throne.exe`. That is not TUN-on.

**Start with Windows is not TUN-on.** Core/node and TUN restore only when **Remember last profile** is on (`remember_enable=true`). The GUI often flushes `remember_enable=false` on exit. Maintainer: [Throne #1547](https://github.com/throneproj/Throne/issues/1547). Symptom after reboot: admin Throne, Routes = Agents only, TUN off, node not started.

Do **not** write these flags into a running `throne.db` from an agent. A logon writer applies them when `Throne.exe`/`ThroneCore` are **not** running. Use a process probe, not `running.marker` — a stale marker must not block boot.

1. Start `Throne.exe` **Run as administrator**. Enable **start with Windows** (one-time UAC). Keep the elevated task; it is what starts the GUI without UAC each boot.
2. Settings → Groups → subscription: auto-update **30** minutes (`sub_auto_update=30`), `skip_auto_update=0`. Keep Throne running for the timer (#1305, #1528).
3. Either register the Limited flags task **or** rebind the Highest task — not both after a successful rebind.

Set the install folder, then register flags-only (Limited, no extra UAC). This does **not** start `Throne.exe`:

```powershell
$env:THRONE_DIR = 'C:\path\to\Throne'   # the folder that contains Throne.exe
$py = (Get-Command python.exe | Where-Object { $_.Source -notlike '*WindowsApps*' } | Select-Object -First 1).Source
powershell -NoProfile -File scripts/register_autostart_flags_task.ps1 -ThroneDir $env:THRONE_DIR -Python $py
```

4. Optional, race-free (needs Administrator). Rebind the existing Highest task to the wrapper with a baked Python path, then disable `ThroneAutostartFlags`:

```powershell
$env:THRONE_DIR = 'C:\path\to\Throne'
$py = (Get-Command python.exe | Where-Object { $_.Source -notlike '*WindowsApps*' } | Select-Object -First 1).Source
powershell -NoProfile -File scripts/rebind_throne_startup_task.ps1 -ThroneDir $env:THRONE_DIR -Python $py
```

Do **not** toggle Throne's own "start with Windows" after step 4 — the UI rewrites the action back to bare `Throne.exe`.

`scripts/ensure_autostart_flags.py` sets `remember_enable=true`, `tun_mode_enabled=true`, `active_routing=Agents only`, `current_route_id`, System Proxy off, tun routing off, Strict off, `dns_final_out=direct`, `disable_private_range_bypass=false`. It refuses an empty `remember_id` or one missing from `profiles`. Skip (exit 0) if Throne is running; fail closed if the process probe fails. It re-probes after taking the SQLite write lock. Wrapper `scripts/start_throne_autostart.cmd` still launches `Throne.exe` if the writer returns 1. Flags-only helper: `scripts/write_autostart_flags.cmd`. Log: `<THRONE_DIR>/config/autostart-flags.log`.

ASCII-only install path is safer for the startup task (Unicode paths have broken autostart in past builds).

**Agent safety:** if this chat’s agent traffic already depends on Throne (TUN or Cursor `http.proxy` into Throne), do **not** stop Throne, kill `ThroneCore`, rewrite `throne.db`, or force-reset TUN from the agent. Tell the user to apply UI changes themselves. Restarting Throne from inside a Throne-routed agent session cuts the agent off mid-task. Hermetic tests and cloud VMs must use a **copy** of Throne, never a tree with `config/logs/running.marker`.

## Portable install

Throne Portable ZIP can live in any `<THRONE_DIR>`. Process path rules are **machine-local**: run discovery on the machine where TUN runs (after updates or if the install path changed). Re-confirm the allowlist on that machine; do not reuse another host’s intranet list blindly. TUN still needs administrator rights on the OS that enables it.

## Modes (do not invert)

| Control | Value | Why |
|---------|--------|-----|
| TUN | On for process rules | `find_process` sees traffic that hits TUN |
| System Proxy | **Off** | Sets WinINET for the whole OS |
| Strict Route | **Off** | Blocks LAN / multi-homed DNS on Windows |
| DNS final outbound | **direct** | Split-horizon needs the OS/corporate resolver |
| Private range bypass | On | RFC1918 stays off TUN routes |
| Tun routing | **Off** | Process rules + Strict off → loops (Throne #1365) |
| Fake-IP / system DNS hijack | Off | Breaks browser and LAN names |

Start a node first, then enable TUN (Admin). Do not persist `tun_mode_enabled=true` before a node and **Agents only** are selected. After that, the logon writer is allowed to restore `tun_mode_enabled=true` and `remember_enable=true` while Throne is not running. Autostart without **Remember last profile** leaves TUN and the node off after reboot.

Throne GUI often rewrites `active_routing=Default` and `dns_final_out=remote` on exit. Re-check those keys after any UI session.

## Discover processes, then route

`default_outbound_id = -2` (direct). `-1` = proxy. First match wins — allowlist before process rules.

On the machine that will enable TUN:

```powershell
powershell -NoProfile -File scripts/discover_agent_processes.ps1
```

Keep only families the user asked for and that discovery actually found (or whose install path they confirmed). Then render:

```text
python scripts/render_agents_only_rules.py --discovered discovered.json --allowlist allowlist.json -o agents-only-profile.json
```

The renderer refuses bare `node.exe`, directory-only `%LOCALAPPDATA%`, and process-name rules with no path/regex.

Resolve live `Cursor.exe`, Claude, Codex, and Devin binaries on the machine. Default Cursor is often `%LOCALAPPDATA%/Programs/cursor/Cursor.exe`; do not assume it. Do not commit version-folder hashes.

1. `hijack-dns` / protocol `dns`
2. `ip_is_private` → direct
3. CIDR `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16` → direct
4. **User allowlist** → direct (extra CIDRs, suffixes, hosts, keywords; separate rules; generic `name` only)
5. Discovered agent process names **and** resolved paths / catalog regexes → proxy

SQL details: [reference.md](reference.md). Vendor FQDNs (diagnostics, not IP TUN rules): [docs/agent-network-requirements.md](docs/agent-network-requirements.md). Architecture: [docs/tun-process-routing.md](docs/tun-process-routing.md).

## Edit `throne.db`

0. If the allowlist question has not been answered in this chat, **stop** and return to Hard gate. Proceed with RFC1918-only only after the user said so.
1. If this chat’s agent traffic already depends on Throne (TUN or Cursor `http.proxy` into Throne), **stop**. Do not quit Throne, kill `ThroneCore`, rewrite `throne.db`, or reset TUN. Hand the UI/SQL steps to the user and wait. Run `python scripts/assert_not_live_throne.py --throne-dir <THRONE_DIR>` — it must refuse a live tree.
2. Otherwise (first-time install / agent not on Throne / **cloud VM**): fully quit Throne (not tray).
3. Backup `config/throne.db` next to the app (no secrets in the backup name).
4. Write `route_profiles` / `route_rules` / `settings` from the rendered profile.
5. Confirm `active_routing=Agents only`, `current_route_id` = that id, `dns_final_out=direct`.
6. Start Throne, pick a node, TUN on, System Proxy off.

Never add `throne.db`, `*.db.bak*`, Throne logs, or Group/subscription exports to git. Publish only this skill folder, not the Throne install tree.

## Fallback when TUN / admin is blocked

If the user cannot elevate or TUN fails (adapter already exists / Element not found):

1. **Do not** enable System Proxy (WinINET for the whole OS — breaks coexistence with other VPNs / direct apps).
2. Leave Throne running with a selected node, System Proxy **off**, TUN **off**. Mixed inbound stays on `127.0.0.1:<inbound_socks_port>` (Throne default often `2080` — read the live inbound port).
3. **Cursor only:** point Cursor at that inbound via User Settings JSON (see [docs/http-proxy-fallback.md](docs/http-proxy-fallback.md)). This does **not** cover Claude, Codex, Devin, or `cursor-agent`.
4. Claude Code: HTTP/HTTPS proxy env vars (`HTTPS_PROXY`), not SOCKS. Codex/Devin CLI: their own proxy settings. None of those equal TUN process split.
5. If helpers must use the tunnel, escalate to TUN + process rules — do not turn on System Proxy.

Prefer TUN + **Agents only** when admin is available. Use the app-proxy fallback when TUN is impossible or as a first isolation test for Cursor IDE only. Do not enable TUN merely to fix HTTP/2 streaming (use HTTP/1.1 first).

## Verify in logs

Pass:

- Discovered agent processes to the public Internet → `outbound/socks[proxy]`
- Same processes to allowlisted names or RFC1918 → `outbound/direct`
- Browser and other apps → `outbound/direct`

Expected noise: `svchost.exe` to the TUN DNS address. SOA for `.` alone is not a LAN outage. Long-lived WSS on TCP/443 (Claude Chrome bridge, Codex sampling) must not be rewritten or idled out by the node.

Fail:

- Browser → `socks[proxy]` → System Proxy on or default outbound `-1`
- Intranet / SSO 403 → `dns_final_out=remote`, empty allowlist, or allowlist below process rules
- Agent → `direct` on vendor APIs → stale path/regex, or family not discovered
- Whole PC on VPN → profile **Default** + TUN
- `node.exe` from Program Files → `socks[proxy]` → illegal bare node rule

After Stop, connections from the TUN address to the peer on high ports being reset is teardown, not a new bug.

When checking the DB, report pass/fail in prose. Do not paste `domain_*` / CIDR query rows into git, PRs, chat, or an updated skill.

## Tests (not on a live TUN host)

```text
python scripts/validate_skill.py
python -m pytest tests -q
```

Dynamic TUN smoke: [docs/cloud-smoke-test.md](docs/cloud-smoke-test.md) on a disposable Windows VM. Never against a Throne instance this chat already depends on.

## Do not

- Enable System Proxy "just to test"
- Use profile **Default** under TUN
- Match all `node.exe`
- Match every `ChatGPT.exe` (Codex App is path-qualified)
- Edit the DB while Throne is running and then click Routes / OK
- Turn on Tun routing to "fix" process rules
- Commit or paste the subscription URL
- Invent, scrape, or publish the user's internal domains
- Spoof User-Agent or otherwise bypass WAF/SSO
- Stop/restart Throne, reset TUN, or rewrite `throne.db` from an agent whose traffic already depends on Throne
- Put a subscription URL into the agent prompt or chat logs
- Treat Devin Cloud source IPs as workstation TUN rules
- Toggle Throne **start with Windows** after rebinding the logon task to `start_throne_autostart.cmd` (the UI rewrites the action to bare `Throne.exe`)
