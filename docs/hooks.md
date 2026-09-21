# Hooks

`hooks/remind_before_git_write.py` prints a non-blocking reminder when the inbound payload looks like `git commit` or `git push`. It always allows the action. It is an agent-session hook, not a git `pre-commit` or `pre-push` hook. It does not start `adaptive-code-review-loop`.

Trust the workspace before enabling project hooks. Audit `hooks/remind_before_git_write.py` and the JSON configs below. See [SECURITY.md](../SECURITY.md).

Configs call `python hooks/remind_before_git_write.py` (or a thin wrapper). They do not call `.cursor/hooks/docs_before_commit.py`.

The script detects Cursor permission payloads versus PreToolUse payloads and emits the matching stdout JSON.

## Cursor

File: `.cursor/hooks.json`.

- `beforeShellExecution`: matcher is the full shell-command text (`git` / `git.exe`).
- `beforeMCPExecution`: same script, so git MCP tools (`git_commit`, `git_push`) are covered.

Stdout: `{"permission":"allow"}` plus optional `agent_message`. Invalid JSON blocks Cursor permission hooks.

## Codex

File: `.codex/hooks.json`. Event `PreToolUse`. Handler type `command`.

## Claude Code

File: `.claude/settings.json`, `hooks` block, event `PreToolUse`. A directory named `hooks/` is not loaded by itself.

## Devin CLI

File: `.devin/hooks.v1.json`. Event `PreToolUse`. Matcher is `tool_name`, not the git command string. The script still inspects `command` / `tool_input` when present; if the payload has only a generic shell tool name and no command text, the reminder is skipped unless the tool name itself is `git_commit` or `git_push`.
