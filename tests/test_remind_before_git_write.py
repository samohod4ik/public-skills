#!/usr/bin/env python3
"""Contract tests for hooks/remind_before_git_write.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "hooks" / "remind_before_git_write.py"


def run(payload: dict) -> dict:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def test_cursor_shell_commit_allows_with_message() -> None:
    body = run({"command": "git commit -m test"})
    assert body["permission"] == "allow"
    assert "agent_message" in body
    assert "continue" not in body


def test_cursor_mcp_push_allows_with_message() -> None:
    body = run({"tool_name": "git_push"})
    assert body["permission"] == "allow"
    assert "agent_message" in body


def test_cursor_unrelated_command_has_no_message() -> None:
    body = run({"command": "git status"})
    assert body == {"permission": "allow"}


def test_pretooluse_bash_commit_uses_continue() -> None:
    body = run(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "git commit -m x"},
        }
    )
    assert body.get("continue") is True
    assert "systemMessage" in body
    assert "permission" not in body


def test_pretooluse_generic_shell_skips_reminder() -> None:
    body = run(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "ls"},
        }
    )
    assert body == {"continue": True}


if __name__ == "__main__":
    test_cursor_shell_commit_allows_with_message()
    test_cursor_mcp_push_allows_with_message()
    test_cursor_unrelated_command_has_no_message()
    test_pretooluse_bash_commit_uses_continue()
    test_pretooluse_generic_shell_skips_reminder()
    print("PASS remind_before_git_write")
