# Public Repository Publishing Skill Design

## Goal

Add an agent-neutral skill that guides creation and publication of a new
public GitHub repository without exposing personal, machine, workplace, or
session-specific context.

The skill is stored only at
`.agents/skills/public-repository-publishing/`. The committed repository does
not duplicate it under client-specific skill directories.

## Scope

The workflow has eight phases: Contract, Inventory, Design, Sanitize and
Build, Verify, Review, Publish, Remote Verification.

Migration, archival, and deletion of an old repository are out of scope.
Do not start or imply migrate, archive, or delete work during publication.

## Skill Structure

```text
.agents/skills/public-repository-publishing/
  SKILL.md
  workflow.md
  anonymization.md
  multi-agent-layout.md
  review-and-release.md
  repository-checklist.md
```

`SKILL.md` contains triggers, required inputs, the phase sequence, stop
conditions, and done criteria. References remain one level below `SKILL.md`.
No executable publish script is included: public repository creation and push
remain explicit, reviewable operations.

## Workflow

### 1. Contract

- Confirm owner, repository name, visibility, license, description, and local
  directory.
- The visibility target is a new public repository.
- Unless the retain-history exception applies, the default target is a fresh
  directory. Do not copy the source `.git` directory into it.

### 2. Inventory

- Inspect source trees, plans, relevant research, existing public patterns,
  and git state.
- Classify every source as public (copy), sanitizable (rewrite or replace),
  or excluded.
- Record explicit out-of-scope operations. Do not start or imply migrate,
  archive, or delete work during publication.

### 3. Design

- Choose one canonical committed skill tree.
- Keep skill names agent-neutral.
- Add client adapters only where discovery or hook contracts differ.
- Separate portable workflow text from client-specific dispatch details.
- Define required root documents and verification commands.

### 4. Sanitize and Build

- Copy public files; rewrite sanitizable files; replace private examples with
  synthetic values; exclude secrets, unclear rights, and diary material.
- Remove personal names, usernames, home paths, machine paths, hostnames,
  workplace domains, fleet identifiers, secret URLs, tokens, and private keys.
- Remove production diaries, session history, author-machine instructions, and
  de-identification commentary.
- Inspect git author and co-author metadata before the first push.
- Use synthetic examples and placeholders where operational examples are
  required.
- Unless the retain-history exception applies, copy classified files into a
  fresh target without the source `.git` directory, then `git init -b main`.
- Retain history is an explicit alternative after `git rev-list --objects --all`
  classifies every object public. Do not remove or rewrite origin to continue
  retain-history or to pass this check. If `origin` exists and is not the
  intended new OWNER/REPOSITORY, stop and use a fresh target.

### 5. Verify

- Write a failing test for required paths and private patterns.
- Scan public text-bearing surfaces.
- Run skill-specific tests and validators.
- Keep the worktree clean before review.

### 6. Review

- Run a code-review loop after tests.
- Fix valid Critical and Important findings according to the repository's stop
  rules.
- Run a separate linguistic review for slop, identity residue, private context,
  agent-bound naming, and diary tone.
- Do not create the remote when Critical or Important findings remain or when
  linguistic review still finds a checklist violation. Optional code polish
  does not block remote creation.

### 7. Publish

- Configure repository-local git identity; never modify global identity.
- Verify author and co-author email allowlists.
- Create without `--push`. Inspect `git remote -v` and `gh repo view`, then
  push `main`.
- Do not change another repository's visibility.

### 8. Remote Verification

- Confirm visibility, description, and default branch.
- Display `git rev-parse HEAD` and `git ls-remote origin refs/heads/main`.
  Compare those two SHAs.
- After they match, list the full remote tree with
  `git ls-tree -r --name-only origin/main`.
- Confirm required files exist and ignored or excluded paths are absent from
  that listing.
- Directory contents API calls are optional focused checks of one `PATH`,
  not a full-tree listing.
- Report the repository URL and immutable commit SHA.

## Safety Model

- Read-only inspection does not require confirmation.
- Remote creation and first push occur only after tests and reviews.
- Do not change another repository's visibility.
- Secret detection is deny-by-default: uncertain content is excluded until
  classified.
- Destructive cleanup of other repositories is never implied by this skill.
  Do not open a cleanup task during publication.
- Authentication or missing GitHub scopes are reported as blockers; the skill
  does not bypass them.

## Tests

Implementation starts with a failing contract in
`tests/test_public_surface.py` that requires the new skill and reference files.
After the skill is added:

- `python tests/test_public_surface.py`
- `python tests/test_remind_before_git_write.py`
- existing skill-specific validators and tests

The review gate is evaluated after verification.

## Obsidian Documentation

Create:

- `10_projects/public-skills/README.md`
- `10_projects/public-skills/architecture.md`
- `10_projects/public-skills/publication-runbook.md`
- `10_projects/public-skills/decisions.md`
- `60_skills/workspace/public-repository-publishing.md`

The project notes record the repository URL, architecture, research links,
release process, failure modes, and durable decisions. The skill card points
to the GitHub canonical file. Obsidian may contain local source references;
public repository files must not.

## Acceptance Criteria

- The new skill is discoverable at the canonical `.agents/skills` path.
- `SKILL.md` is under 500 lines and links only to one-level references.
- The repository README lists the skill.
- Public-surface tests cover the skill and pass.
- Obsidian contains the five structured notes above.
- Code review and linguistic review finish under their stop rules.
- `main` is pushed to the public GitHub repository.
- Remote verification confirms the new skill at the pushed SHA.
