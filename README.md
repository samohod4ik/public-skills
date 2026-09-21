# public-skills

Agent-neutral skills for coding agents. Canonical tree: `.agents/skills/<name>/SKILL.md`.

This catalog does not install skills into `.claude/skills`, `.devin/skills`, or `.cursor/skills`. Those directories are gitignored. Follow the install doc for the client you use.

## Skills

| Skill | Use when |
|-------|----------|
| [adaptive-code-review-loop](.agents/skills/adaptive-code-review-loop/SKILL.md) | Review-fix loop after substantial work, with severity stop rules |
| [writing-prompts](.agents/skills/writing-prompts/SKILL.md) | Turn a weak request into a prompt an agent can execute |
| [public-repository-publishing](.agents/skills/public-repository-publishing/SKILL.md) | Preparing a sanitized public GitHub repository for first publication |
| [throne-agents-tun](.agents/skills/throne-agents-tun/SKILL.md) | Windows Throne TUN for local agent clients only |
| [ralph-loop](.agents/skills/ralph-loop/SKILL.md) | Fresh-context agent loop (Huntley) |
| [happ-extra-whitelist2](.agents/skills/happ-extra-whitelist2/SKILL.md) | Happ as the Windows full-OS proxy with WHITELIST routing |

Happ and Throne must not both own System Proxy / TUN. Chooser: [happ-throne-mutex.md](.agents/skills/happ-extra-whitelist2/docs/happ-throne-mutex.md).

## Client install

| Client | Doc |
|--------|-----|
| Cursor | [docs/install-cursor.md](docs/install-cursor.md) |
| Claude Code | [docs/install-claude.md](docs/install-claude.md) |
| Codex | [docs/install-codex.md](docs/install-codex.md) |
| Devin | [docs/install-devin.md](docs/install-devin.md) |

Hooks: [docs/hooks.md](docs/hooks.md). Audit committed hook scripts before enabling them. See [SECURITY.md](SECURITY.md).

## Tests

From the repository root:

```text
python tests/test_public_surface.py
python tests/test_remind_before_git_write.py
```

## License

MIT. See [LICENSE](LICENSE).
