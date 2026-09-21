"""Catalog of local agent clients for Throne process-split TUN.

Paths here are match *shapes*, not a specific machine. Discovery resolves
live executables. Never match a bare node.exe.
"""

from __future__ import annotations

from pathlib import Path
import re

# Outbound IDs from Throne RouteRule.h
OUTBOUND_PROXY = -1
OUTBOUND_DIRECT = -2

PROFILE_NAME = "Agents only"
LEGACY_PROFILE_NAME = "Cursor only"
LEGACY_SKILL_NAME = "throne-cursor-only-public"
SKILL_NAME = "throne-agents-tun"

# Process-name tokens that are never allowed as a proxy matcher by themselves.
FORBIDDEN_PROCESS_NAMES = frozenset(
    {
        "node.exe",
        "Node.exe",
        "python.exe",
        "pwsh.exe",
        "powershell.exe",
        "cmd.exe",
        "bash.exe",
    }
)

# Match these only via OpenAI.Codex path/regex, never by process name alone.
PATH_ONLY_PROCESS_NAMES = frozenset({"ChatGPT.exe", "chatgpt.exe"})

# Family ids used in docs, discovery, and tests.
FAMILY_IDS = ("cursor", "claude", "codex", "devin")

# Process names that may appear as a leaf but must never go into process_name_json.
PATH_ONLY_LEAVES = frozenset(
    {name.lower() for name in PATH_ONLY_PROCESS_NAMES}
    | {"node.exe", "language_server_windows_x64.exe"}
)

SECRET_PATTERN_PARTS: tuple[tuple[str, ...], ...] = (
    (r"https?://[^\s]+/s/[A-Za-z0-9_\-]{12,}",),
    ("with", "blanc", "vpn"),
    (r"PrivateKey\s*=",),
    (r"BEGIN (OPENSSH|PRIVATE) KEY",),
)


def compile_secret_patterns():
    import re

    patterns = []
    for parts in SECRET_PATTERN_PARTS:
        flags = re.I if parts == ("with", "blanc", "vpn") else 0
        patterns.append(re.compile("".join(parts), flags))
    return tuple(patterns)


def classify_agent_path(name: str, path: str) -> str | None:
    """Map a live executable to a family. None means do not proxy."""
    if not path:
        return None
    leaf = Path(path).name
    if leaf.lower() == "node.exe":
        if is_cursor_agent_node_path(path):
            return "cursor"
        return None
    if leaf.lower() == "chatgpt.exe":
        if is_codex_chatgpt_path(path):
            return "codex"
        return None
    if leaf.lower() == "language_server_windows_x64.exe":
        if is_devin_language_server_path(path):
            return "devin"
        return None
    if leaf.lower() == "cursor.exe" or (name and name.lower() == "cursor.exe"):
        return "cursor"
    if leaf.lower() == "claude.exe":
        return "claude"
    if leaf.lower() in {"codex.exe"}:
        return "codex"
    if leaf.lower() == "devin.exe":
        return "devin"
    return None


def should_emit_process_name(leaf: str) -> bool:
    return leaf.lower() not in PATH_ONLY_LEAVES


_CURSOR_AGENT_NODE = re.compile(
    r"(?i)[\\/]cursor-agent[\\/]versions[\\/][^\\/]+[\\/]node\.exe$"
)


def is_cursor_agent_node_path(path: str) -> bool:
    return bool(path) and _CURSOR_AGENT_NODE.search(path) is not None


def is_codex_chatgpt_path(path: str) -> bool:
    return "openai.codex" in path.replace("/", "\\").lower()


def is_devin_language_server_path(path: str) -> bool:
    lowered = path.replace("/", "\\").lower()
    return (
        "\\extensions\\windsurf\\bin\\" in lowered
        and lowered.endswith("language_server_windows_x64.exe")
    )


def regex_allows_language_server(regex: str) -> bool:
    alnum = re.sub(r"[^a-z0-9]+", "", regex.lower())
    return "languageserverwindowsx64exe" in alnum and "extensionswindsurfbin" in alnum

# path_regexes are published (no machine hashes). path_globs are discovery hints.
FAMILIES = {
    "cursor": {
        "label": "Cursor IDE / cursor-agent",
        "process_names": ["Cursor.exe"],
        "path_globs": [
            r"*\Programs\cursor\Cursor.exe",
            r"*\cursor-agent\versions\*\node.exe",
        ],
        "path_regexes": [
            r"(?i)[\\/]cursor-agent[\\/]versions[\\/][^\\/]+[\\/]node\.exe$",
        ],
        "notes": "Chat/Agent often stays inside Cursor.exe; cursor-agent node is optional.",
    },
    "claude": {
        "label": "Claude Code CLI / Claude Desktop",
        "process_names": ["Claude.exe", "claude.exe"],
        "path_globs": [
            r"*\.local\bin\claude.exe",
            r"*\WindowsApps\Claude.exe",
            r"*\AnthropicClaude\*\Claude.exe",
            r"*\Programs\Claude\Claude.exe",
        ],
        "path_regexes": [
            r"(?i)[\\/]\.local[\\/]bin[\\/]claude\.exe$",
            r"(?i)[\\/](?:AnthropicClaude|Claude)[\\/].*[\\/]Claude\.exe$",
        ],
        "notes": "Desktop alias Claude.exe can shadow CLI; always keep the resolved CLI path.",
    },
    "codex": {
        "label": "Codex CLI / Codex App",
        "process_names": ["codex.exe", "Codex.exe"],
        "path_globs": [
            r"*\Programs\OpenAI\Codex\bin\codex.exe",
            r"*\OpenAI\Codex\bin\codex.exe",
            r"*\.codex\packages\standalone\*\bin\codex.exe",
            r"*\WindowsApps\OpenAI.Codex*\app\ChatGPT.exe",
            r"*\WindowsApps\OpenAI.Codex*\app\resources\codex.exe",
        ],
        "path_regexes": [
            r"(?i)[\\/](?:Programs\\)?OpenAI[\\/]Codex[\\/].*[\\/]codex\.exe$",
            r"(?i)[\\/]\.codex[\\/]packages[\\/]standalone[\\/].*[\\/]codex\.exe$",
            r"(?i)[\\/]WindowsApps[\\/]OpenAI\.Codex[^\\/]*[\\/]app[\\/](?:ChatGPT\.exe|resources[\\/]codex\.exe)$",
        ],
        "notes": (
            "Do not match every ChatGPT.exe. Codex App is ChatGPT.exe under "
            "WindowsApps\\OpenAI.Codex*; add that path/regex only after discovery."
        ),
    },
    "devin": {
        "label": "Devin CLI / Devin Desktop",
        "process_names": ["devin.exe", "Devin.exe"],
        "path_globs": [
            r"*\.local\bin\devin.exe",
            r"*\.local\share\cognition\cli\*\devin.exe",
            r"*\Devin\Devin.exe",
            r"*\extensions\windsurf\devin\bin\devin.exe",
            r"*\extensions\windsurf\bin\language_server_windows_x64.exe",
        ],
        "path_regexes": [
            r"(?i)[\\/]\.local[\\/]bin[\\/]devin\.exe$",
            r"(?i)[\\/]cognition[\\/]cli[\\/].*[\\/]devin\.exe$",
            r"(?i)[\\/]Devin[\\/]Devin\.exe$",
            r"(?i)[\\/]extensions[\\/]windsurf[\\/]devin[\\/]bin[\\/]devin\.exe$",
            r"(?i)[\\/]extensions[\\/]windsurf[\\/]bin[\\/]language_server_windows_x64\.exe$",
        ],
        "notes": (
            "Proxy Devin CLI and, when discovered, Devin Desktop plus the "
            "path-qualified Windsurf language server. Never match a bare "
            "language_server*.exe. Devin Cloud is not this profile."
        ),
    },
}
