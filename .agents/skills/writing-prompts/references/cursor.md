# Cursor mechanics for prompts

Read this file when the target is Cursor Agent / Plan / Superpowers. Do not copy it wholesale into the prompt.

## Modes

Do not confuse **Cursor Plan Mode** (UI) with a Superpowers plan file on disk.

- **Ask**: chat only, no edits. A prompt that says "create a skill/docs" is not executable in Ask.
- **Plan** (`Shift+Tab`): research plus a reviewable UI plan before code. Default plan location is not an arbitrary workspace path. Do not use Plan when Handoff needs those paths.
- **Agent**: writes and edits files. Required for research artifacts, plan files on disk, and code/docs edits.
- Switching mode drops context. A new logical chunk is a new chat.

| Need in the prompt | Mode |
|--------------------|------|
| Text answer, no files | Ask |
| Cursor UI plan only, no disk Handoff | Plan |
| Any Handoff paths / research / Superpowers plan file | **Agent** (never Plan) |

## Skills and Custom Mode

- `/skill-name` applies to one message. A playbook for the whole session is Custom Mode.
- `/subagent-driven-development` is a Superpowers skill. Do not start it without a plan file.
- `/goal` is a long-running goal, not a plan substitute.

## Context

- `@file` / `@folder` only when the path is known.
- Past chats: `@Chats` plus name, not a pasted transcript.
- A subagent starts with empty context. The parent puts facts in a brief file.

## Superpowers order

1. No spec — brainstorming.
2. Spec, no plan — writing-plans (**Agent Mode**).
3. Plan with independent tasks — subagent-driven development in the same session, or executing-plans in another.

## Grok dispatch

Resolve `model` from the Task allowlist of **this** session. Do not reuse a slug from memory.

1. Candidates: slugs matching `cursor-grok-`. Drop `composer-*`, `inherit`, `gpt-*`.
2. Fast only: slug ends with `-fast`.
3. Effort at least high. Known order: `high` < `xhigh`. Reject `low` and `medium`.
4. Rank: higher Grok version first, then higher effort.
5. Always pass `model` explicitly.
6. Floor: `cursor-grok-4.6-high-fast`. If the allowlist has no candidate at or above this floor, stop and tell the user.

Composer and Grok are one first-party family. Do not require different families for review vs fix.

Use the same resolver for implementer, fixer, and reviewer.

## When the original prompt is broken

| Symptom | Put in the improved prompt |
|---------|----------------------------|
| "improve docs" / "any queries" / "any dashboards" | Finite list of scenarios and artifacts; otherwise ask |
| Execution immediately | Phase 0: plan; execution only after approval |
| Research-to-files "in Plan Mode" | **Agent Mode** |
| "subagent, analyze this chat" | `@Chats` name/id or an insights file before implementer |
| Several implementers in parallel | Sequential file edits; explore/review may be parallel |
