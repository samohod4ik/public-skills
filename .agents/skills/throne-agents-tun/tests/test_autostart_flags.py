from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from agent_families import PROFILE_NAME
from ensure_autostart_flags import FLAGS, apply, main


def _make_db(root: Path, *, profile_id: int = 2, remember_id: str = "9") -> Path:
    config = root / "config"
    config.mkdir()
    db = config / "throne.db"
    con = sqlite3.connect(db)
    try:
        con.executescript(
            """
            CREATE TABLE route_profiles (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                default_outbound_id INTEGER
            );
            CREATE TABLE profiles (id INTEGER PRIMARY KEY);
            CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT);
            """
        )
        con.execute(
            "INSERT INTO route_profiles (id, name, default_outbound_id) VALUES (?,?,?)",
            (profile_id, PROFILE_NAME, -2),
        )
        con.execute("INSERT INTO profiles (id) VALUES (?)", (int(remember_id),))
        con.execute(
            "INSERT INTO settings (key, value) VALUES ('remember_id', ?)",
            (remember_id,),
        )
        con.execute(
            "INSERT INTO settings (key, value) VALUES ('remember_enable', 'false')"
        )
        con.execute(
            "INSERT INTO settings (key, value) VALUES ('tun_mode_enabled', 'false')"
        )
        con.execute(
            "INSERT INTO settings (key, value) VALUES ('active_routing', 'Default')"
        )
        con.commit()
    finally:
        con.close()
    return db


def _settings(db: Path) -> dict[str, str]:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return dict(con.execute("SELECT key, value FROM settings"))
    finally:
        con.close()


def test_apply_writes_flags_when_process_not_running(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    rc = apply(tmp_path, probe=lambda: False)
    assert rc == 0
    rows = _settings(db)
    for key, value in FLAGS.items():
        assert rows[key] == value
    assert rows["active_routing"] == PROFILE_NAME
    assert rows["current_route_id"] == "2"
    assert rows["remember_id"] == "9"
    backups = list((tmp_path / "config").glob("throne.db.bak-autostart-*"))
    assert backups


def test_skip_when_process_running_does_not_write(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    rc = apply(tmp_path, probe=lambda: True)
    assert rc == 0
    rows = _settings(db)
    assert rows["remember_enable"] == "false"
    assert rows["tun_mode_enabled"] == "false"
    assert not list((tmp_path / "config").glob("throne.db.bak-autostart-*"))


def test_probe_none_fail_closed(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    rc = apply(tmp_path, probe=lambda: None)
    assert rc == 1
    assert _settings(db)["remember_enable"] == "false"


def test_stale_running_marker_does_not_block(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    marker = tmp_path / "config" / "logs" / "running.marker"
    marker.parent.mkdir(parents=True)
    marker.write_text("stale\n", encoding="utf-8")
    rc = apply(tmp_path, probe=lambda: False)
    assert rc == 0
    assert _settings(db)["remember_enable"] == "true"


def test_empty_remember_id_refused(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    con = sqlite3.connect(db)
    con.execute("UPDATE settings SET value='' WHERE key='remember_id'")
    con.commit()
    con.close()
    rc = apply(tmp_path, probe=lambda: False)
    assert rc == 1
    assert _settings(db)["tun_mode_enabled"] == "false"
    assert not [
        p
        for p in (tmp_path / "config").iterdir()
        if p.name.startswith("throne.db.bak-autostart-")
    ]


def test_unknown_remember_id_refused(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    con = sqlite3.connect(db)
    con.execute("UPDATE settings SET value='404' WHERE key='remember_id'")
    con.commit()
    con.close()
    rc = apply(tmp_path, probe=lambda: False)
    assert rc == 1


def test_missing_profile_refused(tmp_path: Path) -> None:
    _make_db(tmp_path)
    rc = apply(tmp_path, profile_name="Missing", probe=lambda: False)
    assert rc == 1


def test_missing_db_refused(tmp_path: Path) -> None:
    rc = apply(tmp_path, probe=lambda: False)
    assert rc == 1


def test_dry_run_does_not_write(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    rc = apply(tmp_path, dry_run=True, probe=lambda: False)
    assert rc == 0
    rows = _settings(db)
    assert rows["remember_enable"] == "false"
    assert rows["tun_mode_enabled"] == "false"
    assert not list((tmp_path / "config").glob("throne.db.bak-autostart-*"))


def test_cli_requires_throne_dir() -> None:
    assert main([]) == 1


def test_cli_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import ensure_autostart_flags as mod

    _make_db(tmp_path)
    monkeypatch.setattr(mod, "throne_process_running", lambda: False)
    assert main(["--throne-dir", str(tmp_path), "--dry-run"]) == 0
    assert _settings(tmp_path / "config" / "throne.db")["remember_enable"] == "false"


def test_reprobe_running_skips_write(tmp_path: Path) -> None:
    db = _make_db(tmp_path)

    class Flip:
        def __init__(self) -> None:
            self.n = 0

        def __call__(self) -> bool:
            self.n += 1
            return self.n > 1

    rc = apply(tmp_path, probe=Flip())
    assert rc == 0
    assert _settings(db)["remember_enable"] == "false"
    assert not [
        p
        for p in (tmp_path / "config").iterdir()
        if p.name.startswith("throne.db.bak-autostart-")
    ]


def test_prune_keeps_last_backups(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    cfg = tmp_path / "config"
    for i in range(7):
        (cfg / f"throne.db.bak-autostart-2020010{i}-000000").write_bytes(b"old")
    rc = apply(tmp_path, probe=lambda: False)
    assert rc == 0
    mains = [
        p
        for p in cfg.iterdir()
        if p.name.startswith("throne.db.bak-autostart-")
        and not p.name.endswith(("-wal", "-shm"))
    ]
    assert len(mains) == 5


def test_wrapper_cmd_is_portable(skill_root: Path) -> None:
    text = (skill_root / "scripts" / "start_throne_autostart.cmd").read_text(
        encoding="utf-8"
    )
    assert "ensure_autostart_flags.py" in text
    assert 'start "" "%DIR%\\Throne.exe"' in text
    assert "starting Throne.exe anyway" in text
    assert "if errorlevel 1 exit /b 1" not in text
    assert "%DIR%" in text
    assert "LOCALAPPDATA" not in text


def test_register_task_uses_writer_cmd(skill_root: Path) -> None:
    text = (skill_root / "scripts" / "register_autostart_flags_task.ps1").read_text(
        encoding="utf-8"
    )
    assert "write_autostart_flags.cmd" in text
    assert "cmd.exe" not in text
    assert "-Python" in text
    assert "WindowsApps" in text


def test_rebind_bakes_python_and_keeps_highest(skill_root: Path) -> None:
    text = (skill_root / "scripts" / "rebind_throne_startup_task.ps1").read_text(
        encoding="utf-8"
    )
    assert "-Python" in text
    assert "start_throne_autostart.cmd" in text
    assert "expected Highest" in text
    assert "Disable-ScheduledTask" in text
    assert "-Principal $task.Principal" in text
    assert "-Trigger $task.Triggers" in text
    assert "-Settings $task.Settings" in text
    assert "WindowsApps" in text
    assert "FlagsTaskAbsent" in text
