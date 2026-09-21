# Autostart vs autoconnect

**Autostart** launches Happ. **Autoconnect** brings the VPN / TUN / System Proxy session up. They are not the same. After reboot, `Happ.exe --autostart` can leave Happ running minimized with the tunnel still down.

This is the **Happ full-proxy** variant on any **Windows** PC. Do not combine with Throne System Proxy. See [happ-throne-mutex.md](happ-throne-mutex.md).

## Official Happ auto-connect (preferred)

Vendor docs: [App management — Auto-connect](https://www.happ.su/main/dev-docs/app-management) (RU: [Управление приложением](https://www.happ.su/main/ru/dev-docs/app-management)).

```
subscription-autoconnect: true|1
subscription-autoconnect-type: lastused|lowestdelay|random
```

Prefer **`lastused`** (reconnect the last selected server). When Extra Whitelist2 remarks exist, prefer Germany (`DE`) then Netherlands (`NL`) as that last selection.

Delivery (subscription provider — **never** commit the URL):

- HTTP response headers on the subscription, and/or
- Body lines: `#subscription-autoconnect: 1` and `#subscription-autoconnect-type: lastused`

Vendor `app-auto-start` is documented as **Android-only**. On Windows, launch is the Scheduled Task `Happ.exe --autostart`, not that header.

## What this repo can set locally (no provider)

No public Happ Windows **Preferences** registry value for autoconnect is documented. Scripts must not invent keys. `Set-HappAutoconnect.ps1` only *reports* existing HKCU names that already look like autoconnect.

Local options without a subscription provider:

1. **UI toggle** — if the installed build shows Settings **Auto-connect** / **Автоподключение**, enable it.
2. **Soft scheduled nudge** — current-user task waits until `Happ.exe` is running, then `happ://connect` **30–60s after logon** (default 45s). Local protocol nudge, not the vendor header API. Does not kill Happ.
3. **Watch** — if `Happ.exe` is running but TUN / System Proxy is down, run `scripts/Invoke-HappSoftConnect.ps1`. The script skips by default when WinINET already looks like a Happ local proxy (`ProxyEnable=1`); that is not a TUN check — pass `-Force` if the tunnel is actually down. Never `happ://disconnect` or `Stop-Process` while a remote session depends on the tunnel.

```powershell
.\scripts\Install-HappAutostart.ps1          # --autostart + delayed connect nudge
.\scripts\Set-HappAutoconnect.ps1            # nudge only (or -InspectOnly)
.\scripts\Invoke-HappSoftConnect.ps1         # happ://connect now (skip if WinINET looks up; -Force to fire)
.\scripts\Verify-HappExtraWhitelist2.ps1     # -SkipAutoconnectCheck if nudge was skipped
```

## Apply on a live Windows session

If Happ is already running **and** System Proxy / TUN is already up (example: WinINET `ProxyEnable=1` → `127.0.0.1:10809`):

- Do **not** fire `happ://connect` just to "apply" autoconnect.
- Only register / ensure the delayed logon nudge (`Set-HappAutoconnect.ps1`). That script schedules the task; it does not write Happ Preferences and does not need an immediate connect.
- Firing connect on a healthy live tunnel is unnecessary and can blip remote sessions that depend on the proxy.

No public Windows Preferences key is documented. `-InspectOnly` may list zero matching names; do not invent keys. Official `lastused` is subscription-provider only. The local path is the Settings UI toggle (if present) plus the scheduled `happ://connect` nudge.

## Field check

The delayed current-user Scheduled Task `Happ Proxy Autoconnect Nudge` (default ~45s after logon, wait until `Happ.exe` exists, then `happ://connect`) is a soft fallback when provider autoconnect headers are unavailable. Field-check it after a reboot or a fresh logon — not by firing connect on an already-healthy live session. It is not a substitute for official provider `lastused`.

## Competing WinDivert / TUN hijacks

Other WinDivert-based tools (for example Discord/YouTube bypass packs that install a `zapret`-style service) can coexist badly with Happ. Disable or remove competing WinDivert / TUN hijacks before relying on Happ autoconnect.

## Hard rule

Never kill Happ and never call `happ://disconnect` when remote access depends on the tunnel. Soft `happ://open` (focus) or `happ://connect` (bring tunnel up) only. Never enable Happ System Proxy and Throne System Proxy together.

---

## Русский

**Автозапуск** только открывает Happ. **Автоподключение** поднимает туннель. После перезагрузки `Happ.exe --autostart` может оставить Happ свёрнутым без VPN.

Официально автоподключение задаёт провайдер подписки (`lastused` предпочтителен). URL подписки в репозиторий не писать. Локально: тумблер в Settings, если есть; отложенный `happ://connect` после старта Happ.exe (через 30–60 с после входа). Это локальный protocol nudge, не header API вендора.

На уже работающей сессии, если Happ запущен и System Proxy/TUN уже поднят (`ProxyEnable=1` → локальный Happ, например `127.0.0.1:10809`), **не** вызывать `happ://connect` «чтобы применить» автоподключение: только задача `Happ Proxy Autoconnect Nudge`. На здоровом живом туннеле connect не нужен и может моргнуть удалённую сессию. `-InspectOnly` может показать ноль имён Preferences autoconnect/lastused — ключи не выдумывать.

Полевая проверка: отложенный nudge после перезагрузки или нового входа (мягкий fallback, не замена официальному lastused). Конкурирующие WinDivert/TUN-перехваты (в т.ч. обходы в стиле zapret) лучше снять до опоры на автоподключение Happ.

Если процесс есть, а TUN/прокси нет — мягкий `happ://connect`. Не убивать Happ и не вызывать `happ://disconnect`. Не включать System Proxy Happ и Throne вместе.
