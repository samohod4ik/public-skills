---
name: happ-extra-whitelist2
description: >-
  Use when setting up or auditing Happ as the primary proxy client on Windows
  (desktop, laptop, or VM) with RoscomVPN WHITELIST routing, Extra Whitelist2
  exits (DE then NL when those remarks exist), 60-minute subscription refresh,
  Happ.exe --autostart, and autoconnect lastused. Not for Throne-as-primary,
  not for inventing a WHITELIST2 routing profile, not for pasting subscription URLs.
  For Agents-only TUN see ../throne-agents-tun and docs/happ-throne-mutex.md.
---

# Happ Extra Whitelist2

Portable public skill. Scope is **Windows** (any PC), not a single host or laptop-only playbook.

**Variant:** this skill is Happ **full-proxy**. Alternate: [Throne Agents only](docs/happ-throne-mutex.md) — only local agent clients through Throne TUN.

## When to use

- User wants Happ as **primary** Windows proxy client (whole OS).
- Need RoscomVPN **WHITELIST** routing + prefer **Extra Whitelist2** servers (DE → NL) **when those remarks exist**.
- Need subscription auto-update every **60 minutes**, logon **autostart**, and **autoconnect** (`lastused`).

## When NOT to use

- Making Throne (or another client) the primary OS tunnel — use the Throne Agents only variant instead.
- Looking for a public **WHITELIST2** *routing* profile (it does not exist — use WHITELIST routing + Extra Whitelist2 *server remarks* if present).
- Dumping or committing subscription URLs / `subs.db`.

## Autostart vs autoconnect

| | Autostart | Autoconnect (official) | Autoconnect (local nudge) |
|---|-----------|------------------------|---------------------------|
| Does | Starts Happ at logon (`Happ.exe --autostart`) | Brings TUN / System Proxy up on launch | Soft `happ://connect` after Happ.exe is running |
| Source | Windows Scheduled Task (vendor `app-auto-start` is Android-only) | `subscription-autoconnect` + `subscription-autoconnect-type: lastused` | Protocol handler; not the vendor header API |
| Local | Discover `Happ.exe`; register the task | Settings toggle if present | Delayed task 30–60s; Watch if TUN down. Live session already tunneled: register the nudge only — do not fire `happ://connect` just to apply. Field-check after reboot/logon. |
| Docs | [install-pipeline.md](docs/install-pipeline.md) | [autoconnect.md](docs/autoconnect.md) | same |

Prefer **lastused** (last selected server). Prefer Extra Whitelist2 DE then NL **when those remarks exist**.

## Hard rules

1. Never print or commit subscription URLs/tokens.
2. Prefer `happ://open` (focus) and `happ://connect` (tunnel) over disconnect/kill.
3. **Never kill Happ** and never call `happ://disconnect` when a remote session depends on the tunnel.
4. Do not enable another client's System Proxy/TUN while Happ is primary. **Never** Happ System Proxy + Throne System Proxy together. Throne stays spare: TUN off, System Proxy off.
5. Do not invent host-specific paths, computer names, or a `WHITELIST2` routing profile.

## Procedure

1. Confirm Happ installed; **discover** `Happ.exe` (pass `-HappExe` if needed).
2. Ensure subscription present (user-private); do not log the URL.
3. Import RoscomVPN **WHITELIST** deeplink; enable Use routing; confirm via `scripts/Get-HappRoutingNames.ps1`.
4. If Extra Whitelist2 remarks exist, connect DE then NL in the UI. Otherwise keep `lastused`.
5. `scripts/Set-HappSubscriptionRefresh.ps1` → 60.
6. `scripts/Install-HappAutostart.ps1` (launch task + delayed connect nudge).
7. Ask the subscription provider for `subscription-autoconnect: 1` + `subscription-autoconnect-type: lastused` (headers or `#` body lines). Enable the Settings auto-connect toggle **if present**.
8. `scripts/Invoke-HappSoftOpen.ps1` to focus. Use `scripts/Invoke-HappSoftConnect.ps1` only if the tunnel is down. Live session already up: skip connect; field-check the logon nudge after reboot.
9. Confirm Throne System Proxy/TUN are **off**.
10. `scripts/Verify-HappExtraWhitelist2.ps1` — all checks green or document gaps.

## Watch

If the Happ **process** is running but TUN / System Proxy is down:

1. Soft `happ://connect` (`scripts/Invoke-HappSoftConnect.ps1`; add `-Force` if WinINET still looks up but the tunnel is down).
2. Do **not** kill `Happ.exe`. Do **not** `happ://disconnect`.
3. If still down after a short wait, `happ://open` and inspect the UI; re-check provider autoconnect / lastused.
4. Only after the tunnel is up, verify routing + (if present) Extra Whitelist2 DE/NL.

If the live session is already tunneled, skip connect. Field-check the delayed logon nudge after reboot.

## Success criteria

- Happ process running; **autostart** task present; **autoconnect** nudge task present (unless explicitly skipped — then verify with `-SkipAutoconnectCheck`).
- `useRouting` on; active routing profile is the imported WHITELIST-based profile.
- Connected exit is Extra Whitelist2 DE or NL **when those remarks exist**.
- Registry refresh interval is 60 minutes; auto-update enabled.
- Throne System Proxy/TUN off while Happ is primary.

---

## Русский

Публичный навык для **Windows** (любой ПК). Это вариант **Happ (весь ОС)**. Альтернатива: Throne Agents only — [happ-throne-mutex.md](docs/happ-throne-mutex.md). Не включать System Proxy Happ и Throne вместе.

### Когда использовать

- Happ — основной прокси Windows.
- Маршрутизация RoscomVPN **WHITELIST**; Extra Whitelist2 DE→NL **если такие remark есть**.
- Обновление подписки 60 минут, автозапуск и автоподключение `lastused`.

### Когда не использовать

- Нужен VPN только для локальных агентов — вариант Throne Agents only.
- Искать профиль маршрутизации **WHITELIST2** — его нет.
- Писать URL подписки / `subs.db` в git.

### Автозапуск ≠ автоподключение

`--autostart` только запускает Happ. Официальный туннель: `subscription-autoconnect` + `lastused` (провайдер). Локальный nudge: `happ://connect` после старта процесса (не вендорный header API). Живая сессия уже с туннелем: только зарегистрировать nudge, не вызывать connect «чтобы применить»; проверку — после перезагрузки/входа.

### Жёсткие правила

1. Не печатать и не коммитить URL/токены подписки.
2. `happ://open` / `happ://connect`, не disconnect/kill.
3. **Не убивать Happ** и не вызывать `happ://disconnect`, пока удалённый доступ зависит от туннеля.
4. Пока Happ основной — Throne spare: без своего System Proxy/TUN.
5. Не выдумывать хост-пути и профиль `WHITELIST2`.

### Watch

Процесс есть, TUN/прокси нет → мягкий `happ://connect` (`-Force`, если WinINET ещё выглядит поднятым). Живая сессия уже с туннелем — connect не вызывать. Не убивать Happ.

### Успех

Процесс + задача автозапуска + nudge автоподключения (или явный skip). `useRouting` + WHITELIST. Extra Whitelist2 DE/NL только если remark есть. Интервал 60 минут. Throne System Proxy выключен.
