# Public Repository Publishing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add and publish an agent-neutral skill for creating public GitHub repositories without private or session context, with durable project documentation in Obsidian.

**Architecture:** Keep one canonical skill under `.agents/skills/public-repository-publishing`. Put the portable phase sequence in `SKILL.md` and detailed concerns in five one-level references. Enforce presence and public safety through the existing repository surface test; keep local project knowledge in Obsidian.

**Tech Stack:** Markdown Agent Skills, Python public-surface test, Git, GitHub CLI, Obsidian Markdown/MCP.

## Global Constraints

- Canonical skill tree is only `.agents/skills`; do not commit client-specific copies.
- Skill and folder names are agent-neutral.
- No executable publish script; GitHub creation and push remain explicit operations.
- Migration, archival, and deletion of old repositories are out of scope.
  Do not start or imply that work during publication.
- Public text contains no personal, machine, workplace, secret, or session-specific context.
- Run code review and a separate linguistic review before push.

---

### Task 1: Lock the Skill Contract

**Files:**
- Modify: `tests/test_public_surface.py`
- Test: `tests/test_public_surface.py`

**Interfaces:**
- Consumes: `SKILLS = ROOT / ".agents" / "skills"`.
- Produces: required-path checks for `public-repository-publishing` and README catalog checks.

- [ ] **Step 1: Write the failing contract**

Add required paths:

```python
PUBLIC_REPO_SKILL = SKILLS / "public-repository-publishing"

required.extend(
    [
        PUBLIC_REPO_SKILL / "SKILL.md",
        PUBLIC_REPO_SKILL / "workflow.md",
        PUBLIC_REPO_SKILL / "anonymization.md",
        PUBLIC_REPO_SKILL / "multi-agent-layout.md",
        PUBLIC_REPO_SKILL / "review-and-release.md",
        PUBLIC_REPO_SKILL / "repository-checklist.md",
    ]
)
```

Add a catalog assertion:

```python
if "public-repository-publishing" not in catalog:
    fail("README.md must list public-repository-publishing")
```

Skill-tree gates for this skill:

- every `gh repo create` line includes `--public` and `--description` and omits `--push`;
- skill files contain source `.git` exclusion, `git rev-list --objects --all`, `git ls-tree -r`, pre-push `git remote -v`, and collision wording to choose a new name;
- `git config --global` is forbidden in every skill file, not only two;
- executable extensions remain banned in the skill directory.

- [ ] **Step 2: Verify RED**

Run:

```text
python tests/test_public_surface.py
```

Expected: `FAIL missing required file: .agents/skills/public-repository-publishing/SKILL.md`.

- [ ] **Step 3: Keep the failing test for Task 2**

Do not weaken forbidden-pattern scanning or remove existing assertions.

### Task 2: Implement the Skill and Catalog Entry

**Files:**
- Create: `.agents/skills/public-repository-publishing/SKILL.md`
- Create: `.agents/skills/public-repository-publishing/workflow.md`
- Create: `.agents/skills/public-repository-publishing/anonymization.md`
- Create: `.agents/skills/public-repository-publishing/multi-agent-layout.md`
- Create: `.agents/skills/public-repository-publishing/review-and-release.md`
- Create: `.agents/skills/public-repository-publishing/repository-checklist.md`
- Modify: `README.md`
- Test: `tests/test_public_surface.py`

**Interfaces:**
- Consumes: repository owner/name/visibility/license/local path/source inventory.
- Produces: a reviewed public repository URL and immutable pushed SHA.

- [ ] **Step 1: Create `SKILL.md`**

Use frontmatter:

```yaml
---
name: public-repository-publishing
description: >-
  Creates and publishes new public GitHub repositories from local or private
  source material while removing personal, machine, workplace, secret, and
  session-specific context. Use when preparing a repository for public release,
  creating a public GitHub repository, anonymizing reusable code or skills, or
  designing a multi-agent public catalog.
---
```

The body must define inputs, stop conditions, eight phases, done criteria, and links to every one-level reference. It must state that migrate, archive, and delete work is out of scope and must not start or be implied during publication. The eight phases are Contract, Inventory, Design, Sanitize and Build, Verify, Review, Publish, Remote Verification.

- [ ] **Step 2: Add focused references**

`workflow.md` defines Contract through Remote Verification. Unless the
retain-history exception applies, fresh-target steps use `git init -b main`
(`git branch -M main` only if needed). After
`gh repo create`, inspect `git remote -v` and
`gh repo view OWNER/REPOSITORY --json url,isPrivate,description --jq "{url:.url,isPrivate:.isPrivate,description:.description}"`
before a separate `git push -u origin main`. Remote verification requires
comparing the displayed `git ls-remote origin refs/heads/main` SHA with
`git rev-parse HEAD` before the tree listing.

`anonymization.md` defines classification, forbidden data categories, git metadata checks, synthetic examples, and dry public tone. Prefer a fresh target. Retain history is an explicit exception after `git rev-list --objects --all` inventory and a `git remote -v` origin gate. Do not remove or rewrite origin to continue retain-history or to pass this check. If `origin` exists and is not the intended new OWNER/REPOSITORY, stop and use a fresh target.

`multi-agent-layout.md` defines `.agents/skills` as the portable canonical tree and documents Cursor, Claude Code, Codex, and Devin adapters without duplicating skill trees.

`review-and-release.md` defines test order, adaptive code review, independent linguistic review, repository-local identity, remote creation, push, and remote verification. Optional code polish does not block remote creation.

`repository-checklist.md` provides checkboxes for pre-publication and post-publication gates.

- [ ] **Step 3: Add README catalog row**

Add:

```markdown
| [public-repository-publishing](.agents/skills/public-repository-publishing/SKILL.md) | Preparing a sanitized public GitHub repository for first publication |
```

- [ ] **Step 4: Verify GREEN**

Run:

```text
python tests/test_public_surface.py
python tests/test_remind_before_git_write.py
```

Expected: both print `PASS`.

### Task 3: Write Durable Obsidian Documentation

**Files:**
- Create: `10_projects/public-skills/README.md` in the vault
- Create: `10_projects/public-skills/architecture.md` in the vault
- Create: `10_projects/public-skills/publication-runbook.md` in the vault
- Create: `10_projects/public-skills/decisions.md` in the vault
- Create: `60_skills/workspace/public-repository-publishing.md` in the vault

**Interfaces:**
- Consumes: design spec, implementation plan, repository URL, research run links, and pushed SHA.
- Produces: project navigation, architecture, repeatable runbook, durable decisions, and a skill registry card.

- [ ] **Step 1: Write project navigation**

Include status, repository URL, canonical paths, research links, and links to architecture/runbook/decisions.

- [ ] **Step 2: Write architecture**

Document canonical `.agents/skills`, client adapters, hook contract separation, public-surface walker, and review boundaries.

- [ ] **Step 3: Write publication runbook**

Document inputs, source classification, anonymization, tests, review sequence, git identity checks, GitHub commands, remote verification, and failure modes.

- [ ] **Step 4: Write decisions**

Record 3-7 durable decisions with Decision/Anti/Refs, including one canonical tree, sanitize-before-copy, two review tracks, local git identity, and no implied destructive cleanup.

- [ ] **Step 5: Write skill card**

Point to `.agents/skills/public-repository-publishing/SKILL.md` and the public GitHub URL; summarize triggers and references.

### Task 4: Review, Commit, Push, and Verify

**Files:**
- Modify only files required by valid review findings.

**Interfaces:**
- Consumes: clean local tests and the complete diff.
- Produces: pushed `main`, GitHub file verification, and final SHA.

- [ ] **Step 1: Run all local verification**

```text
python tests/test_public_surface.py
python tests/test_remind_before_git_write.py
python .agents/skills/throne-agents-tun/scripts/validate_skill.py --root .agents/skills/throne-agents-tun
python -m pytest .agents/skills/throne-agents-tun/tests -q
git diff --check
```

- [ ] **Step 2: Apply the adaptive review gate**

The change exceeds three production files and 150 non-generated lines, so run `adaptive-code-review-loop`. Fix valid mixed-severity findings and stop on a clean or only-Minor round.

- [ ] **Step 3: Run linguistic review**

Review all new public Markdown for slop, author context, private paths, agent-bound naming, and diary tone. Fix checklist violations and re-run tests.

- [ ] **Step 4: Validate metadata and commit**

```text
git config --local user.name
git config --local user.email
git log --format="%ae%n%b"
git status --short
```

Only the repository noreply author and allowed automation co-author may appear.

- [ ] **Step 5: Push and verify**

```text
git push origin main
git rev-parse HEAD
git ls-remote origin refs/heads/main
git fetch origin main
git ls-tree -r --name-only origin/main
gh repo view OWNER/REPOSITORY --json url,isPrivate,description --jq "{url:.url,isPrivate:.isPrivate,description:.description}"
gh repo view OWNER/REPOSITORY --json defaultBranchRef --jq .defaultBranchRef.name
```

Stop unless the displayed `git ls-remote origin refs/heads/main` SHA equals `git rev-parse HEAD` before the tree listing. Expected: public repository, default branch `main`, required skill files present in the remote tree. Directory contents API may be an optional focused check of one `PATH`, not a full-tree listing.
