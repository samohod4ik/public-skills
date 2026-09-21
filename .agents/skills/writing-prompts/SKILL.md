---
name: writing-prompts
description: >-
  Use when the user asks to improve, rewrite, or draft an agent prompt;
  when a request is vague ("improve docs", "any queries", "any dashboards");
  or when they mention prompt or handoff files.
---

# Writing prompts

Turn a weak or raw request into a prompt an agent can execute without guessing. This skill does not call tools or write project code — it returns prompt text.

If the target is Cursor, read [references/cursor.md](references/cursor.md).

## When to use

- Improve or write a prompt for an agent or a plan.
- The request has no file anchors, no done criterion, or says "any queries / any dashboards".
- The user mixes execution ("implement this") with research or "analyze this chat".

**Do not use** when the user needs a standing rule file rather than a one-shot prompt, or when the task is to execute a plan rather than improve the wording.

## Preflight

Before editing the prompt, check:

1. If Handoff/done require files in the workspace, the prompt must name a reader that can write those paths: the executing agent must be allowed to write the Handoff paths.
2. If the source asks for subagent-driven execution, a plan file with tasks must already exist.
3. Every `@file` / `@folder` in the future prompt exists. No file — do not invent a path; ask or drop the `@`.
4. Named past chats: exact name or id. "This chat" without an id is not a canon for a subagent.
5. Scope: if the source says "any queries / any dashboards / all docs", replace with a finite list of scenarios and artifacts from the canon. If that list cannot be derived, ask and do not emit an execution prompt. A research-then-plan prompt is still allowed.

If Preflight fails: emit the improved prompt, mark it not ready to execute, stop.

## Workflow

1. Read the source prompt. List gaps: goal, reader, canon, bounds, done, phase, handoff.
2. Read [references/cursor.md](references/cursor.md) only if the target is Cursor.
3. Fill the contract below. Exact values (ids, tables, commands) come from `@` files, not from memory.
4. Emit one paste-ready prompt from [assets/prompt-template.md](assets/prompt-template.md). Prompt text first, then 3-6 lines on how to run it.

## Output contract

The finished prompt contains these blocks, in this order:

1. **Goal** — one testable sentence.
2. **Reader** — who will execute (agent / human).
3. **Canon** — `@` files and folders, not "all documentation".
4. **Bounds** — what not to do (DML, other MCP, other repo).
5. **Done** — 3-5 checks the agent can confirm. Do not use "any / all / every" in done.
6. **Phase** — research-to-files / write-plan / execute-plan / research-then-plan.
7. **Handoff** — paths for brief/report; facts from chats as `@Chats` or a file, not "as discussed".

Form is a recipe. Do not replace a block with a list of "do not X".

## Fallback

- No project access: narrow the canon to paths the user named; mark the rest as gaps.
- No chat id: ask for the chat name or write insights to a file before subagents.
- User insists on execution without a plan: return a research-then-plan prompt, not an implementer prompt.
