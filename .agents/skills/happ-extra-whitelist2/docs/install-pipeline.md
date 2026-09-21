# Install pipeline

Ordered steps for a clean **Windows** Happ full-proxy install (desktop, laptop, or VM). For Agents-only TUN instead, stop here and use [happ-throne-mutex.md](happ-throne-mutex.md) — do not run this pipeline beside Throne System Proxy.

1. **Download / install Happ** from the vendor ([happ.su](https://www.happ.su)). Discover `Happ.exe` (do not assume one path). Common vendor locations include `%ProgramFiles%\FlyFrogLLC\Happ\Happ.exe` and the `(x86)` equivalent; pass `-HappExe` if neither exists.
2. **First launch** — complete vendor onboarding; leave System Proxy + TUN as Happ manages them. Confirm Throne (if installed) has System Proxy and TUN **off**.
3. **Subscription** — add via UI or a **private** local URL file. Never paste the URL into git, issues, or chat logs.
4. **Routing** — import RoscomVPN **WHITELIST** ([routing.md](routing.md)); enable Use routing. There is no `WHITELIST2` routing profile.
5. **Exit pick** — if the subscription lists Extra Whitelist2 remarks, prefer DE then NL ([extra-whitelist2.md](extra-whitelist2.md)). Skip this step if those remarks are absent.
6. **Refresh interval** — `scripts/Set-HappSubscriptionRefresh.ps1` → 60 minutes.
7. **Autostart (launch only)** — `scripts/Install-HappAutostart.ps1` → `Happ.exe --autostart` at logon. This does **not** by itself connect the VPN.
8. **Autoconnect** — official `lastused` via subscription headers/body when the provider can set them; plus the local delayed `happ://connect` nudge after Happ.exe (installed by step 7 unless `-SkipAutoconnectNudge`). Details: [autoconnect.md](autoconnect.md).
9. **Soft open / connect** — `scripts/Invoke-HappSoftOpen.ps1` (`happ://open`) to focus; `scripts/Invoke-HappSoftConnect.ps1` (`happ://connect`) only if the tunnel is down. On a live session that is already up, do not fire connect just to apply autoconnect (see [autoconnect.md](autoconnect.md)).
10. **Verify** — `scripts/Verify-HappExtraWhitelist2.ps1` (add `-SkipAutoconnectCheck` only if the nudge was skipped).

## Watch

If the Happ **process** is running but TUN / System Proxy is down: soft `happ://connect` (`Invoke-HappSoftConnect.ps1`; `-Force` if WinINET still looks up). If the live session is already tunneled, skip connect and field-check the logon nudge after reboot. Do **not** kill Happ. Do **not** call `happ://disconnect` while a remote session depends on the tunnel.

## Failure modes

| Symptom | Likely cause | Soft fix |
|---------|--------------|----------|
| No servers | Sub not added / update failed | UI Update; check registry 60m; `happ://open` |
| Full tunnel, no split | Routing empty / Use routing off | Re-import WHITELIST; enable useRouting |
| Wrong country | Connected to a non-preferred remark | Reselect in UI if Extra Whitelist2 DE/NL exist |
| Happ up, VPN down after reboot | Autostart without autoconnect | Enable provider `lastused`; ensure logon nudge; `happ://connect` only if still down |
| Tunnel blip on an already-up live session | Fired `happ://connect` just to "apply" | Register the logon nudge only; field-check after reboot |
| Autoconnect flaky with another TUN | Competing WinDivert / TUN hijack | Disable or remove the other hijack before relying on Happ |
| Remote agents drop | Disconnect/kill Happ | Prefer soft open/connect; never kill |
| Split-brain proxy | Happ + Throne System Proxy both on | Turn one off; see [happ-throne-mutex.md](happ-throne-mutex.md) |

---

## Русский

Порядок для варианта **Happ** на любом Windows ПК. Для TUN только Agents (Throne Agents only, не Cursor-only) — другой вариант, не этот pipeline рядом с Throne System Proxy. **Автозапуск ≠ автоподключение.** `--autostart` только запускает Happ; туннель поднимает `subscription-autoconnect` (`lastused`) и/или мягкий `happ://connect` после Happ.exe. На живой сессии с уже поднятым туннелем connect не вызывать «чтобы применить». Extra Whitelist2 DE→NL — предпочтение, **если** такие remark есть. Нет профиля маршрутизации `WHITELIST2`. URL подписки не коммитить. Если процесс есть, а TUN/прокси нет — `happ://connect`, не убивать Happ.
