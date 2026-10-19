# Cursor dispatch (optional)

Use this file only when the parent session is Cursor and Task tool is available. The portable protocol in `SKILL.md` and `code-reviewer.md` does not require it.

## Models

Prefer one Grok Fast (effort at least high) slug from the Task allowlist of **this** session. Use it for both reviewer and fixer, and pass `model` explicitly.

If the allowlist has no `cursor-grok-*-fast` candidate at that floor, fall back to the session's default model (omit `model` so the session inherits) and say so in the report — never label the review as a fast-model run. If the Task tool requires an explicit allowlist slug and none is usable, stop and tell the user. Do not silently substitute another family; any non-Grok-Fast choice must be disclosed.

## Dispatch

1. Reviewer: `subagent_type: generalPurpose`, `description: "Review code changes"`, `model:` the resolved slug, prompt from `code-reviewer.md`.
2. Fixer (mixed-severity rounds only): one serialized `generalPurpose` session, same `model`.
3. Do not publish a reviewer/fixer slug from one repository as a requirement inside this skill.
