# Cloud smoke test

Hermetic pytest/CI never enable TUN. Dynamic check on a disposable Windows VM (or GitHub-hosted `windows-latest` only for the static job). Do **not** run it against a Throne install that an existing Cursor/agent session already uses.

Rollback on the VM: quit Throne, delete the test profile / restore `throne.db` from the backup taken on that VM, disable TUN. Destroy the VM when done.

## Static job (`windows-latest`)

From the skill root (this skill folder):

```text
python -m pip install pytest
python scripts/validate_skill.py
python -m pytest tests -q
```

No subscription, no GUI, no admin TUN, no production host.

Workflow file at repo root: `.github/workflows/validate-throne-agents-tun.yml`. Copy from [github-actions-validate-skill.yml](github-actions-validate-skill.yml) if the GitHub token cannot push workflows.

## Dynamic VM (admin + throwaway subscription)

1. New Windows VM. Do not run against a live workstation session; use a disposable VM.
2. Install Cursor / Claude / Codex / Devin **only as available**. Discovery may cover a subset; record which families were present.
3. Extract Throne Portable ZIP to a **new** folder (not a copy of a live `running.marker` tree).
4. Import a **test** subscription in the Throne UI only (`Ctrl+V`). Never paste it into git or chat.
5. Confirm `python scripts/assert_not_live_throne.py --throne-dir <VM_THRONE>` succeeds **before** first start, then start Throne, quit fully, backup `config/throne.db`.
6. Run discovery → render → write profile **Agents only** while Throne is fully quit.
7. Start Throne elevated. Select a node. TUN on, System Proxy off, Strict Route off, Tun routing off, `dns_final_out=direct`.
8. Log checks:
   - Discovered agent exe → public HTTPS → `outbound/socks[proxy]`
   - Browser / `ping` from another app → `outbound/direct`
   - RFC1918 / allowlist (if any) → `direct`
   - `C:\Program Files\nodejs\node.exe` if present → `direct`
9. Optional live vendor checks (only with test accounts): one Claude Code request, one Codex CLI request, one Devin CLI request. Missing credentials → skip, do not fail the static gate.
10. Rollback: TUN off, restore backup db **on the VM**, or delete the VM.
11. Optional reboot check: with Throne quit, run `python scripts/ensure_autostart_flags.py --throne-dir <VM_THRONE> --dry-run` (must not SKIP if the process is down), then `register_autostart_flags_task.ps1 -ThroneDir <VM_THRONE> -Python <python.exe>`. Reboot the VM. Expect **Agents only**, last node, TUN on. If `config/autostart-flags.log` says `SKIP write`, the flags task lost the race — rebind with `rebind_throne_startup_task.ps1 -ThroneDir <VM_THRONE> -Python <python.exe>` (admin, not the WindowsApps stub) and reboot again. After a verified rebind the Limited flags task is disabled; do not leave both enabled.

## Fail the release if

- Renderer accepted `processName:node.exe`
- Default outbound is proxy
- Unrelated app hits `socks[proxy]`
- Safety guard allows a tree with `config/logs/running.marker`
- Skill tree contains subscription URLs or machine home paths
