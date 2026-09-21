# Ralph Loop security checklist

Standalone checklist — copy the relevant sections into a project's own `AGENTS.md` /
`IMPLEMENTATION_PLAN.md`, adjust to the specific task.

## Gate 0 — before touching anything with real-world consequences

Required whenever the task involves: running third-party/unverified code, installing
software from the internet, creating or using API keys/tokens, or granting an agent
network/system access it didn't already have.

- [ ] Read the actual source (README, install script, etc.) directly — don't rely on
      secondary documentation sites, especially ones with a domain that doesn't obviously
      belong to the claimed owner.
- [ ] Cross-check the claimed owner/publisher's *primary* site/socials directly for any
      mention of the thing you're about to install — silence there is a real signal.
- [ ] Read any script you're about to execute **in full**, before running it. Look
      specifically for: obfuscation/base64/encoded payloads, unexpected persistence
      (scheduled tasks, startup entries, registry Run keys) that isn't clearly explained
      by the feature you asked for, credential/clipboard access, network calls to domains
      you don't recognize.
- [ ] Look for independent third-party confirmation (press, community discussion) that
      isn't just other pages on the same suspect domain citing each other in a loop.
- [ ] Write a plain verdict (LEGIT / NOT-LEGIT / UNCLEAR) with the evidence for it.
- [ ] **Do not write the line that authorizes proceeding yourself.** That's a human-only
      action — a specific, named line (e.g. `HUMAN_CONFIRM: <date> <who>`) that the loop
      mechanically checks for before unlocking the next phase. Stop and ask instead.

## Pinning and re-verification

- [ ] Never execute directly against a mutable ref (a branch like `main`/`master`, a
      "latest" URL). Pin to an immutable tag or commit SHA.
- [ ] Hash-check the artifact immediately before executing it — not just once during the
      audit, but again right before the actual run. If the hash changed, stop; that
      specific hash needs its own fresh confirmation, even if the artifact "looks the
      same" in every other way.
- [ ] Scope any human confirmation to the specific hash/version it was given for. A
      confirmation given for one artifact does not carry over to a different one, even at
      the exact same URL.

## Secrets

- [ ] Identify, explicitly and in writing, which file is the *real* target config for
      whatever you're installing/configuring — separately from wherever the harness
      itself stages user-provided secrets.
- [ ] Assume installers/setup wizards may recreate their own config file from a template
      at install/update time, discarding anything written there beforehand. Don't assume
      a value you set once will still be there after a later install/update step —
      re-verify.
- [ ] Never put a secret only in chat/conversation text as the final resting place — get
      it into the actual secrets file, then treat the chat-pasted copy as already
      partially exposed (recommend rotation, don't panic-block on it).
- [ ] One value per line in `.env`-style files; never an inline `# comment` after a real
      value on the same line — trailing-comment handling is inconsistent across parsers.
- [ ] Don't rely solely on grep/search tooling to confirm a secret is absent — some
      coding-agent search tools deliberately don't index dotfiles/`.env`. Read the
      specific file directly by path when checking for a secret's presence.
- [ ] Mask secrets in every log/commit/status line (`sk-XXXX...YYYY`), never print them
      in full anywhere the human or a stored transcript will see.

## Executor hardening (protect against the executor itself over-reaching)

- [ ] Know whether your executor CLI auto-discovers and loads directory-local
      instructions/rules files into a session's context. If it does, use whichever flag
      disables that for any invocation that isn't supposed to carry full agency
      (smoke tests, one-off queries).
- [ ] Put a real, code-level write-scope restriction in place (not just a command-
      approval prompt) before running the executor from inside any directory that itself
      contains agent-rules/instructions — approval-gates and write-scope sandboxing are
      different layers; a command-approval allowlist typically does **not** cover file
      write/patch/delete tool calls.
- [ ] Set approvals to manual (not auto-approve-everything) by default while you don't
      yet fully trust the specific setup.
- [ ] For anything granting remote/messaging access (chat platforms, webhooks): read the
      actual authorization code path, not just the docs — allow-lists sometimes apply
      more broadly than the obvious reading of the config option's name suggests (e.g.
      "allowed users" applying to group chats, not just DMs). Verify the fix by exercising
      the real code with realistic before/after inputs.
- [ ] Default any new remote-access surface to the narrowest scope (DM-only, not groups;
      one allow-listed identity, not a wildcard) and widen deliberately later if needed.
- [ ] Write down, in the harness's rules file, the actual emergency-revocation steps
      (how to pause without revoking, how to revoke one user, how to fully revoke a
      token) *before* you need them, not after.

## Process discipline

- [ ] One task per iteration. No exceptions for "it's a quick one too."
- [ ] Every step ends with an observable, checkable result — a command's exit code, a
      specific log line, a live round-trip to a real API — never "should be fine."
- [ ] Cap consecutive failures on the same step (e.g. 3) and stop with a clear question
      rather than retry-looping silently.
- [ ] Commit after every iteration, even trivial ones — the audit trail is the point.
- [ ] Match model cost to step risk: strongest/most careful model for irreversible or
      judgment-heavy steps, a cheaper/faster model for the mechanical majority.
