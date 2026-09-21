from __future__ import annotations

from pathlib import Path

from agent_families import FAMILY_IDS, PROFILE_NAME, SKILL_NAME


def test_skill_frontmatter(skill_root: Path) -> None:
    text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert f"name: {SKILL_NAME}" in text
    assert PROFILE_NAME in text
    assert "Do **not** add bare `processName:node.exe`" in text
    assert "running.marker" in text
    assert "Devin Cloud" in text
    assert "ensure_autostart_flags.py" in text
    assert "remember_enable" in text


def test_readme_coverage_matrix(skill_root: Path) -> None:
    text = (skill_root / "README.md").read_text(encoding="utf-8")
    for token in ("Cursor", "Claude", "Codex", "Devin CLI", "Devin Desktop", "Devin Cloud"):
        assert token in text
    assert SKILL_NAME in text


def test_reference_profile_name(skill_root: Path) -> None:
    text = (skill_root / "reference.md").read_text(encoding="utf-8")
    assert "active_routing=Agents only" in text
    assert "Cursor only" not in text
    assert "process_name=node.exe" in text
    for token in (
        "language_server_windows_x64.exe",
        "windsurf",
        "Devin\\Devin",
        "cognition",
        "AnthropicClaude",
        ".codex",
    ):
        assert token in text


def test_family_catalog_complete() -> None:
    from agent_families import FAMILIES

    assert tuple(FAMILIES) == FAMILY_IDS
    for family_id, spec in FAMILIES.items():
        assert spec["process_names"]
        assert spec["path_regexes"]
        assert "node.exe" not in spec["process_names"]
