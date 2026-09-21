# Review and Release

Publication is the final phase, not an early integration test.

## Verification order

Run in this order:

1. required-path and private-pattern tests;
2. component validators and unit tests;
3. formatting, schema, link, and diff checks;
4. code review;
5. linguistic review;
6. metadata and tracked-file checks;
7. remote creation and push;
8. remote verification.

Later checks do not replace earlier checks. A code reviewer is not a secret
scanner, and a successful push is not proof of correct visibility.

## Code review

Give the reviewer:

- implementation summary;
- requirements or plan;
- full changed-file list and git range;
- constraints and exclusions;
- exact test commands and fresh results.

Review:

- plan alignment;
- missing files or broken links;
- unsafe defaults and destructive behavior;
- client discovery and hook contracts;
- test completeness;
- release readiness.

Use bounded review/fix rounds. Verify findings against the checkout before
editing. Follow the repository's severity and stop rules.

## Linguistic review

Use a fresh read-only reviewer after code findings are resolved. Cover all
public docs, comments, frontmatter, rules, hook messages, templates, and
fixtures.

Checklist:

- personal, machine, workplace, or customer residue;
- source-repository and session context;
- diary language and incident narratives;
- marketing claims and vague adjectives;
- agent-specific names for portable workflows;
- references to files that are absent from the public tree.

Fix wording that violates the checklist even when it would be a Minor code
review finding. Re-run required-path and private-pattern tests after edits.

## Repository-local identity

Set only local values:

```text
git config --local user.name "Example Name"
git config --local user.email "12345678+USERNAME@users.noreply.github.com"
```

Never use `--global`.

Before push, list every commit author and trailer:

```text
git log --format="%H%n%an <%ae>%n%b%n-----"
```

Stop on an unapproved identity. Rewriting published history is not part of this
skill.

## Fresh target or retain-history exception

Unless the retain-history exception applies, build a fresh target by copying
classified files without the source `.git` directory, then `git init -b main`,
set `--local` identity, and create the initial commit. If `git init -b` is
unavailable, `git init` then `git branch -M main`. Stop if a source `.git`
was copied accidentally into a target that should have been fresh.

Retain history is an explicit alternative. Use it only after
`git rev-list --objects --all` inventories every object and each object and
commit is explicitly classified public. Before remote creation, inspect
`git remote -v`. Do not remove or rewrite origin to continue retain-history
or to pass this check. If `origin` exists and is not the intended new
OWNER/REPOSITORY, stop and use a fresh target.

## Create and push

If the named repository already exists, or its visibility is not the intended
new public repository, stop and choose a new name. Never change another
repository's visibility. Do not archive, transfer, rename, make private, or
delete another repository as part of this workflow.

Before creating the remote, inspect `git remote -v`. Do not remove or rewrite
origin to continue retain-history or to pass this check. If `origin` exists
and is not the intended new OWNER/REPOSITORY, stop and use a fresh target.

Create the new repository without an initial push:

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

Do not create the remote when Critical or Important findings remain, when
linguistic review still finds a checklist violation, or when the destination
owner is uncertain. Optional code polish does not block remote creation.

## Remote verification

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

Verify:

- `isPrivate` is `false`;
- default branch is `main`;
- local and remote SHA match after comparing the two displayed values
  (`git rev-parse HEAD` and `git ls-remote origin refs/heads/main`) before
  the tree listing;
- required files exist in the full remote tree;
- ignored compatibility trees and excluded files are absent from that tree.

## Scope boundary

Do not archive, transfer, rename, make private, or delete another repository as
part of this workflow.
