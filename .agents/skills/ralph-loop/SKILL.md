---
name: ralph-loop
description: >-
  Bootstrap and run a Ralph Loop — Geoffrey Huntley's technique for autonomous,
  iterative agent work: one task per iteration, fresh agent context each run, all
  state on disk, hard human-confirmed safety gates for irreversible/high-risk steps.
  Use when the user wants to automate a multi-step task (install, configure, build,
  migrate) end-to-end with an agent, especially when the task touches real systems,
  secrets, or external installers and needs an audit trail. Triggers: "ralph loop",
  "loop engineering", "run this in a loop", "autonomous multi-step task", "agent loop".
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
homepage: https://ghuntley.com/ralph/
---

# Ralph Loop

Harness for running an AI agent in a loop to complete a multi-step task
(installs, config, migrations, ops runbooks) with a forced human gate before
irreversible steps.

This skill packages the technique (`references/`), templates (`templates/`),
and runner scripts (`scripts/`) for Windows/PowerShell and POSIX shells.

`scripts/loop.sh` and `scripts/loop.ps1` are **Cursor CLI adapters** (`agent -p`).
Other CLIs: change the executor function; keep `EXECUTOR` overridable.

## The technique

Coined by Geoffrey Huntley ("Ralph Wiggum as a software engineer", see
`references/ralph-technique.md`). Minimal form:

```bash
while true; do
  agent -p --force --trust "$(cat PROMPT.md)"   # fresh process, fresh context
  git add -A && git commit -m "iteration"        # state lives on disk, not in the model
done
```

Every iteration: a **brand-new agent process** reads the **same fixed prompt**, reads
the current plan/progress from disk (never from its own memory of past iterations),
does **exactly one** unit of work, validates it observably, updates the plan/progress
files, commits, and exits. The loop restarts it immediately. No context survives
between iterations except what is written to disk.

## When to use this

Good fit:
- Multi-step setup/ops tasks with a clear, checkable end-state.
- Tasks where each step has an observable pass/fail signal (exit code, log line, API response).
- Tasks touching real credentials/external installers, where a human checkpoint is required.

Bad fit:
- One-shot trivial edits.
- Purely creative work with no "done" signal.
- Anything without a validation check per step.

## Quick start

```bash
# 1. Scaffold a new Ralph project from the templates in this skill
scripts/init-ralph-project.sh /path/to/my-project "Do X, then Y, then Z"
#   (Windows: scripts/init-ralph-project.ps1 C:\path\to\my-project "Do X, then Y, then Z")

# 2. Edit the generated IMPLEMENTATION_PLAN.md into concrete checkboxes,
#    and AGENTS.md with any task-specific safety rules (see references/security-checklist.md)

# 3. Run it
cd /path/to/my-project
./scripts/loop.sh              # POSIX
# or: .\scripts\loop.ps1        # Windows PowerShell
```

The loop stops and prints why when it hits `RALPH_STATUS: BLOCKED` or `RALPH_STATUS: DONE`.
It never loops forever on a failing step (`MaxConsecutiveFailures`, default 3).

## Executor backends

The runner scripts call one configurable "executor" command per iteration — a CLI agent
that supports a non-interactive single-shot invocation with tool access.

- **Cursor CLI** (`agent -p --force --trust --model <model> "<prompt>"`) — the shipped adapter.
  Install: `irm 'https://cursor.com/install?win32=true' | iex` (Windows) or
  `curl https://cursor.com/install -fsS | bash` (macOS/Linux/WSL). Auth: `agent login`.

Any other CLI agent with a documented headless/print mode and tool access can be wired
the same way — see `scripts/loop.sh` for the single function to change.

## The core rules (see references/security-checklist.md)

1. **One task per iteration.** Never let a single iteration do more than one plan item.
2. **State lives on disk, not in the model.** `AGENTS.md` + `IMPLEMENTATION_PLAN.md` + `PROGRESS.md` are the only source of truth.
3. **Gate 0: verify before you trust.** Before real-world consequences, the agent gathers evidence. Only a human writes `HUMAN_CONFIRM`.
4. **Pin, don't trust "latest".** Re-download and re-hash any external artifact immediately before executing it.
5. **Secrets have one source of truth**, kept separate from anything a third-party installer might overwrite.
6. **Every step needs an observable check.** Never "looks like it worked."
7. **Fail loudly, not forever.** Cap consecutive failures; emit `RALPH_STATUS: BLOCKED: <reason + question>`.
8. **Watch for the executor accidentally becoming a full agent.** A smoke-test CLI run from the project directory can auto-load `AGENTS.md`. Use the flag that disables rule auto-injection for smoke tests.
9. **Git-commit every iteration.**
10. **Match model cost to step risk.** Strongest model for Gate 0; cheaper model for mechanical checklist items.

## Files in this skill

```
ralph-loop/
├── SKILL.md
├── references/
│   ├── ralph-technique.md
│   └── security-checklist.md
├── templates/
│   ├── AGENTS.md.template
│   ├── PROMPT.md.template
│   ├── IMPLEMENTATION_PLAN.md.template
│   └── PROGRESS.md.template
└── scripts/
    ├── loop.ps1                    # Cursor CLI adapter (Windows)
    ├── loop.sh                     # Cursor CLI adapter (POSIX)
    ├── init-ralph-project.ps1
    └── init-ralph-project.sh
```
