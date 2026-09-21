# Migration from throne-cursor-only-public

`throne-cursor-only-public` is replaced by **`throne-agents-tun`**.

| Old | New |
|-----|-----|
| Skill id `throne-cursor-only-public` | `throne-agents-tun` |
| Profile **Cursor only** | **Agents only** |
| Proxy `Cursor.exe` + `cursor-agent` node | Same, plus Claude / Codex / Devin after discovery |
| HTTP proxy fallback | Still Cursor IDE only |

Keep a working **Cursor only** profile on a live workstation until a human switches UI to **Agents only**. An agent whose traffic already depends on Throne must not rewrite `throne.db` or toggle TUN.

Private machine skill `throne-cursor-only` (PAC / named intranet) is out of scope for this public folder. Do not copy corp domains here.
