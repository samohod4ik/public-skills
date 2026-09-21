# The Ralph technique — background and sources

## Origin

Coined by Geoffrey Huntley as **"Ralph Wiggum as a software engineer"**
(https://ghuntley.com/ralph/). Named after the endearingly simple-minded Simpsons
character — the joke being that the technique embraces the agent's limitations (no
memory across runs, prone to repeating mistakes) instead of fighting them.

Huntley used it to build **Cursed**, a self-hosting compiler and esoteric programming
language, almost entirely autonomously over roughly three months. The most-quoted cost
figure associated with the technique: an engineer reported delivering an MVP — tested
and reviewed, against a roughly $50,000-scope contract — for about $297 in API costs by
putting the agent in a loop (Y Combinator hackathon write-up: "We Put a Coding Agent in
a While Loop and It Shipped 6 Repos Overnight").

## Core mechanism

> "In its purest form, Ralph is a Bash loop." — Geoffrey Huntley

A `while true` loop feeds the **same fixed prompt** to a coding agent on every
iteration. Nothing about the instruction changes between iterations — the world does,
because the agent re-reads the repository and its own scratch/plan files each time, and
finds the work a little further along than the last pass.

Per-iteration cycle (from `ghuntley/how-to-ralph-wiggum`):

1. **Orient** — subagents study `specs/*` (requirements)
2. **Read plan** — study `IMPLEMENTATION_PLAN.md`
3. **Select** — pick the single most important task (the agent decides, not you)
4. **Investigate** — study the relevant code/state; *"don't assume it's not
   implemented"* — a common failure mode is the agent running `ripgrep`, finding
   nothing, and wrongly concluding a feature doesn't exist yet
5. **Implement** — do the work
6. **Validate** — run build/tests as backpressure before committing
7. **Update the plan** — mark the task done, note discoveries/bugs found along the way
8. **Update AGENTS.md** — if the iteration learned something operationally useful
9. **Commit**
10. **Loop ends** → context is cleared → next iteration starts fresh

## Why fresh context per iteration matters

> "If you implement Ralph as part of the agent harness via skill/command/etc you are
> missing the point of Ralph, which is to use always a fresh context." — Michael
> Arnaldi, quoted in ZeroSync's technical deep dive.

Each iteration starts a **new process** with a clean context window. This is what
distinguishes Ralph from a long-running continuous agent session: no context rot, no
compaction, no gradual drift — every pass re-derives its understanding of the current
state purely from what's on disk (plan files, specs, code, git history).

Running the "same idea" inside a single continuous chat session (re-issuing a prompt on
a timer, e.g. a generic `/loop` skill inside one conversation) is a **weaker
approximation**: it's easier to set up and fine for light/monitoring-style tasks, but
loses the core context-hygiene benefit for larger multi-step work. This skill's runner
scripts implement the "real" version — a brand-new agent process every iteration.

## Variants and related work

- **SpecKit-based / spec-driven Ralph** — a more structured take combining Ralph with
  GitHub SpecKit-style specifications, where the loop picks a spec, implements it with a
  fresh context each time, and only advances when the agent explicitly signals `DONE`.
- **Matt Pocock's variant** — a differently-tuned explainer/implementation of the same
  core idea.
- Community consensus: works best for **greenfield, clearly-specified work** where
  ~90% automated completion with ~10% human cleanup is an acceptable trade — not a
  guarantee of zero supervision.

## Primary sources

- Geoffrey Huntley, "Ralph Wiggum as a software engineer" — https://ghuntley.com/ralph/
- `ghuntley/how-to-ralph-wiggum` (GitHub) — https://github.com/ghuntley/how-to-ralph-wiggum
- "The Ralph Technique: Geoffrey Huntley's Agentic Coding Loop" — howaiworks.ai
- "Ralph Wiggum — Viral Agentic Coding Loop, Simplified" — https://ralph-wiggum.ai/
- "The Ralph Loop: Long-Running AI Agents" — ZeroSync technical deep dive
