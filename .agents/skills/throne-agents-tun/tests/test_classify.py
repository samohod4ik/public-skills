from __future__ import annotations

from agent_families import classify_agent_path, should_emit_process_name


def test_cursor_and_agent_node() -> None:
    assert classify_agent_path("Cursor.exe", r"C:\Users\fixture\AppData\Local\Programs\cursor\Cursor.exe") == "cursor"
    assert (
        classify_agent_path(
            "cursor.exe",
            r"C:\Users\fixture\AppData\Local\Programs\cursor\cursor.exe",
        )
        == "cursor"
    )
    assert (
        classify_agent_path(
            "node.exe",
            r"C:\Users\fixture\AppData\Local\cursor-agent\versions\1.0\node.exe",
        )
        == "cursor"
    )
    assert classify_agent_path("node.exe", r"C:\Program Files\nodejs\node.exe") is None
    assert (
        classify_agent_path(
            "node.exe",
            r"C:\Users\fixture\AppData\Local\cursor-agent\versions\node.exe",
        )
        is None
    )
    assert not should_emit_process_name("node.exe")


def test_chatgpt_only_under_codex() -> None:
    assert (
        classify_agent_path(
            "ChatGPT.exe",
            r"C:\Program Files\WindowsApps\OpenAI.Codex_1.0.0_x64__x\app\ChatGPT.exe",
        )
        == "codex"
    )
    assert classify_agent_path("ChatGPT.exe", r"C:\Program Files\ChatGPT\ChatGPT.exe") is None
    assert not should_emit_process_name("ChatGPT.exe")


def test_devin_desktop_cli_and_language_server() -> None:
    assert classify_agent_path("Devin.exe", r"C:\Users\fixture\Devin\Devin.exe") == "devin"
    assert (
        classify_agent_path(
            "devin.exe",
            r"C:\Users\fixture\Devin\resources\app\extensions\windsurf\devin\bin\devin.exe",
        )
        == "devin"
    )
    assert (
        classify_agent_path(
            "language_server_windows_x64.exe",
            r"C:\Users\fixture\Devin\resources\app\extensions\windsurf\bin\language_server_windows_x64.exe",
        )
        == "devin"
    )
    assert (
        classify_agent_path(
            "language_server_windows_x64.exe",
            r"C:\Program Files\SomeIDE\language_server_windows_x64.exe",
        )
        is None
    )
    assert not should_emit_process_name("language_server_windows_x64.exe")
    assert should_emit_process_name("Devin.exe")
