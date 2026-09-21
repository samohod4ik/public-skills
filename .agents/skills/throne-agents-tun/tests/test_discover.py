from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from render_agents_only_rules import render_profile

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "discover_agent_processes.ps1"

SNAPSHOT = [
    {
        "Name": "Cursor.exe",
        "ExecutablePath": r"C:\Users\fixture\AppData\Local\Programs\cursor\Cursor.exe",
    },
    {
        "Name": "cursor.exe",
        "ExecutablePath": r"C:\Users\fixture\AppData\Local\Programs\cursor\cursor.exe",
    },
    {
        "Name": "node.exe",
        "ExecutablePath": r"C:\Program Files\nodejs\node.exe",
    },
    {
        "Name": "node.exe",
        "ExecutablePath": r"C:\Users\fixture\AppData\Local\cursor-agent\versions\node.exe",
    },
    {
        "Name": "node.exe",
        "ExecutablePath": r"C:\Users\fixture\AppData\Local\cursor-agent\versions\1.0\node.exe",
    },
    {
        "Name": "ChatGPT.exe",
        "ExecutablePath": r"C:\Program Files\ChatGPT\ChatGPT.exe",
    },
    {
        "Name": "ChatGPT.exe",
        "ExecutablePath": r"C:\Program Files\WindowsApps\OpenAI.Codex_1.0.0_x64__x\app\ChatGPT.exe",
    },
    {
        "Name": "language_server_windows_x64.exe",
        "ExecutablePath": r"C:\Program Files\SomeIDE\language_server_windows_x64.exe",
    },
    {
        "Name": "language_server_windows_x64.exe",
        "ExecutablePath": r"C:\Users\fixture\Devin\resources\app\extensions\windsurf\bin\language_server_windows_x64.exe",
    },
    {
        "Name": "Devin.exe",
        "ExecutablePath": r"C:\Users\fixture\Devin\Devin.exe",
    },
]


def _run_discover(snapshot_path: Path) -> dict:
    completed = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-SnapshotPath",
            str(snapshot_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return json.loads(completed.stdout)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell discovery is Windows-only")
def test_snapshot_classifies_and_skips_broad_names(tmp_path: Path) -> None:
    snap = tmp_path / "snapshot.json"
    snap.write_text(json.dumps(SNAPSHOT), encoding="utf-8")
    data = _run_discover(snap)
    names = []
    paths = []
    for family in data["families"].values():
        assert isinstance(family["process_names"], list)
        assert isinstance(family["process_paths"], list)
        names.extend(family["process_names"])
        paths.extend(family["process_paths"])
    lowered_names = {n.lower() for n in names}
    assert "node.exe" not in lowered_names
    assert "chatgpt.exe" not in lowered_names
    assert "language_server_windows_x64.exe" not in lowered_names
    assert "Cursor.exe" in data["families"]["cursor"]["process_names"]
    assert any(p.lower().endswith("\\cursor.exe") for p in data["families"]["cursor"]["process_paths"])
    assert any(p.lower().endswith("\\versions\\1.0\\node.exe") for p in data["families"]["cursor"]["process_paths"])
    assert not any(p.lower().endswith("\\versions\\node.exe") for p in paths)
    assert not any(p.lower().endswith("\\nodejs\\node.exe") for p in paths)
    assert any("openai.codex" in p.lower() for p in data["families"]["codex"]["process_paths"])
    assert not any(p.lower().endswith("\\chatgpt\\chatgpt.exe") for p in paths)
    assert any("windsurf\\bin\\language_server_windows_x64.exe" in p.lower() for p in data["families"]["devin"]["process_paths"])
    assert "Devin.exe" in data["families"]["devin"]["process_names"]
    profile = render_profile(data, {})
    assert "cursor" in profile["covered_families"]
    assert "devin" in profile["covered_families"]
    assert "codex" in profile["covered_families"]


@pytest.mark.skipif(os.name != "nt", reason="PowerShell discovery is Windows-only")
def test_single_process_stays_json_array(tmp_path: Path) -> None:
    snap = tmp_path / "snapshot.json"
    snap.write_text(
        json.dumps(
            [
                {
                    "Name": "Cursor.exe",
                    "ExecutablePath": r"C:\Users\fixture\AppData\Local\Programs\cursor\Cursor.exe",
                }
            ]
        ),
        encoding="utf-8",
    )
    data = _run_discover(snap)
    names = data["families"]["cursor"]["process_names"]
    assert names == ["Cursor.exe"]
    assert data["families"]["claude"]["process_names"] == []
    assert data["families"]["cursor"]["path_regexes"] == []
