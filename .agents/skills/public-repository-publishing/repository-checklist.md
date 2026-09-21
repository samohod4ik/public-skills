# Repository Checklist

## Contract

- [ ] Owner, repository name, visibility, description, and license are explicit.
- [ ] Local target directory and source locations are explicit.
- [ ] Required artifacts, supported clients, and exclusions are listed and closed.
- [ ] Migration, archive, and deletion work is excluded. Do not start or imply
      that work during publication.
- [ ] Unless the retain-history exception applies, the default target is a
      fresh directory and source `.git` is not copied.

## Source inventory

- [ ] Every source is classified as public (copy), sanitizable (rewrite or
      replace), or excluded.
- [ ] Reuse rights and attribution are known.
- [ ] Hidden files, adapters, fixtures, templates, and scripts were inspected.
- [ ] Source-to-target paths and link rewrites are recorded.

## Public structure

- [ ] There is one canonical committed location per artifact.
- [ ] Shared skill and workflow names are agent-neutral.
- [ ] Client-specific details are isolated in adapters or references.
- [ ] `README.md`, `LICENSE`, `SECURITY.md`, and tests exist.
- [ ] Local compatibility trees, generated files, and caches are ignored.

## Anonymization

- [ ] No personal names, handles, emails, or workstation identifiers remain.
- [ ] No absolute machine paths, internal hosts, domains, or fleet labels remain.
- [ ] No credentials, private keys, signed URLs, dumps, or live identifiers remain.
- [ ] No private repository names or organization inventory remain.
- [ ] No session narration, incident diary, or author-machine instructions remain.
- [ ] Examples and fixtures are synthetic.
- [ ] Upstream attribution and license notices are preserved.

## Local verification

- [ ] Required-path and private-pattern tests failed before implementation for
      the intended reason.
- [ ] Required-path and private-pattern tests pass after implementation.
- [ ] Component validators and existing tests pass.
- [ ] Links, schemas, and formatting checks pass where applicable.
- [ ] `git diff --check` passes.

## Review

- [ ] Code review received requirements, diff, constraints, and test evidence.
- [ ] Critical, Important, and linguistic violations are resolved. Optional
      code polish does not block publication.
- [ ] Separate linguistic review covers all public text-bearing surfaces.
- [ ] Tests were re-run after review fixes.

## Git metadata

- [ ] Fresh target (`git init -b main` after classified copy, without source
      `.git`; `git branch -M main` only if `git init -b` is unavailable)
      OR retain-history exception after `git rev-list --objects --all`
      classifies every object public. Do not remove or rewrite origin to
      continue retain-history or to pass this check. If `origin` exists and
      is not the intended new OWNER/REPOSITORY, stop and use a fresh target.
- [ ] `user.name` and `user.email` are repository-local (`--local`, never `--global`).
- [ ] Author emails are approved public identities.
- [ ] Co-author trailers are approved public identities.
- [ ] Commit messages contain no private paths or session history.
- [ ] Worktree is clean.
- [ ] Tracked files do not include ignored compatibility trees.

## Publication

- [ ] Remote owner and repository name are correct.
- [ ] If the name already exists or visibility is not the new public repo, a new name was chosen.
- [ ] No other repository's visibility was changed.
- [ ] Public repository was created only after Critical, Important, and
      linguistic violations were resolved. Optional code polish does not
      block remote creation.
- [ ] Create used `--public --source . --remote origin --description` and not `--push`.
- [ ] Immediately after create, `git remote -v` and
      `gh repo view OWNER/REPOSITORY --json url,isPrivate,description --jq "{url:.url,isPrivate:.isPrivate,description:.description}"`
      were inspected before push.
- [ ] Push ran only after origin matched OWNER/REPOSITORY, `isPrivate` was false,
      and the description matched.
- [ ] `origin` points to the intended repository.
- [ ] Reviewed `main` was pushed with a separate `git push -u origin main`.

## Remote verification

- [ ] Repository visibility is public.
- [ ] Description and default branch are correct (`--jq .defaultBranchRef.name`).
- [ ] Local HEAD SHA equals `git ls-remote origin refs/heads/main` after
      comparing those two displayed SHAs, before the tree listing.
- [ ] Full remote tree was listed with `git ls-tree -r --name-only origin/main`.
- [ ] Required files are present in that tree.
- [ ] Excluded and ignored paths are absent from that tree.
- [ ] Directory contents API, if used, was only a focused check of one `PATH`,
      not a full-tree listing.
- [ ] Handoff reports URL, SHA, tests, reviews, and residual limitations.
