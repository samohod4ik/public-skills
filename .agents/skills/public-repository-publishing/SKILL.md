---
name: public-repository-publishing
description: >-
  Creates and publishes new public GitHub repositories from local or private
  source material while removing personal, machine, workplace, secret, and
  session-specific context. Use when preparing a repository for public release,
  creating a public GitHub repository, anonymizing reusable code or skills, or
  designing a multi-agent public catalog.
---

# Public Repository Publishing

Create a new public repository only after its content, metadata, and
documentation pass local verification and independent review.

This skill does not migrate, archive, or delete an old repository. Those
operations are out of scope. Do not start or imply migrate, archive, or
delete work during publication.

The workflow has eight phases: Contract, Inventory, Design, Sanitize and
Build, Verify, Review, Publish, Remote Verification.

Full sequence: [workflow.md](workflow.md).

## 1. Contract

Confirm or derive:

- GitHub owner and new repository name;
- local target directory;
- public description and license;
- source directories and repositories;
- required artifacts and supported clients;
- explicit exclusions;
- verification commands;
- repository-local author name and noreply email.

If visibility, ownership, license, or source classification is unclear, stop
before creating the remote.

Unless the retain-history exception applies, the default target is a fresh
directory. Do not copy the source `.git` directory into it.

## 2. Inventory

Read the source trees, requirements, plans, relevant research, git status, and
existing public examples. Classify each source:

- **public** — copy with attribution;
- **sanitizable** — rewrite or replace after removing private context;
- **excluded** — secrets, production dumps, personal diaries, or unclear rights.

Record out-of-scope work. Do not start or imply cleanup, migrate, archive, or
delete work during publication.

## 3. Design

- Choose one canonical committed location for each artifact.
- Use agent-neutral names for shared skills and workflows.
- Keep client-specific discovery and hook details in adapters or references.
- Define `README.md`, `LICENSE`, `SECURITY.md`, tests, and install docs before
  copying implementation content.
- Avoid committed aliases, duplicate skill trees, and machine-created links.

For a multi-agent skill catalog, follow
[multi-agent-layout.md](multi-agent-layout.md).

## 4. Sanitize and Build

Unless the retain-history exception applies, copy classified files into a
fresh target without the source `.git` directory. Then `git init -b main`,
set repository-local identity, and create the initial commit. If
`git init -b` is unavailable, `git init` then `git branch -M main`. Stop if
a source `.git` was copied accidentally into a target that should have been
fresh.

Retain history is an explicit alternative. Use it only after
`git rev-list --objects --all` inventories every object and each object and
commit is explicitly classified public. Before remote creation, inspect
`git remote -v`. Do not remove or rewrite origin to continue retain-history
or to pass this check. If `origin` exists and is not the intended new
OWNER/REPOSITORY, stop and use a fresh target.

Remove or replace:

- names, usernames, emails, hostnames, machine paths, and workstation IDs;
- workplace domains, fleet labels, internal repository names, and private URLs;
- tokens, keys, subscription material, database extracts, and real identifiers;
- session history, production incident diaries, and instructions tied to the
  author's machine;
- de-identification commentary such as "sanitized from the author's setup".

Use synthetic examples and neutral placeholders. Inspect file contents,
filenames, frontmatter, fixtures, comments, git authors, and co-author trailers.

Checklist: [anonymization.md](anonymization.md).

Before implementation, write a failing test for required paths and private
patterns. Then add the minimum files that make it pass.

Scan public text-bearing surfaces, including:

- root and nested Markdown;
- source and script files;
- fixtures and templates;
- rules, hooks, and client adapter configuration.

Do not rely on a manual search as the only privacy gate.

## 5. Verify

Run repository tests and validators:

- required-path and private-pattern tests;
- component validators;
- unit and integration tests already used by the source;
- `git diff --check`.

Do not claim that copied scripts work merely because the privacy test passes.

## 6. Review

Then run:

1. code review for correctness, safety, layout, tests, and release readiness;
2. a separate linguistic review for identity residue, private context, slop,
   diary tone, and agent-bound naming.

Do not create or push the public remote until both tracks reach their stop
conditions. Optional code polish does not block remote creation. See
[review-and-release.md](review-and-release.md).

## 7. Publish

- Configure `user.name` and `user.email` with `--local`, never `--global`.
- Use an approved GitHub noreply email.
- Inspect every author email and `Co-authored-by` trailer.
- Confirm ignored local install trees are not tracked.
- Keep the working tree clean before publication.

If the named repository already exists, or its visibility is not the intended
new public repository, stop and choose a new name. Never change another
repository's visibility.

Before creating the remote, inspect `git remote -v`. Do not remove or rewrite
origin to continue retain-history or to pass this check. If `origin` exists
and is not the intended new OWNER/REPOSITORY, stop and use a fresh target.

Create the remote only after tests pass and review stop conditions are met:

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

Treat authentication, scope, policy, or organization restrictions as blockers;
do not route around them.

## 8. Remote Verification

Confirm:

- repository is public;
- description and default branch are correct;
- remote `main` points to the reviewed SHA;
- required files and directories exist;
- excluded and ignored paths are absent.

Display `git rev-parse HEAD` and `git ls-remote origin refs/heads/main`.
Compare those two SHAs. After they match, fetch and list the full remote
tree with `git ls-tree -r --name-only origin/main`. Directory contents API
calls are optional focused checks of one `PATH`, not a full-tree listing
and not proof that ignored or excluded paths are absent.

Use [repository-checklist.md](repository-checklist.md) for handoff.

## Stop conditions

Stop before publication if any of these is true:

- source ownership or license is unclear;
- a secret or personal identifier is found;
- required-path or private-pattern tests fail;
- Critical or Important review findings remain;
- linguistic review still finds a checklist violation;
- git author metadata is outside the approved allowlist;
- remote visibility or destination owner is uncertain;
- the named repository already exists or is not the intended new public
  repository;
- a source `.git` directory was copied into a target that should have been
  fresh;
- retained history has an unclassified or non-public object from
  `git rev-list --objects --all`;
- Do not remove or rewrite origin to continue retain-history or to pass this
  check. If `origin` exists and is not the intended new OWNER/REPOSITORY,
  stop and use a fresh target;

## Done

The task is complete when:

1. local tests and validators pass;
2. code and linguistic review stop conditions are met;
3. `main` is pushed to the intended public repository;
4. remote visibility, default branch, required files, and SHA are verified;
5. the final response includes the GitHub URL, pushed SHA, tests, and any
   explicit residual limitations.
