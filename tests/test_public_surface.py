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
PUBLIC_REPO_SKILL = SKILLS / "public-repository-publishing"
ADAPTER_JSON = (
    ROOT / ".cursor" / "hooks.json",
    ROOT / ".codex" / "hooks.json",
    ROOT / ".devin" / "hooks.v1.json",
    ROOT / ".claude" / "settings.json",
)

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
    (re.compile(r"author['’]s workstation", re.I), "author-machine framing"),
    (re.compile(r"live SSH", re.I), "author-machine framing"),
    (re.compile(r"software-development/throne-agents-tun"), "private monorepo path"),
    (re.compile(r"samohod4ik/skills"), "private catalog path"),
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
    paths.extend(ADAPTER_JSON)
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        key = path.resolve()
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


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
        PUBLIC_REPO_SKILL / "SKILL.md",
        PUBLIC_REPO_SKILL / "workflow.md",
        PUBLIC_REPO_SKILL / "anonymization.md",
        PUBLIC_REPO_SKILL / "multi-agent-layout.md",
        PUBLIC_REPO_SKILL / "review-and-release.md",
        PUBLIC_REPO_SKILL / "repository-checklist.md",
        ROOT / ".cursor" / "rules" / "adaptive-code-review-gate.mdc",
        ROOT / ".claude" / "rules" / "review-gate.md",
        *ADAPTER_JSON,
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
    if "public-repository-publishing" not in catalog:
        fail("README.md must list public-repository-publishing")
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
    if "Copy-Item" not in install_devin:
        fail("install-devin.md must include a Windows Copy-Item variant")
    if "tool_name" not in hooks_doc:
        fail("docs/hooks.md must state Devin matcher is tool_name")
    if "non-blocking" not in hooks_doc.lower() and "always allow" not in hooks_doc.lower():
        fail("docs/hooks.md must state the reminder is non-blocking")
    if "--format" not in hooks_doc:
        fail("docs/hooks.md must document --format stdout contracts")

    cursor_hooks = read(ROOT / ".cursor" / "hooks.json")
    claude_hooks = read(ROOT / ".claude" / "settings.json")
    codex_hooks = read(ROOT / ".codex" / "hooks.json")
    devin_hooks = read(ROOT / ".devin" / "hooks.v1.json")
    if "--format" in cursor_hooks:
        fail(".cursor/hooks.json must use default cursor format (no --format)")
    if "--format claude" not in claude_hooks:
        fail(".claude/settings.json must pass --format claude")
    if "Bash|PowerShell" not in claude_hooks:
        fail(".claude/settings.json matcher must include PowerShell")
    if "--format codex" not in codex_hooks:
        fail(".codex/hooks.json must pass --format codex")
    if "--format devin" not in devin_hooks:
        fail(".devin/hooks.v1.json must pass --format devin")
    if "|exec|" not in devin_hooks and not re.search(r"\bexec\b", devin_hooks):
        fail(".devin/hooks.v1.json matcher must include exec")

    writing_skill = read(SKILLS / "writing-prompts" / "SKILL.md")
    if "Superpowers" in writing_skill:
        fail("writing-prompts SKILL.md must not name Superpowers")
    if "research-to-files / write-plan / execute-plan / research-then-plan" not in writing_skill:
        fail("writing-prompts SKILL.md phase block must keep research-to-files / write-plan / execute-plan / research-then-plan")
    if "executing agent must be allowed to write the Handoff paths" not in writing_skill:
        fail("writing-prompts SKILL.md Preflight must require the executing agent to write Handoff paths")

    if "cursor-grok" in review_skill.lower() and "fast" in review_skill.lower():
        fail("public adaptive-code-review-loop SKILL.md must not require Grok Fast")
    if "Task tool" in review_prompt:
        fail("code-reviewer.md must not require Cursor Task tool")

    gitignore = read(ROOT / ".gitignore")
    for needle in (".claude/skills/", ".devin/skills/", ".cursor/skills/"):
        if needle not in gitignore:
            fail(f".gitignore must ignore {needle}")

    pub_skill = read(PUBLIC_REPO_SKILL / "SKILL.md")
    pub_release = read(PUBLIC_REPO_SKILL / "review-and-release.md")
    create_seen = {"SKILL.md": False, "review-and-release.md": False}
    exec_ext = {".py", ".ps1", ".sh", ".cmd", ".exe", ".bat"}
    skill_blob_parts: list[str] = []

    for label, text in (
        ("public-repository-publishing SKILL.md", pub_skill),
        ("public-repository-publishing review-and-release.md", pub_release),
    ):
        lower = text.lower()
        if "fresh" not in lower:
            fail(f"{label}: missing fresh target unless retain-history exception")
        if ".git" not in text:
            fail(f"{label}: missing source .git exclusion language")
        if "--local" not in text:
            fail(f"{label}: must require --local git identity")

    skill_lower = pub_skill.lower()
    if "delete" not in skill_lower:
        fail("public-repository-publishing SKILL.md: old-repository delete must be out of scope")
    if "out of scope" not in skill_lower and "does not" not in skill_lower:
        fail("public-repository-publishing SKILL.md: old-repository delete must be out of scope")

    for path in PUBLIC_REPO_SKILL.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in exec_ext:
            fail(
                "public-repository-publishing must not contain executable "
                f"{path.relative_to(ROOT)}"
            )
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        body = read(path)
        skill_blob_parts.append(body)
        if "git config --global" in body:
            fail(f"{path.relative_to(ROOT)}: must not set git identity with --global")
        if "gh repo delete" in body:
            fail(f"{path.relative_to(ROOT)}: gh repo delete is out of scope")
        for line in body.splitlines():
            cmd = line.strip().lstrip("`")
            if not cmd.startswith("gh repo create"):
                continue
            if path.name in create_seen:
                create_seen[path.name] = True
            if "--public" not in cmd:
                fail(f"{path.relative_to(ROOT)}: gh repo create must include --public")
            if "--description" not in cmd:
                fail(f"{path.relative_to(ROOT)}: gh repo create must include --description")
            if "--push" in cmd:
                fail(f"{path.relative_to(ROOT)}: gh repo create must not include --push")

    if not create_seen["SKILL.md"] or not create_seen["review-and-release.md"]:
        fail("SKILL.md and review-and-release.md must include gh repo create")

    skill_blob = "\n".join(skill_blob_parts)
    for needle, label in (
        ("source `.git`", "source .git exclusion"),
        ("git rev-list --objects --all", "object inventory"),
        ("git ls-tree -r", "full remote tree listing"),
        ("git remote -v", "pre-push remote inspect"),
        ("choose a new name", "collision stop"),
        ("Do not remove or rewrite origin", "origin no-remove/no-rewrite rule"),
    ):
        if needle not in skill_blob:
            fail(f"public-repository-publishing: missing {label} ({needle})")

    origin_rule = "Do not remove or rewrite origin"
    origin_gate_files = (
        PUBLIC_REPO_SKILL / "SKILL.md",
        PUBLIC_REPO_SKILL / "workflow.md",
        PUBLIC_REPO_SKILL / "anonymization.md",
        PUBLIC_REPO_SKILL / "review-and-release.md",
        PUBLIC_REPO_SKILL / "repository-checklist.md",
        ROOT / "docs" / "superpowers" / "specs" / "2026-09-21-public-repository-publishing-design.md",
        ROOT / "docs" / "superpowers" / "plans" / "2026-09-21-public-repository-publishing.md",
    )
    for path in origin_gate_files:
        if origin_rule not in read(path):
            fail(f"{path.relative_to(ROOT)}: missing origin no-remove/no-rewrite rule")

    linguistic_stop = "linguistic review still finds a checklist violation"
    if linguistic_stop not in pub_skill:
        fail("public-repository-publishing SKILL.md: missing linguistic checklist violation stop")
    if linguistic_stop not in pub_release:
        fail(
            "public-repository-publishing review-and-release.md: missing "
            "linguistic checklist violation stop"
        )

    print("PASS public surface gates")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        if e.code not in (0, 1):
            raise
        sys.exit(e.code)
