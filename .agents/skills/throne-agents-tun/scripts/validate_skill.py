"""Static checks for the throne-agents-tun skill tree. No Throne UI, no live DB."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_families import (
    LEGACY_SKILL_NAME,
    PROFILE_NAME,
    SKILL_NAME,
    compile_secret_patterns,
)

SECRET_PATTERNS = compile_secret_patterns()

ALLOWED_LEGACY_FILES = {
    "SKILL.md",
    "README.md",
    "docs/MIGRATION.md",
    "scripts/agent_families.py",
}


def iter_text_files(root: Path) -> list[Path]:
    skip_dirs = {".git", "__pycache__", ".pytest_cache"}
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in {
            ".md",
            ".py",
            ".ps1",
            ".cmd",
            ".yml",
            ".yaml",
            ".json",
            ".txt",
        }:
            files.append(path)
    return files


def check_frontmatter(skill_md: str) -> list[str]:
    errors = []
    if f"name: {SKILL_NAME}" not in skill_md:
        errors.append(f"SKILL.md frontmatter must set name: {SKILL_NAME}")
    if PROFILE_NAME not in skill_md:
        errors.append(f"SKILL.md must mention profile {PROFILE_NAME!r}")
    if "default outbound **direct**" not in skill_md and "default outbound **direct**" not in skill_md.replace(
        "**direct**", "direct"
    ):
        if "default outbound" not in skill_md.lower() and "default_outbound_id = -2" not in skill_md:
            errors.append("SKILL.md must state default outbound direct")
    return errors


def check_legacy_mentions(root: Path) -> list[str]:
    errors = []
    for path in iter_text_files(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        if LEGACY_SKILL_NAME in text and rel not in ALLOWED_LEGACY_FILES:
            if rel == "SKILL.md" and "Replaces" in text:
                continue
            if rel in {"README.md", "docs/MIGRATION.md"}:
                continue
            errors.append(
                f"{rel} mentions {LEGACY_SKILL_NAME}; keep that only in README/MIGRATION/frontmatter"
            )
    return errors


def check_secrets(root: Path) -> list[str]:
    errors = []
    for path in iter_text_files(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"{rel} matches secret/machine pattern {pattern.pattern}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=SKILL_ROOT)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    skill_md = (root / "SKILL.md").read_text(encoding="utf-8")
    errors = []
    errors.extend(check_frontmatter(skill_md))
    errors.extend(check_legacy_mentions(root))
    errors.extend(check_secrets(root))
    if "node.exe" in skill_md and "Do **not** add bare `processName:node.exe`" not in skill_md:
        if "bare `processName:node.exe`" not in skill_md and "bare processName:node.exe" not in skill_md:
            errors.append("SKILL.md must forbid bare processName:node.exe")
    if errors:
        print("FAIL")
        for item in errors:
            print(f"- {item}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
