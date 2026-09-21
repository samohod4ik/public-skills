# Architecture

```text
Internet
    → Happ (System Proxy 127.0.0.1:10809 + TUN)   # typical local listen; confirm on the host
        → RoscomVPN WHITELIST routing (RU whitelist direct; else proxy)
        → Selected outbound: last used server; prefer Extra Whitelist2 DE then NL when those remarks exist
```

Applies to any **Windows** PC where Happ is the **primary** proxy client. Alternate path (Throne Agents only, OS direct): [happ-throne-mutex.md](happ-throne-mutex.md).

| Layer | Role |
|-------|------|
| Happ | Primary Windows client (FlyFrog). **Autostart** = `Happ.exe --autostart` (launch). **Autoconnect (official)** = provider `lastused`. **Autoconnect (local)** = delayed `happ://connect` after Happ.exe. |
| Routing JSON | `%LOCALAPPDATA%\Happ\routing.json` — `useRouting`, `activeRoutingName`, `routings[]`. |
| Geo assets | Often under `%LOCALAPPDATA%\Happ\routing\0\<ProfileName>\` (`geoip.dat`, `geosite.dat`). |
| Subscription | Opaque in Happ; refresh interval via HKCU registry (Windows keys are minutes). Official autoconnect flags are **subscription-delivered**, not a documented registry value. |
| Throne / other clients | Spare only while Happ is primary — their System Proxy and TUN **off**. Never dual System Proxy. |

## Autostart vs autoconnect

| Mechanism | What it does | What it does not do |
|-----------|----------------|---------------------|
| Scheduled Task `Happ.exe --autostart` | Starts Happ at logon (often minimized) | Does not guarantee TUN/proxy up |
| `subscription-autoconnect` + `lastused` | Official auto-connect on app launch | Requires provider headers/body (no URLs in this repo) |
| Delayed `happ://connect` | Local protocol nudge after Happ.exe is running (30–60s after logon) | Not the vendor header API; does not kill Happ; not `happ://disconnect` |

Vendor `app-auto-start` is Android-only in [official docs](https://www.happ.su/main/dev-docs/app-management).

## Registry (subscription refresh)

Path: `HKCU\Software\Happ\OrganizationDefaults\Preferences\Subscriptions`

| Value | Recommended |
|-------|-------------|
| `subsUpdateTimerInMinutes` | `60` |
| `subsAutoUpdateInterval` | `60` (if present) |
| `subsAutoUpdate` | `true` |
| `subsUpdateOnOpen` | `true` |

Windows keys are minutes; vendor docs may say hours. No public autoconnect value is documented under Preferences — do not invent one.

---

## Русский

Слои те же на любом Windows ПК, если выбран вариант Happ. Автозапуск только поднимает процесс; официальное автоподключение — `lastused` от провайдера; локальный nudge — `happ://connect` после Happ.exe. Реестр здесь — интервал обновления подписки. Extra Whitelist2 DE/NL — если такие серверы есть. Throne на целевом ПК — spare, без своего System Proxy.
