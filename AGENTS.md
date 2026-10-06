# Agent notes

Canonical skills: `.agents/skills/<name>/SKILL.md`. Cursor, Codex, and hosted Devin read that path. Claude Code does not; see [docs/install-claude.md](docs/install-claude.md). Devin CLI does not unless copied; see [docs/install-devin.md](docs/install-devin.md).

Rules in this repository advise. They do not block shell or git. The only executable reminder is `hooks/remind_before_git_write.py`, wired per client in [docs/hooks.md](docs/hooks.md). That reminder always allows the action.

## Review gate

After code-changing work, start `adaptive-code-review-loop` when the change is security, auth, migrations, data mutation, concurrency, public API, or deployment; or when a simple complexity score is 3 or higher (more than three production files, more than 150 non-generated diff lines, several modules, a new dependency or config, substantial edge cases, multi-layer tests). Skip the automatic loop for read-only answers, docs-only edits, or an explicit user skip. Explicit `/adaptive-code-review-loop` always runs; so does delegated invocation as a required stage of another process or skill.

Do not attach the review loop to an always-on hook. Do not fix a round that contains only Minor findings.

Protocol: [.agents/skills/adaptive-code-review-loop/SKILL.md](.agents/skills/adaptive-code-review-loop/SKILL.md).
