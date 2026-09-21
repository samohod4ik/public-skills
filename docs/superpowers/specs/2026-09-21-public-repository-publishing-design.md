# Public Repository Publishing Skill Design

## Goal

Add an agent-neutral skill that guides creation and publication of a new
public GitHub repository without exposing personal, machine, workplace, or
session-specific context.

The skill is stored only at
`.agents/skills/public-repository-publishing/`. The committed repository does
not duplicate it under client-specific skill directories.

## Scope

The workflow covers:

1. source and requirement inventory;
2. repository and skill layout design;
3. anonymization before copying content;
4. public-surface tests and metadata checks;
5. code and linguistic review gates;
6. GitHub repository creation and first push;
7. remote verification after publication.

Migration, archival, and deletion of an old repository are out of scope.
Those destructive operations require a separate task and explicit gates.

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

### 1. Discovery

- Confirm owner, repository name, visibility, license, description, and local
  directory.
- Inspect source trees, plans, relevant research, existing public patterns,
  and git state.
- Classify every source as public, private-but-sanitizable, or excluded.
- Record explicit out-of-scope operations.

### 2. Design

- Choose one canonical committed skill tree.
- Keep skill names agent-neutral.
- Add client adapters only where discovery or hook contracts differ.
- Separate portable workflow text from client-specific dispatch details.
- Define required root documents and verification commands.

### 3. Sanitize Before Copy

- Remove personal names, usernames, home paths, machine paths, hostnames,
  workplace domains, fleet identifiers, secret URLs, tokens, and private keys.
- Remove production diaries, session history, author-machine instructions, and
  de-identification commentary.
- Inspect git author and co-author metadata before the first push.
- Use synthetic examples and placeholders where operational examples are
  required.

### 4. Verify Locally

- Add a repository-level public-surface test that scans documentation, code,
  scripts, rules, hooks, and adapter configuration.
- Assert required files and forbidden obsolete paths.
- Run skill-specific tests and validators.
- Keep the worktree clean before review.

### 5. Review

- Run a code-review loop after tests.
- Fix valid Critical and Important findings according to the repository's stop
  rules.
- Run a separate linguistic review for slop, identity residue, private context,
  agent-bound naming, and diary tone.
- Do not create or push the public remote until both review gates finish.

### 6. Publish

- Configure repository-local git identity; never modify global identity.
- Verify author and co-author email allowlists.
- Create the public GitHub repository without an initial push.
- Push the reviewed `main` branch.

### 7. Verify Remotely

- Confirm visibility, description, default branch, and remote HEAD.
- Confirm required skill directories and files through the GitHub API.
- Confirm ignored client-local skill trees were not committed.
- Report the repository URL and immutable commit SHA.

## Safety Model

- Read-only inspection does not require confirmation.
- Visibility change, remote creation, and first push occur only after tests and
  reviews.
- Secret detection is deny-by-default: uncertain content is excluded until
  classified.
- Destructive cleanup of other repositories is never implied by this skill.
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
