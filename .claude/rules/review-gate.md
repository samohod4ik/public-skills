# Adaptive review gate

After code-changing work, start `adaptive-code-review-loop` when the change is security, auth, migrations, data mutation, concurrency, public API, or deployment.

Otherwise score +1 for each: more than three production files; more than 150 non-generated diff lines; several modules; a new dependency or config; substantial edge cases; multi-layer tests. Threshold 3.

Skip the automatic loop for read-only answers, docs-only edits, or an explicit skip. Explicit `/adaptive-code-review-loop` always runs.

Do not fix a round that contains only Minor findings. Do not attach the loop to an always-on hook.

Protocol: `.agents/skills/adaptive-code-review-loop/SKILL.md`. Claude Code must load that skill via `.claude/skills` — see `docs/install-claude.md`.
