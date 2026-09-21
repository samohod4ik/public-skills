"""Emit a non-blocking reminder for git commit/push in an agent session."""

from __future__ import annotations

import json
import re
import sys

_SHELL_GIT_ACTION = re.compile(
    r"""(?:^|[;&|]\s*|\s)git(?:\.exe)?\s+
        (?:
            -C\s+(?:"[^"]*"|'[^']*'|\S+)\s+
            |(?:--git-dir|--work-tree)(?:=|\s+)(?:"[^"]*"|'[^']*'|\S+)\s+
        )*
        (?:commit|push)\b""",
    re.IGNORECASE | re.VERBOSE,
)
_MCP_GIT_ACTION = re.compile(r"(?:^|[^A-Za-z0-9_])git_(?:commit|push)$", re.IGNORECASE)
_REMINDER = (
    "Before commit/push, verify project docs and AGENTS.md. "
    "This hook is a reminder only; it does not block the action."
)


def _tool_name(payload: dict) -> str:
    return str(payload.get("tool_name") or payload.get("toolName") or "")


def _command_text(payload: dict) -> str:
    command = str(payload.get("command") or "")
    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    if isinstance(tool_input, dict):
        command = command or str(
            tool_input.get("command") or tool_input.get("cmd") or ""
        )
    return command


def is_cursor_payload(payload: object) -> bool:
    """Cursor permission hooks have no PreToolUse event name."""
    if not isinstance(payload, dict):
        return False
    event = str(payload.get("hook_event_name") or payload.get("hookEventName") or "")
    return not event


def is_git_write_action(payload: object) -> bool:
    """Return whether a hook payload represents a Git commit or push."""
    if not isinstance(payload, dict):
        return False
    command = _command_text(payload)
    tool_name = _tool_name(payload)
    return bool(
        _SHELL_GIT_ACTION.search(command) or _MCP_GIT_ACTION.search(tool_name)
    )


def response_for(payload: object) -> dict:
    """Build stdout JSON for Cursor permission hooks or PreToolUse hooks."""
    remind = is_git_write_action(payload)
    if is_cursor_payload(payload):
        body: dict[str, str] = {"permission": "allow"}
        if remind:
            body["agent_message"] = _REMINDER
        return body
    body = {"continue": True}
    if remind:
        body["systemMessage"] = _REMINDER
    return body


def main() -> int:
    """Read one hook payload and always permit the action."""
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}

    sys.stdout.write(json.dumps(response_for(payload), ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
