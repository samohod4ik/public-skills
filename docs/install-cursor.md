# Install: Cursor

Cursor reads project skills from `.agents/skills/<name>/SKILL.md`. No copy step.

1. Clone this repository and open it as the workspace, or copy selected skill folders into the target project's `.agents/skills/`.
2. Project rules: `.cursor/rules/adaptive-code-review-gate.mdc` (YAML frontmatter required; a bare `.md` in `.cursor/rules` is ignored).
3. Hooks: `.cursor/hooks.json` calls `hooks/remind_before_git_write.py` on `beforeShellExecution` (matcher is the shell text) and `beforeMCPExecution` (matcher `git_commit|git_push`). See [hooks.md](hooks.md).

Do not commit a local `.cursor/skills/` copy; that path is gitignored.
