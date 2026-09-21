---
name: adaptive-code-review-loop
description: >-
  Use after substantial implementation, when the user asks for a review-fix
  loop, adaptive review, /adaptive-code-review-loop, or when the complexity
  gate triggers. Do not start after trivial edits.
---

# Adaptive Code Review Loop

Read [code-reviewer.md](code-reviewer.md) before dispatching the reviewer.

This file is the portable protocol. It does not require a specific model family or a specific agent dispatcher. Cursor Task tool and Grok Fast dispatch live only in [references/cursor-dispatch.md](references/cursor-dispatch.md).

## When this skill runs

- Explicit: `/adaptive-code-review-loop` or a request to review-and-fix until clean. Always proceed, even if the gate previously declined.
- Automatic: after code-changing work, if `adaptive-code-review-gate` said the complexity threshold was met.

A declined gate stops **only the automatic path**. Explicit user invocation always starts this loop.

## Protocol

1. Complete proportionate verification first (tests/lint/typecheck already used in this repo, if any) and confirm it passed before dispatching the first reviewer. If there is nothing to run (docs/skill-only), say so and proceed.
2. Collect reviewer context: implementation summary, plan/requirements, changed-file list, `BASE_SHA`/`HEAD_SHA` (or uncommitted-diff description), constraints, and test evidence.
3. Dispatch one read-only reviewer session. Fill every placeholder in [code-reviewer.md](code-reviewer.md). The reviewer must not mutate the checkout.
4. Triage the returned findings against the checkout. Verify before implementing. Push back if a finding is wrong.

### Stop / continue

| Reviewer result | Action |
|-----------------|--------|
| No findings | Stop. Report clean. |
| Only Minor (any round, including 5) | Report Minors. Do **not** fix. Stop. |
| Any Critical or Important | Continue: fix this mixed-severity round. After round 5, apply Cap (no reviewer round 6). |

5. If continuing: run **one** serialized fixer session. That fixer must address every **valid** Critical, Important, **and** Minor finding from this mixed-severity round. No parallel fixers on the shared checkout.
6. Re-run proportionate repo verification (tests, lint, typecheck already used in this repo).
7. Re-dispatch a **fresh** reviewer with updated SHAs/diff and the previous finding list (what was fixed / pushed back). Skip this step after mixed round 5 (see Cap).
8. Repeat from step 4. Maximum **5** reviewer rounds.

### Cap

Do not start reviewer round 6.

- Only-Minor on any round, including 5: report Minors, do **not** fix, stop.
- Mixed round 5 (any Critical or Important plus optional Minors): fix every **valid** Critical, Important, **and** Minor finding (same as other mixed rounds), verify, then stop. Do not start reviewer round 6.
- The cap means no independent re-review after that final fix pass. Tell the user the final fixes were **not** independently re-reviewed.

## Forbidden

- Reviewer mutating the checkout
- Parallel fixers on one checkout
- Fixing an only-Minor round
- Unbounded loops
- Sending the reviewer a raw diff with no requirements or test evidence
- Treating reviewer claims as valid without checking the code
- Starting this loop automatically after a declined complexity gate (explicit invocation still proceeds)
- Attaching this loop to an always-on hook
