"""Emit a non-blocking reminder for git commit/push in an agent session."""

from __future__ import annotations

import argparse
import json
import re
import sys

FORMATS = ("cursor", "claude", "codex", "devin")

_SHELL_GIT_ACTION = re.compile(
    r"""(?:^|[;&|]\s*|\s)git(?:\.exe)?\s+
        (?:
            --no-pager\s+
            |-C\s+(?:"[^"]*"|'[^']*'|\S+)\s+
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


def parse_format(argv: list[str] | None = None) -> str | None:
    """Return --format if present. Unknown extra args from hook runners are ignored."""
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--format", choices=FORMATS, default=None)
    args, _unknown = parser.parse_known_args(argv)
    return args.format


def detect_format(payload: object) -> str:
    """Cursor if no event name. PreToolUse is not unique; fallback is Claude."""
    if is_cursor_payload(payload):
        return "cursor"
    return "claude"


def resolve_format(explicit: str | None, payload: object) -> str:
    if explicit in FORMATS:
        return explicit
    return detect_format(payload)


def cursor_response(remind: bool) -> dict:
    body: dict = {"permission": "allow"}
    if remind:
        body["agent_message"] = _REMINDER
    return body


def claude_response(remind: bool) -> dict:
    body: dict = {"continue": True}
    if remind:
        body["systemMessage"] = _REMINDER
    return body


def codex_response(remind: bool) -> dict:
    if remind:
        return {"systemMessage": _REMINDER}
    return {}


def devin_response(remind: bool) -> dict:
    if remind:
        return {"hookSpecificOutput": {"additionalContext": _REMINDER}}
    return {}


def response_for(payload: object, output_format: str | None = None) -> dict:
    """Build stdout JSON for the selected client contract."""
    remind = is_git_write_action(payload)
    fmt = resolve_format(output_format, payload)
    builders = {
        "cursor": cursor_response,
        "claude": claude_response,
        "codex": codex_response,
        "devin": devin_response,
    }
    return builders[fmt](remind)


def main(argv: list[str] | None = None) -> int:
    """Read one hook payload and always permit the action."""
    output_format = parse_format(argv)
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}

    sys.stdout.write(
        json.dumps(response_for(payload, output_format), ensure_ascii=True) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
