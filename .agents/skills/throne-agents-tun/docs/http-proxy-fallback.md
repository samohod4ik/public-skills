# Cursor: app-level proxy без System Proxy

Два разных инструмента решают разные проблемы:

- **App-level `http.proxy`** — изоляция и отладка; только Cursor (и то, что уважает эти settings).
- **TUN + process split** — покрытие helpers / `cursor-agent` / Claude / Codex / Devin / proxy-unaware процессов; сложнее (DNS, loops, LAN).
- **HTTP/1.1** — транспортный workaround, когда proxy ломает HTTP/2 streaming. **Не** замена TUN и наоборот.

Полный отчёт research (санитизированный): [research-cursor-http-proxy.md](research-cursor-http-proxy.md).

Этот fallback **не** реализует профиль **Agents only**. Claude Code, Codex и Devin CLI его не используют.

## Когда что выбирать

| Цель | Способ |
|------|--------|
| Локальные агенты через VPN, есть admin | Throne TUN + профиль **Agents only** (основной для этого skill) |
| Только IDE Cursor, нет admin / TUN падает | App-level proxy на mixed inbound (ниже) |
| Streaming ломается, обычный HTTPS ок | HTTP/1.1 Compatibility — **не** включать TUN «от стриминга» |
| «Проверить Cursor» через System Proxy | **Нельзя** — уводит всю ОС |

## User Settings JSON

`F1` → **Preferences: Open User Settings (JSON)**. Порт — live mixed inbound Throne (часто `2080`; у других локальных клиентов бывают иные порты — смотреть inbound):

```json
{
  "http.proxy": "http://127.0.0.1:2080",
  "http.proxySupport": "override",
  "http.proxyStrictSSL": true,
  "cursor.general.disableHttp2": true
}
```

Если inbound только SOCKS (не mixed HTTP), попробуй `socks5://127.0.0.1:PORT` тем же набором ключей.

Смысл:

- `http.proxy` — локальный listener, **не** URL подписки.
- `http.proxySupport`: `override` — не WinINET; если сборка игнорирует ключ — настраивай Network UI.
- `http.proxyStrictSSL`: `true` всегда на старте. SSL inspection/DLP → exclude доменов Cursor на фильтре, не `false`.
- `cursor.general.disableHttp2` — community/compatibility; канон для HTTP/1.1 — UI ниже. Если HTTP/2 через ноду стабилен — ключ можно убрать.

## HTTP Compatibility Mode

Settings → **Browser & Network** → **HTTP Compatibility Mode** → **HTTP/1.1**, затем **полный перезапуск Cursor** (требуется доками Cursor).

Симптомы, когда это нужно:

- ответ агента приходит целиком сразу → buffering proxy;
- ~5 с задержки / stall при живом обычном HTTPS → нет HTTP/2 bidirectional;
- handshake `SSLV3_ALERT_HANDSHAKE_FAILURE` на части региональных путей.

HTTP/1.1 — fallback, не «всегда быстрее».

Там же **Required Domains** (в т.ч. `*.cursor.sh`, `*.cursor-cdn.com`, `*.cursorapi.com`) и **Run Diagnostics**.

## Диагностика (порядок)

1. Listener жив, порт совпадает с `http.proxy`.
2. Короткий Chat / sign-in.
3. **Network → Run Diagnostics**.
4. Отдельно проверить Agent streaming.
5. Обычный HTTPS ок, streaming нет → HTTP/1.1 + restart Cursor.
6. IDE ок, но agent CLI / helpers / Claude / Codex / Devin мимо proxy → эскалация на TUN + process rules (не наоборот).

## Throne в app-proxy режиме

1. Нода up.
2. System Proxy **off**.
3. TUN **off**.
4. `http.proxy` = `http://127.0.0.1:<inbound_socks_port>`.

Process-rules **Agents only** для IDE не обязательны в этом режиме. Для `cursor-agent`, Claude, Codex, Devin без TUN покрытия нет — тогда нужен TUN.

## TUN vs app-proxy (кратко)

| | App-proxy | TUN process split |
|--|-----------|-------------------|
| Blast radius | в основном Cursor | ОС-уровень, LAN/DNS риски |
| Покрытие | может миновать extensions/CLI/terminal | ловит named processes |
| Когда | нет admin; проверка пути Cursor | нужен agent/helpers; admin есть |

На Windows: Strict Route **off**, Tun routing **off**, allowlist выше process rules; не заворачивать `127.0.0.1` / mixed inbound обратно в TUN.

## Ограничения

- Медленный агент часто = плохая нода, не HTTP/1.1.
- Не считать один успешный Chat доказательством, что Tab/Agent/terminal/extensions тоже на proxy.
- Не публиковать URL подписок.
