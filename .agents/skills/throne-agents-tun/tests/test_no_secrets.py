from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agent_families import compile_secret_patterns

SECRET_PATTERNS = compile_secret_patterns()


def test_validate_skill_script_ok(skill_root: Path) -> None:
    script = skill_root / "scripts" / "validate_skill.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--root", str(skill_root)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_tree_has_no_machine_secrets(skill_root: Path) -> None:
    skip = {".git", "__pycache__", ".pytest_cache"}
    for path in skill_root.rglob("*"):
        if any(part in skip for part in path.parts):
            continue
        if not path.is_file() or path.suffix.lower() not in {
            ".md",
            ".py",
            ".ps1",
            ".cmd",
            ".yml",
            ".yaml",
            ".json",
            ".txt",
        }:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            assert not pattern.search(text), f"{path} matched {pattern.pattern}"
