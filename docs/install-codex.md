# Install: Codex

Codex reads `AGENTS.md` (keep it short; the chained budget is about 32 KiB) and skills at `.agents/skills/<name>/SKILL.md`. No copy step.

1. Clone this repository or copy selected skill folders into the target project's `.agents/skills/`.
2. Review-gate text is the paragraph in `AGENTS.md`, not a fourth copy of the loop protocol.
3. Hooks: `.codex/hooks.json`, event `PreToolUse`, handler `command`, script `hooks/remind_before_git_write.py`. See [hooks.md](hooks.md).
