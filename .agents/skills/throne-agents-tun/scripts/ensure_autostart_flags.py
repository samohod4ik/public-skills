"""Set Throne logon flags so the last node + TUN come up with Agents only.

Safe only when Throne.exe/ThroneCore are not running (boot wrapper).
Uses a process probe, not running.marker — a stale marker must not block logon.
Does not start or stop Throne. Does not print subscription URLs.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_families import PROFILE_NAME
from assert_not_live_throne import throne_process_running

FLAGS = {
    "remember_enable": "true",
    "tun_mode_enabled": "true",
    "system_proxy_enabled": "false",
    "enable_tun_routing": "false",
    "vpn_strict_route": "false",
    "dns_final_out": "direct",
    "disable_private_range_bypass": "false",
}

REPORT_KEYS = (
    "remember_enable",
    "tun_mode_enabled",
    "active_routing",
    "current_route_id",
    "system_proxy_enabled",
    "enable_tun_routing",
    "vpn_strict_route",
    "dns_final_out",
    "disable_private_range_bypass",
    "remember_id",
)

BACKUP_KEEP = 5

ProbeFn = Callable[[], bool | None]


def _backup_stem(path: Path) -> bool:
    name = path.name
    return name.startswith("throne.db.bak-autostart-") and not name.endswith(
        ("-wal", "-shm")
    )


def prune_backups(db: Path, keep: int = BACKUP_KEEP) -> None:
    mains = sorted(
        (p for p in db.parent.iterdir() if p.is_file() and _backup_stem(p)),
        reverse=True,
    )
    for old in mains[keep:]:
        old.unlink(missing_ok=True)
        for suffix in ("-wal", "-shm"):
            extra = Path(str(old) + suffix)
            extra.unlink(missing_ok=True)


def backup_db(db: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = db.parent / f"throne.db.bak-autostart-{stamp}"
    shutil.copy2(db, dest)
    for suffix in ("-wal", "-shm"):
        extra = Path(str(db) + suffix)
        if extra.exists():
            shutil.copy2(extra, Path(str(dest) + suffix))
    return dest


def _upsert_setting(con: sqlite3.Connection, key: str, value: str) -> None:
    cur = con.execute("UPDATE settings SET value=? WHERE key=?", (value, key))
    if cur.rowcount == 0:
        con.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))


def _check_running(probe_fn: ProbeFn) -> int | None:
    running = probe_fn()
    if running is True:
        print("SKIP write: Throne.exe/ThroneCore is running")
        print("Flags will be applied on the next logon wrapper.")
        return 0
    if running is None:
        print("Refusing: could not probe Throne.exe/ThroneCore", file=sys.stderr)
        return 1
    return None


def apply(
    throne_dir: str | Path,
    *,
    profile_name: str = PROFILE_NAME,
    dry_run: bool = False,
    probe: ProbeFn | None = None,
) -> int:
    root = Path(throne_dir).expanduser()
    db = root / "config" / "throne.db"
    if not db.exists():
        print(f"Missing {db}", file=sys.stderr)
        return 1
    probe_fn = probe or throne_process_running
    early = _check_running(probe_fn)
    if early is not None:
        return early

    con = sqlite3.connect(db, timeout=15, isolation_level=None)
    bak: Path | None = None
    try:
        try:
            con.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            locked = _check_running(probe_fn)
            if locked is not None:
                return locked
            print(f"sqlite error: {exc}", file=sys.stderr)
            return 1
        locked = _check_running(probe_fn)
        if locked is not None:
            con.execute("ROLLBACK")
            return locked
        row = con.execute(
            "SELECT id FROM route_profiles WHERE name=?",
            (profile_name,),
        ).fetchone()
        if row is None:
            con.execute("ROLLBACK")
            print(f"No route profile named {profile_name!r}", file=sys.stderr)
            return 1
        profile_id = str(row[0])
        remember = con.execute(
            "SELECT value FROM settings WHERE key='remember_id'"
        ).fetchone()
        if remember is None or not str(remember[0]).strip():
            con.execute("ROLLBACK")
            print(
                "remember_id is empty; start a node once in the UI first",
                file=sys.stderr,
            )
            return 1
        rid = str(remember[0]).strip()
        exists = con.execute("SELECT 1 FROM profiles WHERE id=?", (rid,)).fetchone()
        if exists is None:
            con.execute("ROLLBACK")
            print(f"remember_id={rid} is not in profiles", file=sys.stderr)
            return 1
        if dry_run:
            con.execute("ROLLBACK")
            print(f"dry-run throne_dir={root}")
            print(f"dry-run {profile_name} current_route_id={profile_id}")
            for key, value in FLAGS.items():
                print(f"dry-run {key}={value}")
            print(f"dry-run remember_id={rid}")
            return 0
        bak = backup_db(db)
        for key, value in FLAGS.items():
            _upsert_setting(con, key, value)
        _upsert_setting(con, "active_routing", profile_name)
        _upsert_setting(con, "current_route_id", profile_id)
        con.execute("COMMIT")
    except sqlite3.OperationalError as exc:
        try:
            con.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        locked = _check_running(probe_fn)
        if locked is not None:
            return locked
        print(f"sqlite error: {exc}", file=sys.stderr)
        return 1
    except Exception:
        try:
            con.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        raise
    finally:
        con.close()

    if bak is not None:
        prune_backups(db)
    keys = REPORT_KEYS
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        rows = dict(
            con.execute(
                "SELECT key,value FROM settings WHERE key IN ({})".format(
                    ",".join("?" for _ in keys)
                ),
                keys,
            )
        )
    finally:
        con.close()
    print(f"backup={bak}")
    for key in keys:
        print(f"{key}={rows.get(key)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--throne-dir",
        default=os.environ.get("THRONE_DIR", ""),
        help="Throne install folder (does not start Throne).",
    )
    parser.add_argument(
        "--profile",
        default=PROFILE_NAME,
        help="Route profile name to select at logon.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print flags without writing.",
    )
    args = parser.parse_args(argv)
    if not args.throne_dir:
        print("THRONE_DIR / --throne-dir is required", file=sys.stderr)
        return 1
    return apply(args.throne_dir, profile_name=args.profile, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
