# Hooks

`hooks/remind_before_git_write.py` prints a non-blocking reminder when the inbound payload looks like `git commit` or `git push`, including shell commands with Git global `--no-pager`, `-C`, `--git-dir`, or `--work-tree` options before the action. The script always allows the action. Cursor still fail-closes the permission hook if `python` is missing from PATH or the process cwd is not the repository root (`.cursor/hooks.json` runs `python hooks/remind_before_git_write.py` from the repo root). It is an agent-session hook, not a git `pre-commit` or `pre-push` hook. It does not start `adaptive-code-review-loop`.

Trust the workspace before enabling project hooks. Audit `hooks/remind_before_git_write.py` and the JSON configs below. See [SECURITY.md](../SECURITY.md).

Configs call `python hooks/remind_before_git_write.py` (Cursor) or the same script with `--format {claude,codex,devin}`. They do not call `.cursor/hooks/docs_before_commit.py`.

`--format {cursor,claude,codex,devin}` selects the stdout JSON contract. Default is `cursor` when the payload has no `hook_event_name` / `hookEventName`. PreToolUse payloads are not unique per client, so Claude/Codex/Devin configs pass `--format` explicitly. If `--format` is omitted and an event name is set, the script uses the Claude contract (`continue`) as a fallback.

## Cursor

File: `.cursor/hooks.json`. Command: `python hooks/remind_before_git_write.py` (cursor format; `--format cursor` is optional).

- `beforeShellExecution`: matcher is the full shell-command text (`git` / `git.exe`).
- `beforeMCPExecution`: matcher is `git_commit|git_push` so only those git MCP tools spawn the script.

Stdout: `{"permission":"allow"}` plus optional `agent_message`. Invalid JSON blocks Cursor permission hooks. Do not emit `continue`.

## Codex

File: `.codex/hooks.json`. Event `PreToolUse`. Handler type `command`. Command: `python hooks/remind_before_git_write.py --format codex`.

Stdout when reminding: `{"systemMessage":"..."}`. Otherwise `{}`. Do not emit `continue` (Codex can treat it as a failed hook) or Cursor `permission`.

## Claude Code

File: `.claude/settings.json`, `hooks` block, event `PreToolUse`. Matcher: `Bash|PowerShell` (Windows Claude uses PowerShell). A directory named `hooks/` is not loaded by itself. Command: `python hooks/remind_before_git_write.py --format claude`.

Stdout: `{"continue":true}` plus optional `systemMessage`. Do not emit Cursor `permission`.

## Devin CLI

File: `.devin/hooks.v1.json`. Event `PreToolUse`. Matcher is `tool_name` (`bash|shell|terminal|exec|git_commit|git_push`), not the git command string. Command: `python hooks/remind_before_git_write.py --format devin`. The script still inspects `command` / `tool_input` when present; if the payload has only a generic shell tool name and no command text, the reminder is skipped unless the tool name itself is `git_commit` or `git_push`.

Stdout when reminding: `{"hookSpecificOutput":{"additionalContext":"..."}}`. Otherwise `{}`. Do not emit `continue` or Cursor `permission`.

## Linux validation

The pilot was validated with Python 3.12.14 in an isolated virtual environment. From the repository root, install the direct test dependencies:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-quality.txt
```

`requirements-quality.txt` pins pytest 8.3.5, pytest-cov 6.2.1, and coverage 7.10.6; it does not lock transitive dependencies. Run the root checks explicitly:

```sh
python -m pytest -q tests/
python tests/test_public_surface.py
python tests/test_remind_before_git_write.py
```

`tests/test_public_surface.py` is a standalone static gate, so invoke it directly; pytest does not collect it.

## Pull request validation

GitHub Actions runs the full `tests/` suite, the standalone public-surface and reminder checks, and the scoped Code Quality report for pull requests. The Code Quality command uses `--no-deps`, excluding dependency-cruiser cycle and knip dead-code scans from this pilot; other optional scanner skips remain visible in the uploaded report. The workflow uploads JUnit and quality reports as run artifacts; branch-protection settings determine whether its result is required to merge.
