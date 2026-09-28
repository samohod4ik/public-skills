# Routing: WHITELIST vs DEFAULT

Source: [hydraponique/roscomvpn-routing](https://github.com/hydraponique/roscomvpn-routing) (`HAPP/` deeplinks).

| Profile | Behavior (summary) | When to use |
|---------|-------------------|-------------|
| **WHITELIST** | Direct only for RU whitelist destinations; everything else via proxy | This skill default ("белые списки") |
| **DEFAULT** | RU/BY-oriented direct + selective proxy (YouTube/Telegram/GitHub, etc.) | Lighter split / alternate |

There is **no** public **WHITELIST2** routing profile. Do not invent one. **Extra Whitelist2** is a server-group remark, not a route name.

## Import (soft)

1. Download `HAPP/WHITELIST.DEEPLINK` from the RoscomVPN routing repo (or use [routing.help](https://routing.help) if it still mirrors these profiles).
2. Open the deeplink / `Start-Process` the `happ://routing/onadd/...` line from the file.
3. In HAPP 4.0.5+, the global routing screen is a read-only profile library. A successful deeplink import does **not** assign the profile to a subscription. Open **Servers → subscription containing the connected server → ⋯ → Routing**. If the profile is absent there, import it in that subscription's Routing screen. Set **Enable Routing = On** and select the intended profile under **Select Rule**. See [official release notes](https://github.com/Happ-proxy/happ-desktop/releases/tag/4.0.5).
4. Confirm the subscription name, toggle, and selected profile in the UI after import. On older versions without per-subscription routing, use the global routing controls instead.
5. Soft open: `happ://open`. Never `happ://disconnect` or kill Happ while a remote session depends on the tunnel.

## Verify

```powershell
.\scripts\Get-HappRoutingNames.ps1
```

The script lists profile names and per-subscription selections, but `routing.json` does not identify the subscription containing the **currently connected** server. On HAPP 4.0.5+, confirm that subscription in the UI, then run:

```powershell
.\scripts\Verify-HappExtraWhitelist2.ps1 -UiConfirmedRoutingProfile '<name shown in Select Rule>'
```

The verifier requires this explicit UI check. It checks for an enabled subscription selection and a profile with the same subscription ID and name; it cannot independently identify the active server. Even an empty `subConfigs` list is a per-subscription configuration and must not fall back to global fields. If `subConfigs` is absent, confirm the installed HAPP is older than 4.0.5 before passing `-ConfirmedLegacyHapp`. Do not use the global `useRouting` or `activeRoutingName` fields to claim success on HAPP 4.0.5+.

Finally, open the required sites in a browser. An automated HTTP 429 response establishes server reachability but not browser usability. In Mixed/TUN mode, `curl --noproxy '*'` still uses HAPP's TUN default route and is **not** a direct-path check. Check the actual domain rules in the selected geosite list before asserting that a site is present or absent; a tag alone does not prove it.

---

## Русский

Импортировать **WHITELIST**. Не создавать профиль маршрутизации `WHITELIST2`. В HAPP 4.0.5+ после импорта открыть **Servers → активная подписка → ⋯ → Routing**, включить **Enable Routing** и выбрать профиль в **Select Rule**. Общая библиотека профилей не подтверждает применение к подписке. Проверить сайты в браузере; HTTP 429 и `curl --noproxy '*'` при включённом TUN не подтверждают прямой маршрут. Мягкий `happ://open`; не разрывать туннель и не убивать Happ, если от него зависит удалённый доступ.
