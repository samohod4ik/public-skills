# Prompt template

Fill the slots. Delete sections that do not apply. Do not leave "TBD".

```text
Goal: <one testable sentence>.

Reader: agent that <will write SQL / update docs / execute a plan>.
Canon is the files below, not this chat.

Canon:
@<path> @<path>

Bounds:
- <what is forbidden: DML without a snapshot / other MCP / other repo>
- <what not to build>
- Scenarios: <finite list, not "any">

Done:
1. <check the agent can confirm>
2. <check>
3. <check>

Phase: <research-to-files | write-plan | execute-plan <path> | research-then-plan below>

Handoff:
- Research/insights -> <path/to/artifact.md>
- Past chats: @Chats "<name>" (id <uuid>), not "this chat"
- Subagent brief <path>, not the whole plan and not the session history
```

## Research-then-plan (when execution is early)

If the source asks to execute and also "collect the schema / walk the docs / parse a chat":

```text
Now: write only research files and the plan at the Handoff paths; do not change canon or push.

Phase 0 — do not start execution.
Handoff: research files below -> plan <path> -> human approval -> new chat for execution.

Phase 1 — subagents write artifacts only (no canon edits, no commits):
1) Docs audit -> <path/docs-audit.md>
2) Live inventory -> <path/inventory.md> (only allowed data access)
3) Chat insights -> <path/chat-insights.md> from @Chats "<name>", not from "this" chat

The plan is ready when it has: Goal, Global Constraints, tasks with Files and a check.
Canon edits only after that plan is approved.
Scenarios the plan must cover: <finite list>.
```
