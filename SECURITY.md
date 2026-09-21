# Security

- Do not commit subscription URLs, tokens, private keys, HWID dumps, or database extracts.
- Do not commit host names, user profile paths, or machine identifiers.
- Happ scripts must not print full subscription URLs.
- Prefer `happ://open` / `happ://connect` over `happ://disconnect` or process kill when a remote session depends on the tunnel.
- Do not enable Happ System Proxy and Throne System Proxy at the same time.

## Hooks

Committed files under `hooks/`, `.cursor/hooks.json`, `.codex/hooks.json`, `.devin/hooks.v1.json`, and `.claude/settings.json` run in an agent session only after the workspace is trusted. They are not git `pre-commit` / `pre-push` hooks.

The reminder hook in this repository is non-blocking: it never denies `git commit` or `git push`. Review the script before use. Do not enable hooks from an untrusted clone.
