# Throne SQLite (portable)

Windows. DB: `<THRONE_DIR>/config/throne.db`

## Outbound IDs

From Throne `RouteRule.h`:

| ID | Meaning |
|----|---------|
| -1 | proxy |
| -2 | direct |
| -3 | block |
| -4 | reserved (dns hijack internally) |
| -5 | warp-bypass |

`route_rules.outbound_id` default is `-2`. `route_profiles.default_outbound_id` default is `-1` (proxy). Stock **Default** + TUN tunnels the whole PC.

## Rule types (`route_rules.type`)

| Int | Token |
|-----|--------|
| 0 | custom |
| 2 | simpleAddressBypass |
| 4 | simpleProcessNameProxy |
| 7 | simpleProcessPathProxy |

Several fields on one rule are AND. Put suffixes, exact hosts, and keywords on **separate** rules.

## Settings

```
active_routing=Agents only
current_route_id=<id of Agents only>
vpn_strict_route=false
dns_final_out=direct
enable_tun_routing=false
disable_private_range_bypass=false
system_proxy_enabled=false
tun_mode_enabled=true
sub_auto_update=30
windows_set_admin=true
remember_enable=true
```

First-time: enable TUN in the UI after a node is selected; leave `tun_mode_enabled` false in the DB until then. After a node exists (`remember_id` in `profiles`), `scripts/ensure_autostart_flags.py` restores `remember_enable=true` and `tun_mode_enabled=true` at logon while Throne is not running. Do not write those keys from a tunneled agent against a live process. `remember_id` alone does nothing. Task Scheduler launching `Throne.exe` ≠ core running.

`sub_auto_update` is minutes between subscription refreshes while Throne is running. `windows_set_admin=true` records that the app expects elevation (pairs with the Task Scheduler startup task created from the UI).

GUI drift: `active_routing` → `Default`, `dns_final_out` → `remote`. Restore both after a UI session.

Read-only check. Set `THRONE_DIR` first. Do not hard-code a user profile path. Summarize pass/fail in prose; do not paste `domain_*` / CIDR rows into git, PRs, chat, or a skill file.

```powershell
if (-not $env:THRONE_DIR) { throw 'Set THRONE_DIR to the Throne install folder' }
python -c "import sqlite3,os; p=os.path.join(os.environ['THRONE_DIR'],'config','throne.db'); c=sqlite3.connect(p);
print(list(c.execute('SELECT id,name,default_outbound_id FROM route_profiles')));
print(list(c.execute('SELECT rule_order,type,protocol,action,ip_is_private,outbound_id FROM route_rules WHERE route_profile_id=(SELECT id FROM route_profiles WHERE name=''Agents only'') ORDER BY rule_order')));
print(list(c.execute('SELECT key,value FROM settings WHERE key IN (''active_routing'',''current_route_id'',''vpn_strict_route'',''dns_final_out'',''enable_tun_routing'',''disable_private_range_bypass'',''system_proxy_enabled'',''tun_mode_enabled'',''sub_auto_update'',''windows_set_admin'',''remember_enable'',''remember_id'')')))"
```

The SELECT above omits domain/CIDR JSON on purpose. To confirm an allowlist exists, count non-empty `domain_json` / `domain_suffix_json` / `domain_keyword_json` rows; do not print their values.

`python scripts/assert_not_live_throne.py --throne-dir $env:THRONE_DIR` must fail when `config/logs/running.marker` exists. Do not apply a rendered profile to that tree.

## Columns used when inserting `route_rules`

Write these columns. Unused JSON matchers are the text `[]`.

| column | notes |
|--------|--------|
| `route_profile_id` | id of **Agents only** |
| `rule_order` | 0, 1, 2, … first match wins |
| `name` | generic label only (`Allowlist suffixes`, `cursor process name`; never an FQDN or CIDR) |
| `type` | see table above |
| `protocol` | `dns` on the hijack rule, else empty |
| `action` | `hijack-dns` or `route` |
| `ip_is_private` | `1` or `0` |
| `ip_cidr_json` | JSON array of CIDR strings |
| `domain_json` | JSON array of exact hosts (user-supplied) |
| `domain_suffix_json` | JSON array of suffixes (user-supplied) |
| `domain_keyword_json` | JSON array of keywords (user-supplied) |
| `process_name_json` | e.g. `["Cursor.exe"]` — never `["node.exe"]` |
| `process_path_json` | JSON array with one resolved Windows path |
| `process_path_regex_json` | JSON array with one regex string |
| `outbound_id` | `-1` proxy or `-2` direct |

Other matcher columns stay `[]` / `0` / empty. Do not fill host examples or home-directory paths into this skill.

## Rule order template

DNS → private/LAN → **user allowlist** → discovered agent processes.

Exact process names and paths are written **after** discovery on the test/target machine. Publish only generic labels.

| order | name | type | match | outbound |
|-------|------|------|-------|----------|
| 0 | Route DNS | 0 | `protocol=dns`, `action=hijack-dns` | -2 |
| 1 | Private IPs | 2 | `ip_is_private=1` | -2 |
| 2 | LAN CIDRs | 2 | `ip_cidr_json` = `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16` | -2 |
| 3+ | Allowlist extra CIDRs | 2 | `ip_cidr_json` from this chat only | -2 |
| | Allowlist suffixes | 2 | `domain_suffix_json` from this chat only | -2 |
| | Allowlist hosts | 2 | `domain_json` from this chat only | -2 |
| | Allowlist keywords | 2 | `domain_keyword_json` from this chat only | -2 |
| | cursor/claude/codex/devin process name | 4 | discovered exe name | -1 |
| | same family process path | 7 | resolved exe path | -1 |
| | same family process regex | 0 | catalog regex, no version hashes | -1 |

A process-name proxy rule is invalid unless that family also has a path or regex rule. Generate with `scripts/render_agents_only_rules.py`.

Catalog regexes (no machine hashes):

```
(?i)[\\/]cursor-agent[\\/]versions[\\/][^\\/]+[\\/]node\.exe$
(?i)[\\/]\.local[\\/]bin[\\/]claude\.exe$
(?i)[\\/](?:AnthropicClaude|Claude)[\\/].*[\\/]Claude\.exe$
(?i)[\\/](?:Programs\\)?OpenAI[\\/]Codex[\\/].*[\\/]codex\.exe$
(?i)[\\/]\.codex[\\/]packages[\\/]standalone[\\/].*[\\/]codex\.exe$
(?i)[\\/]WindowsApps[\\/]OpenAI\.Codex[^\\/]*[\\/]app[\\/](?:ChatGPT\.exe|resources[\\/]codex\.exe)$
(?i)[\\/]\.local[\\/]bin[\\/]devin\.exe$
(?i)[\\/]cognition[\\/]cli[\\/].*[\\/]devin\.exe$
(?i)[\\/]Devin[\\/]Devin\.exe$
(?i)[\\/]extensions[\\/]windsurf[\\/]devin[\\/]bin[\\/]devin\.exe$
(?i)[\\/]extensions[\\/]windsurf[\\/]bin[\\/]language_server_windows_x64\.exe$
```

Resolve live paths on the machine; do not commit version-folder hashes.

```powershell
powershell -NoProfile -File scripts/discover_agent_processes.ps1
```

Equivalent CIM filter (read-only):

```powershell
Get-CimInstance Win32_Process -Filter "Name='Cursor.exe' OR Name='Claude.exe' OR Name='claude.exe' OR Name='codex.exe' OR Name='Codex.exe' OR Name='ChatGPT.exe' OR Name='devin.exe' OR Name='Devin.exe' OR Name='node.exe' OR Name='language_server_windows_x64.exe'" |
  Where-Object {
    $_.Name -eq 'Cursor.exe' -or
    $_.Name -match '^(?i)(claude|codex|devin)\.exe$' -or
    $_.ExecutablePath -like '*\cursor-agent\versions\*\node.exe' -or
    $_.ExecutablePath -like '*\OpenAI\Codex\*\codex.exe' -or
    $_.ExecutablePath -like '*\WindowsApps\OpenAI.Codex*\app\ChatGPT.exe' -or
    $_.ExecutablePath -like '*\Devin\Devin.exe' -or
    $_.ExecutablePath -like '*\extensions\windsurf\devin\bin\devin.exe' -or
    ($_.Name -eq 'language_server_windows_x64.exe' -and $_.ExecutablePath -like '*\extensions\windsurf\bin\language_server_windows_x64.exe')
  } |
  Select-Object Name, ProcessId, ExecutablePath
```

If the version folder changed and regex failed, add the new exact path as another type-7 rule. Do not use `process_name=node.exe`. Do not match every `ChatGPT.exe`. Do not use `process_name=language_server_windows_x64.exe`; path-qualify under `extensions\windsurf\bin` only.

Default mixed inbound is `127.0.0.1:2080` (`inbound_socks_port`). TUN IPv4 CIDR is whatever Throne generated (often `172.19.0.1/24`); treat it as an implementation detail, not a site identifier.

If TUN is unavailable, **Cursor** can use that mixed inbound via app-level `http.proxy` only — never System Proxy. That fallback does not cover Claude, Codex, or Devin. See [docs/http-proxy-fallback.md](docs/http-proxy-fallback.md).

## Links

- https://throneproj.github.io
- https://throneproj.github.io/get_started/installation/
- https://throneproj.github.io/get_started/configuration
- https://github.com/throneproj/Throne/discussions/893 (TUN per process)
- https://github.com/throneproj/Throne/issues/1365 (Tun routing + Strict off + process rules)
- https://github.com/throneproj/Throne/issues/1305 (active profile may stop on subscription update)
- https://github.com/throneproj/Throne/releases/tag/1.1.2 (Task Scheduler autostart)
