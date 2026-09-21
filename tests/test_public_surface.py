#!/usr/bin/env python3
"""Static gates for the public skills catalog.

Run from repo root: python tests/test_public_surface.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HAPP = ROOT / ".agents" / "skills" / "happ-extra-whitelist2"
SKILLS = ROOT / ".agents" / "skills"

FORBIDDEN = [
    (re.compile(r"\bHermes\b", re.I), "host-specific Hermes"),
    (re.compile(r"Марьин"), "host-specific name"),
    (re.compile(r"\balexm\b", re.I), "host-specific username"),
    (re.compile(r"DESKTOP-[A-Z0-9]+", re.I), "host-specific computer name"),
    (re.compile(r"\brr77\b", re.I), "fleet identifier"),
    (re.compile(r"\bwezen\b", re.I), "fleet identifier"),
    (re.compile(r"APMuravev", re.I), "personal identifier"),
    (re.compile(r"uravev", re.I), "split personal identifier"),
    (re.compile(r"PycharmProjects", re.I), "machine path"),
    (re.compile(r"D:\\file", re.I), "machine path"),
    (re.compile(r"npv\\Throne", re.I), "machine path"),
    (re.compile(r"\breestr\b", re.I), "workplace hostname fragment"),
    (re.compile(r"\bmosregistr\b", re.I), "workplace hostname fragment"),
    (re.compile(r"\bkadastr\b", re.I), "workplace hostname fragment"),
    (re.compile(r"на машине автора", re.I), "author-machine framing"),
    (re.compile(r"живой SSH с машины автора", re.I), "author-machine framing"),
    (re.compile(r"on the author's machine", re.I), "author-machine framing"),
    (re.compile(r"live SSH", re.I), "author-machine framing"),
]

LAPTOP_ONLY = re.compile(
    r"(skill for Windows laptops|Windows laptops\b|clean Windows laptop|"
    r"Windows laptop with|on a Windows laptop)",
    re.I,
)

SECRETISH_URL = re.compile(
    r"https?://[^\s)>\"]*(token|uuid|hwid|subs\.db|/sub/)[^\s)>\"]*",
    re.I,
)

KILL_HAPP = re.compile(r"Stop-Process\s+.*Happ", re.I)
START_DISCONNECT = re.compile(r"Start-Process\s+['\"]happ://disconnect", re.I)
AGENT_IN_SKILL_DIR = re.compile(r"cursor|claude|codex|devin", re.I)

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".ps1",
    ".cmd",
    ".sh",
    ".yml",
    ".yaml",
    ".json",
    ".txt",
    ".template",
    ".mdc",
}


def iter_public_text() -> list[Path]:
    paths: list[Path] = []
    paths.extend(ROOT.glob("*.md"))
    paths.extend(ROOT.glob("docs/**/*.md"))
    paths.extend(ROOT.glob("hooks/**/*.py"))
    paths.extend(p for p in ROOT.glob(".cursor/rules/*.mdc") if p.is_file())
    paths.extend(p for p in ROOT.glob(".claude/rules/*") if p.is_file())
    if SKILLS.is_dir():
        for path in SKILLS.rglob("*"):
            if not path.is_file():
                continue
            if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
                continue
            if path.suffix.lower() in TEXT_SUFFIXES:
                paths.append(path)
    return paths


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def fail(msg: str) -> None:
    print(f"FAIL {msg}")
    raise SystemExit(1)


def main() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "SECURITY.md",
        ROOT / "AGENTS.md",
        ROOT / "CLAUDE.md",
        ROOT / "hooks" / "remind_before_git_write.py",
        ROOT / "docs" / "hooks.md",
        ROOT / "docs" / "install-cursor.md",
        ROOT / "docs" / "install-claude.md",
        ROOT / "docs" / "install-codex.md",
        ROOT / "docs" / "install-devin.md",
        HAPP / "SKILL.md",
        HAPP / "docs" / "happ-throne-mutex.md",
        HAPP / "docs" / "autoconnect.md",
        HAPP / "docs" / "install-pipeline.md",
        HAPP / "scripts" / "Set-HappAutoconnect.ps1",
        HAPP / "scripts" / "Invoke-HappSoftConnect.ps1",
        HAPP / "scripts" / "Install-HappAutostart.ps1",
        HAPP / "scripts" / "Invoke-HappSoftOpen.ps1",
        HAPP / "scripts" / "Verify-HappExtraWhitelist2.ps1",
        SKILLS / "adaptive-code-review-loop" / "SKILL.md",
        SKILLS / "writing-prompts" / "SKILL.md",
        SKILLS / "throne-agents-tun" / "SKILL.md",
        SKILLS / "throne-agents-tun" / "docs" / "http-proxy-fallback.md",
        SKILLS / "ralph-loop" / "SKILL.md",
        ROOT / ".cursor" / "rules" / "adaptive-code-review-gate.mdc",
        ROOT / ".claude" / "rules" / "review-gate.md",
    ]
    for p in required:
        if not p.is_file():
            fail(f"missing required file: {p.relative_to(ROOT)}")

    removed = [
        ROOT / "docs" / "variant-throne-cursor-only.md",
        ROOT / "skills" / "throne-cursor-only-public" / "SKILL.md",
        SKILLS / "throne-cursor-only-public" / "SKILL.md",
        ROOT / "scripts" / "Verify-HappExtraWhitelist2.ps1",
        SKILLS / "throne-agents-tun" / "docs" / "cursor-http-proxy.md",
    ]
    for p in removed:
        if p.exists():
            fail(f"must not publish: {p.relative_to(ROOT)}")

    if not SKILLS.is_dir():
        fail("missing .agents/skills")
    for skill_dir in SKILLS.iterdir():
        if skill_dir.is_dir() and AGENT_IN_SKILL_DIR.search(skill_dir.name):
            fail(f"skill folder name is agent-tied: {skill_dir.name}")

    for p in iter_public_text():
        text = read(p)
        rel = p.relative_to(ROOT)
        for rx, label in FORBIDDEN:
            if rx.search(text):
                fail(f"{rel}: forbidden {label}")
        if LAPTOP_ONLY.search(text):
            fail(f"{rel}: laptop-only framing (say Windows / Windows PC)")
        if SECRETISH_URL.search(text):
            fail(f"{rel}: looks like a subscription/secret URL")
        if p.suffix.lower() == ".ps1":
            if KILL_HAPP.search(text):
                fail(f"{rel}: kills Happ")
            if START_DISCONNECT.search(text):
                fail(f"{rel}: starts happ://disconnect")

    skill = read(HAPP / "SKILL.md")
    pipeline = read(HAPP / "docs" / "install-pipeline.md")
    autoconnect_doc = read(HAPP / "docs" / "autoconnect.md")
    security = read(ROOT / "SECURITY.md")
    extra = read(HAPP / "docs" / "extra-whitelist2.md")
    routing = read(HAPP / "docs" / "routing.md")
    set_ac = read(HAPP / "scripts" / "Set-HappAutoconnect.ps1")
    soft_c = read(HAPP / "scripts" / "Invoke-HappSoftConnect.ps1")
    install = read(HAPP / "scripts" / "Install-HappAutostart.ps1")
    verify = read(HAPP / "scripts" / "Verify-HappExtraWhitelist2.ps1")
    mutex = read(HAPP / "docs" / "happ-throne-mutex.md")
    catalog = read(ROOT / "README.md")
    claude_md = read(ROOT / "CLAUDE.md")
    install_claude = read(ROOT / "docs" / "install-claude.md")
    install_devin = read(ROOT / "docs" / "install-devin.md")
    hooks_doc = read(ROOT / "docs" / "hooks.md")
    review_skill = read(SKILLS / "adaptive-code-review-loop" / "SKILL.md")
    review_prompt = read(SKILLS / "adaptive-code-review-loop" / "code-reviewer.md")

    for label, text in (
        ("happ SKILL.md", skill),
        ("install-pipeline.md", pipeline),
        ("autoconnect.md", autoconnect_doc),
    ):
        for needle in (
            "autostart",
            "autoconnect",
            "lastused",
            "happ://connect",
            "Extra Whitelist2",
        ):
            if needle.lower() not in text.lower():
                fail(f"{label}: missing {needle}")

    if not re.search(r"never (kill|Stop-Process)|do not kill|не убивать", skill, re.I):
        fail("happ SKILL.md: missing hard rule to never kill Happ")
    if "Watch" not in skill and "watch" not in skill:
        fail("happ SKILL.md: missing Watch guidance")
    if "WHITELIST2" not in routing or "Do not invent" not in routing:
        fail("routing.md: must warn not to invent WHITELIST2 routing")
    if (
        "when those" not in extra.lower()
        and "if those" not in extra.lower()
        and "if present" not in extra.lower()
    ):
        fail("extra-whitelist2.md: must treat DE/NL Extra Whitelist2 as preference-when-present")
    if "subscription URL" not in security.lower() and "subscription URLs" not in security:
        fail("SECURITY.md: must forbid subscription URLs")

    if "happ://connect" not in set_ac or "happ://connect" not in soft_c:
        fail("connect scripts must invoke happ://connect")
    if "subscription-autoconnect" not in set_ac or "lastused" not in set_ac:
        fail("Set-HappAutoconnect.ps1 must document official lastused headers")
    if re.search(r"New-ItemProperty[\s\S]{0,200}[Aa]uto[Cc]onnect", set_ac):
        fail("Set-HappAutoconnect.ps1 must not invent autoconnect registry values")
    if "Set-HappAutoconnect.ps1" not in install:
        fail("Install-HappAutostart.ps1 should wire the autoconnect nudge")
    if "Autoconnect" not in verify and "autoconnect" not in verify:
        fail("Verify-HappExtraWhitelist2.ps1 must check the autoconnect nudge")
    if "SkipAutoconnectCheck" not in verify:
        fail("Verify-HappExtraWhitelist2.ps1 must allow -SkipAutoconnectCheck")
    if "Get-Process Happ" not in set_ac:
        fail("Set-HappAutoconnect.ps1 must wait for Happ.exe before happ://connect")

    if "happ-extra-whitelist2" not in catalog or "throne-agents-tun" not in catalog:
        fail("README.md must list happ-extra-whitelist2 and throne-agents-tun")
    if "Throne Cursor-only" in catalog:
        fail("README.md must not keep the old Throne Cursor-only variant name")
    if "System Proxy" not in mutex:
        fail("happ-throne-mutex.md must contrast System Proxy ownership")
    if "throne-agents-tun" not in mutex:
        fail("happ-throne-mutex.md must point at throne-agents-tun")
    if "Agents only" not in mutex:
        fail("happ-throne-mutex.md must name Agents only")
    if not re.search(r"Never.*System Proxy|не включать System Proxy", skill, re.I):
        fail("happ SKILL.md must forbid dual Happ+Throne System Proxy")
    ru = skill.split("Русский", 1)[-1]
    if "Watch" not in ru:
        fail("happ SKILL.md RU section must include Watch")
    if "local" not in autoconnect_doc.lower() or "official" not in autoconnect_doc.lower():
        fail("autoconnect.md must separate official headers from local happ://connect")

    if "## Apply on a live Windows session" not in autoconnect_doc:
        fail("autoconnect.md: missing live-session apply section")
    if "## Field check" not in autoconnect_doc:
        fail("autoconnect.md: missing Field check section")
    if "field-check" not in autoconnect_doc.lower() and "after a reboot" not in autoconnect_doc.lower():
        fail("autoconnect.md: missing field-check / after reboot logon nudge")
    if not re.search(r"do\s+(\*\*)?not(\*\*)?\s+fire", autoconnect_doc, re.I):
        fail("autoconnect.md: must say do not fire happ://connect on a healthy live tunnel")
    if "ProxyEnable" not in autoconnect_doc:
        fail("autoconnect.md: must mention ProxyEnable as the live System Proxy example")
    if "Happ Proxy Autoconnect Nudge" not in autoconnect_doc:
        fail("autoconnect.md: must name the delayed logon nudge task")
    if "WinDivert" not in autoconnect_doc:
        fail("autoconnect.md: must note competing WinDivert/TUN hijacks as a generic pitfall")

    if "live session" not in set_ac.lower() or "ProxyEnable" not in set_ac:
        fail("Set-HappAutoconnect.ps1 must document live-session soft-apply (ProxyEnable)")
    if "do not fire" not in set_ac.lower() and "skip immediate" not in set_ac.lower():
        fail("Set-HappAutoconnect.ps1 must say not to fire immediate happ://connect on a healthy tunnel")

    if "optional" not in soft_c.lower():
        fail("Invoke-HappSoftConnect.ps1 must warn that connect is optional when the tunnel is already healthy")
    if "already healthy" not in soft_c.lower() and "already up" not in soft_c.lower():
        fail("Invoke-HappSoftConnect.ps1 must warn when the tunnel already looks up")
    if "-Force" not in soft_c:
        fail("Invoke-HappSoftConnect.ps1 must offer -Force when the operator knows the tunnel is down")

    if "live session" not in skill.lower():
        fail("happ SKILL.md: missing live-session apply pointer")
    if "field-check" not in skill.lower() and "already tunneled" not in skill.lower():
        fail("happ SKILL.md: missing live-session vs reboot field-check pointer")

    if "install-claude.md" not in claude_md:
        fail("CLAUDE.md must point at docs/install-claude.md")
    if re.search(r"auto[- ]?loads?\s+`.agents/skills`|\.agents/skills`\s+is auto-loaded", claude_md, re.I):
        fail("CLAUDE.md must not claim Claude auto-loads .agents/skills")
    if "does not load" not in claude_md.lower() or ".agents/skills" not in claude_md:
        fail("CLAUDE.md must say Claude Code does not load .agents/skills")
    if ".claude/skills" not in claude_md:
        fail("CLAUDE.md must name .claude/skills as the Claude load path")
    if "copy" not in claude_md.lower() and "link" not in claude_md.lower():
        fail("CLAUDE.md must say to copy or link skills to .claude/skills")
    if "does not load" not in install_claude.lower() and "only at `.claude/skills" not in install_claude.lower():
        fail("install-claude.md must say Claude Code does not load .agents/skills")
    if "hosted Devin" not in install_devin and "Hosted Devin" not in install_devin:
        fail("install-devin.md must mention hosted Devin")
    if "copy" not in install_devin.lower():
        fail("install-devin.md must describe CLI copy-or-link")
    if "tool_name" not in hooks_doc:
        fail("docs/hooks.md must state Devin matcher is tool_name")
    if "non-blocking" not in hooks_doc.lower() and "always allow" not in hooks_doc.lower():
        fail("docs/hooks.md must state the reminder is non-blocking")

    if "cursor-grok" in review_skill.lower() and "fast" in review_skill.lower():
        fail("public adaptive-code-review-loop SKILL.md must not require Grok Fast")
    if "Task tool" in review_prompt:
        fail("code-reviewer.md must not require Cursor Task tool")

    gitignore = read(ROOT / ".gitignore")
    for needle in (".claude/skills/", ".devin/skills/", ".cursor/skills/"):
        if needle not in gitignore:
            fail(f".gitignore must ignore {needle}")

    print("PASS public surface gates")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        if e.code not in (0, 1):
            raise
        sys.exit(e.code)
