# Extra Whitelist2 (server group)

**Extra Whitelist2** is a **remark / folder label** on subscription servers inside Happ — not a RoscomVPN routing profile. There is no public routing profile named `WHITELIST2`. Do not invent one.

Remarks are **subscription-specific**. Do not assume Extra Whitelist2 or DE/NL nodes exist.

## Selection policy (when those remarks exist)

1. Filter servers whose remark/title contains `Extra Whitelist2` (exact phrase; do not use plain `Extra Whitelist` without `2`).
2. Prefer **Germany** (`Германия`, `Germany`, `DE`) among those. Treat informal `GE` as Germany only when the remark clearly means Germany, not Georgia.
3. Else prefer **Netherlands** (`Нидерланды`, `Netherlands`, `NL`).
4. Other Extra Whitelist2 countries (for example FI/SE/LT) are fallbacks only if DE/NL are missing or unhealthy.
5. If no Extra Whitelist2 remarks exist, leave the user's current / `lastused` server; do not invent labels.

## How to apply

Happ does not expose a stable public deeplink for "connect to remark X". Agents should:

1. Open Happ UI → server / profile list.
2. If an Extra Whitelist2 group or matching remarks exist, connect DE, else NL.
3. Confirm connectivity with a probe the user allows.
4. After reboot, rely on **autoconnect `lastused`** and/or soft `happ://connect` — not on kill/relaunch.

Synthetic example labels (fixtures only): see `fixtures/example-server-labels.txt`.

## Do not

- Hardcode real hostnames, ports, or UUIDs from a live subscription.
- Confuse this label with RoscomVPN **WHITELIST** routing.
- Treat Extra Whitelist2 / DE / NL as always present.

---

## Русский

**Extra Whitelist2** — метка серверов в подписке, не профиль маршрутизации. Профиля `WHITELIST2` нет. DE→NL — предпочтение **если** такие remark есть; иначе не выдумывать. После перезагрузки — `lastused` / `happ://connect`, не убивать Happ.
