# Подводные камни

Типичные сбои при настройке Throne + Agents-only split tunnel.

## TUN и права администратора

- Режим **TUN** требует elevation. «Запуск от имени администратора» без реальных прав → TUN не поднимется.
- Ошибка вида `configure tun interface: create adapter: Cannot create a file when that file already exists | open existing adapter: Element not found` — залипший/битый TUN-адаптер. В UI Throne: **Сброс** ядра, затем снова нода → TUN. Не включать System Proxy «вместо».
- Без TUN process-rules **не** видят чужой трафик: split по процессу не работает.

## System Proxy — не fallback

System Proxy пишет WinINET на **всю** ОС: ломает сосуществование с другим VPN/корпоративным каналом и уводит в proxy приложения, которые должны остаться direct. Для проверки «открывается ли Cursor» это ложный позитив.

Правильный fallback без TUN: app-level `http.proxy` **только в Cursor** → mixed inbound Throne. Claude/Codex/Devin этим не покрыть. См. [http-proxy-fallback.md](http-proxy-fallback.md).

## GUI сбрасывает маршрутизацию

После кликов в UI Throne часто сам ставит:

- `active_routing=Default` (default outbound = proxy → при TUN уезжает весь ПК)
- `dns_final_out=remote` (split-horizon intranet/SSO получает публичные IP → WAF 403)

После любой UI-сессии проверить: профиль **Agents only**, `dns_final_out=direct`.

## Allowlist обязателен

Процесс матчится целиком. Всё, что не direct-правило, уходит в VPN — включая SSO, intranet-имена, Git/MCP/пакеты. Пустой allowlist = агент не достанет внутренние DNS. Агент должен **спросить** список, не выдумывать и не читать PAC с диска без вложения в чат.

## Пути процессов локальны

Снимать discovery на машине TUN. После обновления Cursor/Claude/Codex/Devin — снова CIM. Не матчить голый `node.exe` (системный Node уйдёт в proxy). Не матчить каждый `ChatGPT.exe` — только путь `OpenAI.Codex`. Не использовать `%LOCALAPPDATA%` как каталог без имени exe.

Electron/Node helpers, которые не совпали с name/path/regex, остаются **direct**. Это ожидаемо; не расширять правило до всего `node.exe`.

## WebSocket / DPI

Claude Chrome bridge и Codex sampling держат WSS на TCP/443. TLS inspection, короткий idle timeout или запрет `Upgrade: websocket` рвут стрим при «живом» обычном HTTPS. Не включать Tun routing / Strict Route «чтобы починить стрим».

## Подписка

- URL только в UI Throne, не в skill/git/чат.
- Форматы других клиентов (например `vpn://`) Throne может не принять — тогда ручной профиль или конвертация.
- Автообновление (`sub_auto_update`) требует, чтобы Throne **работал**. Обновление может остановить активный профиль (#1305); таймер в части сборок сбоил (#1528) — после refresh проверить ноду + TUN.

## Автозапуск

С Throne 1.1.2 — **Task Scheduler** из UI (не registry). Один раз UAC при создании задачи; если Throne был elevated, последующие старты тоже elevated. Путь установки лучше ASCII — Unicode-пути ломали autostart в части сборок.

**Start with Windows ≠ TUN.** Задача только поднимает GUI. Нода и TUN после ребута восстанавливаются при **Remember last profile** (`remember_enable=true`). Иначе: Throne elevated, профиль **Agents only** выбран, TUN Off, ядро не запущено. GUI часто сбрасывает `remember_enable=false` на выходе — поэтому logon-writer `scripts/ensure_autostart_flags.py` (задача `ThroneAutostartFlags` или обёртка `start_throne_autostart.cmd`) пишет флаги, пока процесс не запущен. Не писать `tun_mode_enabled=true` в живой `throne.db` из агента. После rebind не переключать «запуск с Windows» в UI — задача вернётся на голый `Throne.exe`. См. [Throne #1547](https://github.com/throneproj/Throne/issues/1547).

## Агент уже сидит на Throne

Если текущий Cursor/agent ходит через этот же Throne, **нельзя** из агента гасить Throne/ядро/TUN или переписывать `throne.db` — агент отрежет сам себя. UI-правки делает пользователь. Тесты — fixture или cloud VM без `config/logs/running.marker`.

## Tun routing

`enable_tun_routing=true` вместе с process rules и Strict off → петли (Throne #1365). Держать **Off**.

## Devin Cloud

IP allowlist Cognition относится к **входу на ваши SCM/артефакты**, не к TUN ноутбука. Не класть эти CIDR в proxy-правила профиля **Agents only**.
