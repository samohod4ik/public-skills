# Workflow

The workflow has eight phases: Contract, Inventory, Design, Sanitize and
Build, Verify, Review, Publish, Remote Verification.

## Phase 1: Contract

Record:

- owner and repository name;
- local directory;
- visibility target: a new public repository;
- description and license;
- required content;
- supported clients or platforms;
- source locations;
- exclusions;
- done criteria.

Resolve ownership and licensing before copying files. A technically clean file
is not publishable when reuse rights are unclear.

Unless the retain-history exception applies, the default local directory is
a fresh target. Do not copy a source `.git` directory into it.

## Phase 2: Inventory

Read source trees and git metadata rather than copying directories wholesale.
Inventory:

- code, scripts, fixtures, templates, docs, and tests;
- rules, hooks, settings, manifests, and hidden files;
- symlinks, junctions, generated files, caches, and local overrides;
- commit authors, co-authors, remotes, and branch state.

Classify sources as public (copy), sanitizable (rewrite or replace), or
excluded. Keep a source-to-target map so references and relative paths can be
rewritten deliberately.

## Phase 3: Design

Define the complete committed tree before copying classified files. Prefer:

```text
README.md
LICENSE
SECURITY.md
AGENTS.md
docs/
tests/
<canonical artifacts>
<optional client adapters>
```

Keep operational scripts beside the skill or component that owns them. Do not
leave root-level files that only make sense in their source repository.

## Phase 4: Sanitize and Build

Write a failing test that requires the planned files and rejects known private
patterns. Confirm it fails for missing required paths or a known private
pattern.

Unless the retain-history exception applies, then:

1. create a fresh target directory;
2. copy only classified files, excluding the source `.git` directory;
3. `git init -b main` in the target (if unavailable, `git init` then
   `git branch -M main`);
4. set `user.name` and `user.email` with `--local`, never `--global`;
5. create the initial commit.

Stop if a source `.git` was copied accidentally into a target that should
have been fresh. Rebuild the target without it.

Retain history is an explicit alternative. Use it only after
`git rev-list --objects --all` inventories every object and each object and
commit is explicitly classified public. Before remote creation, inspect
`git remote -v`. Do not remove or rewrite origin to continue retain-history
or to pass this check. If `origin` exists and is not the intended new
OWNER/REPOSITORY, stop and use a fresh target.

In either case, rewrite paths and links, replace private examples with
synthetic values, and run the test after each logical batch.

Scan file contents and names. Include hidden configuration and text-bearing
fixtures; ignore VCS metadata and test caches.

## Phase 5: Verify

Run:

- required-path and private-pattern tests;
- component validators;
- unit and integration tests already used by the source;
- link, format, or schema checks when present;
- `git diff --check`.

Do not claim that copied scripts work merely because the privacy test passes.

## Phase 6: Review

Code review runs first against requirements and the complete diff. A separate
linguistic review runs after code findings are resolved.

The linguistic pass checks public prose and comments for:

- identity residue;
- source-repository or workstation context;
- vague claims and marketing language;
- incident diaries and session narration;
- names tied to one agent when the workflow is portable.

Re-run verification after every fix batch.

## Phase 7: Publish

Confirm:

- branch is `main`;
- local identity is repository-scoped (`--local`, never `--global`);
- author and co-author metadata is approved;
- ignored local install directories are untracked;
- remote does not already point to an unintended repository;
- worktree is clean.

If the named repository already exists, or its visibility is not the intended
new public repository, stop and choose a new name. Never change another
repository's visibility.

Before creating the remote, inspect `git remote -v`. Do not remove or rewrite
origin to continue retain-history or to pass this check. If `origin` exists
and is not the intended new OWNER/REPOSITORY, stop and use a fresh target.

Create the public remote without pushing:

```text
gh repo create OWNER/REPOSITORY --public --source . --remote origin --description "PUBLIC DESCRIPTION"
```

Immediately after create, inspect before any push:

```text
git remote -v
gh repo view OWNER/REPOSITORY --json url,isPrivate,description --jq "{url:.url,isPrivate:.isPrivate,description:.description}"
```

Stop unless `origin` matches OWNER/REPOSITORY, `isPrivate` is false, and the
description matches the public description. Do not pass `--push`. Then:

```text
git push -u origin main
```

## Phase 8: Remote Verification

Display `git rev-parse HEAD` and `git ls-remote origin refs/heads/main`.
Compare those two SHAs. After they match, fetch and list the full remote
tree:

```text
git rev-parse HEAD
git ls-remote origin refs/heads/main
git fetch origin main
git ls-tree -r --name-only origin/main
gh repo view OWNER/REPOSITORY --json url,isPrivate,description --jq "{url:.url,isPrivate:.isPrivate,description:.description}"
gh repo view OWNER/REPOSITORY --json defaultBranchRef --jq .defaultBranchRef.name
```

`defaultBranchRef` is a nested object; `.defaultBranchRef.name` is the branch
name.

Optional focused check: `PATH` is one repository path to inspect, not a
full-tree listing.

```text
gh api repos/OWNER/REPOSITORY/contents/PATH --jq ".[].name"
```

Verify required files against the full tree listing. Confirm ignored and
excluded paths are absent from that listing. Do not infer a complete upload
from a successful push message or from a single directory contents response.

## Failure handling

| Failure | Action |
|---------|--------|
| Authentication denied | Report the account/scope blocker and stop |
| Repository already exists | Stop and choose a new name. Never change another repository's visibility |
| Visibility is not the intended new public repository | Stop and choose a new name. Never change another repository's visibility |
| Privacy test finds a match | Classify and remove or replace it; do not whitelist blindly |
| Review finds only optional polish | Optional polish does not block remote creation |
| Push succeeds but remote files are missing | Compare branch and SHA, then inspect the full remote tree |
| Source `.git` was copied into a target that should have been fresh | Stop and rebuild the fresh target without it |
| Retained history has an unclassified or non-public object | Stop; prefer a fresh target after `git rev-list --objects --all` |
| `origin` exists and is not the intended new OWNER/REPOSITORY | Do not remove or rewrite origin to continue retain-history or to pass this check. Stop and use a fresh target |
