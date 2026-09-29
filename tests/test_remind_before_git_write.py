#!/usr/bin/env python3
"""Contract tests for hooks/remind_before_git_write.py, split by --format."""
from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "hooks" / "remind_before_git_write.py"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
response_for = importlib.import_module("hooks.remind_before_git_write").response_for

_CLAUDE_COMMIT = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Bash",
    "tool_input": {"command": "git commit -m x"},
}
_CLAUDE_LS = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Bash",
    "tool_input": {"command": "ls"},
}


def run(payload: dict, *args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def _assert_advisory_reminder(output_format: str, body: dict) -> None:
    if output_format == "cursor":
        assert body["permission"] == "allow"
        assert body["agent_message"]
        assert "continue" not in body
    elif output_format == "claude":
        assert body["continue"] is True
        assert body["systemMessage"]
        assert "permission" not in body
    elif output_format == "codex":
        assert body["systemMessage"]
        assert "continue" not in body
        assert "permission" not in body
    else:
        assert body["hookSpecificOutput"]["additionalContext"]
        assert "continue" not in body
        assert "permission" not in body


def test_no_pager_commit_and_push_with_global_options() -> None:
    commands = (
        "git --no-pager commit -m x",
        "git --no-pager push",
        "git -C repo --no-pager commit -m x",
        "git --no-pager -C 'repo with spaces' push",
        "git --git-dir=.git --no-pager push",
        "git --no-pager --git-dir .git commit -m x",
        "git --work-tree=. --no-pager commit -m x",
        "git --no-pager --work-tree . push",
        "git -C repo --git-dir=.git --no-pager --work-tree=. commit -m x",
    )
    for command in commands:
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }
        for output_format in ("cursor", "claude", "codex", "devin"):
            _assert_advisory_reminder(
                output_format, response_for(payload, output_format)
            )


def test_no_pager_status_does_not_remind() -> None:
    for command in ("git --no-pager status", "git -C repo --no-pager status"):
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }
        expected = {
            "cursor": {"permission": "allow"},
            "claude": {"continue": True},
            "codex": {},
            "devin": {},
        }
        for output_format, body in expected.items():
            assert response_for(payload, output_format) == body


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


def test_cursor_format_flag_matches_default() -> None:
    body = run({"command": "git commit -m test"}, "--format", "cursor")
    assert body["permission"] == "allow"
    assert "agent_message" in body
    assert "continue" not in body


def test_claude_bash_commit_uses_continue() -> None:
    body = run(_CLAUDE_COMMIT, "--format", "claude")
    assert body.get("continue") is True
    assert "systemMessage" in body
    assert "permission" not in body


def test_claude_generic_shell_skips_reminder() -> None:
    body = run(_CLAUDE_LS, "--format", "claude")
    assert body == {"continue": True}


def test_claude_powershell_commit_uses_continue() -> None:
    body = run(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "PowerShell",
            "tool_input": {"command": "git commit -m x"},
        },
        "--format",
        "claude",
    )
    assert body.get("continue") is True
    assert "systemMessage" in body
    assert "permission" not in body


def test_claude_git_commit_tool_uses_continue() -> None:
    body = run(
        {"hook_event_name": "PreToolUse", "tool_name": "git_commit"},
        "--format",
        "claude",
    )
    assert body.get("continue") is True
    assert "systemMessage" in body
    assert "permission" not in body


def test_claude_git_push_tool_uses_continue() -> None:
    body = run(
        {"hook_event_name": "PreToolUse", "tool_name": "git_push"},
        "--format",
        "claude",
    )
    assert body.get("continue") is True
    assert "systemMessage" in body
    assert "permission" not in body


def test_pretooluse_without_format_falls_back_to_claude() -> None:
    body = run(_CLAUDE_COMMIT)
    assert body.get("continue") is True
    assert "systemMessage" in body
    assert "permission" not in body


def test_codex_commit_system_message_no_continue() -> None:
    body = run(_CLAUDE_COMMIT, "--format", "codex")
    assert "systemMessage" in body
    assert "continue" not in body
    assert "permission" not in body
    assert "hookSpecificOutput" not in body


def test_codex_unrelated_is_empty() -> None:
    body = run(_CLAUDE_LS, "--format", "codex")
    assert body == {}
    assert "continue" not in body
    assert "permission" not in body


def test_devin_commit_additional_context_no_continue() -> None:
    body = run(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "exec",
            "tool_input": {"command": "git commit -m x"},
        },
        "--format",
        "devin",
    )
    assert body["hookSpecificOutput"]["additionalContext"]
    assert "continue" not in body
    assert "permission" not in body


def test_devin_unrelated_is_empty() -> None:
    body = run(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "exec",
            "tool_input": {"command": "ls"},
        },
        "--format",
        "devin",
    )
    assert body == {}
    assert "continue" not in body
    assert "permission" not in body


def test_devin_git_commit_tool_reminds() -> None:
    body = run(
        {"hook_event_name": "PreToolUse", "tool_name": "git_commit"},
        "--format",
        "devin",
    )
    assert "additionalContext" in body.get("hookSpecificOutput", {})
    assert "continue" not in body
    assert "permission" not in body


if __name__ == "__main__":
    test_no_pager_commit_and_push_with_global_options()
    test_no_pager_status_does_not_remind()
    test_cursor_shell_commit_allows_with_message()
    test_cursor_mcp_push_allows_with_message()
    test_cursor_unrelated_command_has_no_message()
    test_cursor_format_flag_matches_default()
    test_claude_bash_commit_uses_continue()
    test_claude_generic_shell_skips_reminder()
    test_claude_powershell_commit_uses_continue()
    test_claude_git_commit_tool_uses_continue()
    test_claude_git_push_tool_uses_continue()
    test_pretooluse_without_format_falls_back_to_claude()
    test_codex_commit_system_message_no_continue()
    test_codex_unrelated_is_empty()
    test_devin_commit_additional_context_no_continue()
    test_devin_unrelated_is_empty()
    test_devin_git_commit_tool_reminds()
    print("PASS remind_before_git_write")
