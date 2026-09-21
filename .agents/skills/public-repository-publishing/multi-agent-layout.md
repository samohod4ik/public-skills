# Multi-Agent Layout

Use one portable source and thin client adapters. Do not maintain several
committed copies of the same skill.

## Canonical tree

```text
.agents/skills/<skill-name>/SKILL.md
```

This is the committed canonical location for a shared public skill. Supporting
references, templates, scripts, and tests stay inside the skill directory.

Skill directory names describe the workflow, not a client. Client names are
valid inside compatibility references when behavior genuinely differs.

## Client behavior

| Client | Shared instructions | Project skill path | Adapter notes |
|--------|---------------------|--------------------|---------------|
| Cursor | `AGENTS.md`, `.cursor/rules/*.mdc` | `.agents/skills` | Project hooks in `.cursor/hooks.json` |
| Codex | `AGENTS.md` | `.agents/skills` | Project hooks in `.codex/hooks.json` |
| Hosted Devin | `AGENTS.md` | `.agents/skills` | CLI hooks use `.devin/hooks.v1.json` |
| Devin CLI | `AGENTS.md` | `.devin/skills` | Consumer copies or links locally |
| Claude Code | `CLAUDE.md`, `.claude/rules` | `.claude/skills` | Consumer copies or links locally |

When a client does not discover `.agents/skills`, document a consumer-side
copy or link. `.cursor/skills`, `.claude/skills`, and `.devin/skills` are
gitignored local consumer installs, not committed adapter trees. Gitignore
those compatibility trees so they cannot become a second committed source.

## Rules

- Keep portable workflow and safety constraints in `SKILL.md`.
- Keep client dispatch syntax, model selection, event names, and JSON stdout
  contracts in client-specific references or adapters.
- Keep `AGENTS.md` and `CLAUDE.md` short; point to canonical docs.
- Do not claim one client's path or hook contract works for another.
- Do not commit junctions, symlinks, generated copies, or local install trees.

## Hook portability

The same lifecycle intent may require different payload and response formats.
Treat each client as a separate contract:

- event name and matcher;
- stdin JSON shape;
- stdout JSON shape;
- blocking semantics;
- working directory and timeout;
- failure behavior when the interpreter is unavailable.

A shared hook script may expose an explicit client format switch. Test every
format independently. A response accepted by one client can be an error in
another.

## Repository documents

Recommended root, listing only tested adapters rather than whole client
directories:

```text
README.md
LICENSE
SECURITY.md
AGENTS.md
CLAUDE.md
.gitignore
.agents/skills/
.cursor/hooks.json
.claude/settings.json
.codex/hooks.json
.devin/hooks.v1.json
docs/
hooks/
tests/
```

Only include adapter files that the repository supports and tests. Empty
adapter directories add no compatibility. Do not commit `.cursor/skills`,
`.claude/skills`, or `.devin/skills`.
