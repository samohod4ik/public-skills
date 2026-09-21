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
3. In Happ: enable **Use routing**; set active profile to the imported name (confirm in UI and in `routing.json`).
4. Soft open: `happ://open`. Never `happ://disconnect` or kill Happ while a remote session depends on the tunnel.

## Verify

```powershell
.\scripts\Get-HappRoutingNames.ps1
```

Expect `useRouting=True` and an active name corresponding to the WHITELIST import (exact display string can vary by export).

---

## Русский

Импортировать **WHITELIST**. Не создавать профиль маршрутизации `WHITELIST2`. Мягкий `happ://open`; не разрывать туннель и не убивать Happ, если от него зависит удалённый доступ.
