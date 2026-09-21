from __future__ import annotations

from pathlib import Path

import pytest

from assert_not_live_throne import assert_not_live, live_reason


def test_empty_tree_is_ok(tmp_path: Path) -> None:
    assert live_reason(tmp_path) is None
    assert assert_not_live(tmp_path) == tmp_path


def test_running_marker_refused(tmp_path: Path) -> None:
    marker = tmp_path / "config" / "logs" / "running.marker"
    marker.parent.mkdir(parents=True)
    marker.write_text("live\n", encoding="utf-8")
    assert live_reason(tmp_path)
    with pytest.raises(SystemExit, match="running.marker"):
        assert_not_live(tmp_path)


def test_live_guard_file_refused(tmp_path: Path) -> None:
    (tmp_path / ".throne-live-do-not-edit").write_text("no\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="do-not-edit"):
        assert_not_live(tmp_path)


def test_throne_exe_while_process_running(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import assert_not_live_throne as guard

    (tmp_path / "Throne.exe").write_text("stub\n", encoding="utf-8")

    class FakeCompleted:
        stdout = "yes\n"
        stderr = ""
        returncode = 0

    monkeypatch.setattr(guard.subprocess, "run", lambda *_args, **_kwargs: FakeCompleted())
    with pytest.raises(SystemExit, match="running"):
        assert_not_live(tmp_path)


def test_probe_error_with_exe_fail_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import assert_not_live_throne as guard

    (tmp_path / "Throne.exe").write_text("stub\n", encoding="utf-8")

    def boom(*_args, **_kwargs):
        raise OSError("probe failed")

    monkeypatch.setattr(guard.subprocess, "run", boom)
    with pytest.raises(SystemExit, match="could not probe"):
        assert_not_live(tmp_path)


def test_probe_nonzero_exit_with_exe_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import assert_not_live_throne as guard

    (tmp_path / "Throne.exe").write_text("stub\n", encoding="utf-8")

    class FakeCompleted:
        stdout = ""
        stderr = "error"
        returncode = 1

    monkeypatch.setattr(guard.subprocess, "run", lambda *_args, **_kwargs: FakeCompleted())
    with pytest.raises(SystemExit, match="could not probe"):
        assert_not_live(tmp_path)
