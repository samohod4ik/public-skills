# Anonymization

Anonymization is removal of context that identifies a person, machine,
workplace, customer, network, or private operating history. Renaming one user
is not sufficient.

## Classify first

For every source artifact choose one:

- **publish unchanged** — already public and licensed;
- **rewrite** — useful behavior with removable private context;
- **replace** — retain the contract using synthetic examples;
- **exclude** — secrets, unclear rights, production data, or diary material.

Apply classification before copying. This reduces the chance that excluded
text enters git history and is removed only from the latest commit.

## Fresh git history

Unless the retain-history exception applies, copy classified files into a
fresh directory without the source `.git` directory, then `git init -b main`.
Set identity with `--local` (never `--global`), and create the initial commit.
If `git init -b` is unavailable, `git init` then `git branch -M main`. If a
source `.git` was copied accidentally into a target that should have been
fresh, stop and rebuild the target without it.

Retain history is an explicit exception. Use it only after
`git rev-list --objects --all` inventories every object and each object and
commit is explicitly classified public. Before remote creation, inspect
`git remote -v`. Do not remove or rewrite origin to continue retain-history
or to pass this check. If `origin` exists and is not the intended new
OWNER/REPOSITORY, stop and use a fresh target.

## Data categories

Check content, paths, filenames, metadata, and fixtures for:

### Identity

- personal names and handles;
- local usernames and email addresses;
- workstation names and device IDs;
- author-specific prose.

### Organization

- internal domains and hostnames;
- project, fleet, department, and customer labels;
- issue tracker, vault, database, and service names;
- private repository paths and organization URLs.

### Machine context

- absolute home and workspace paths;
- drive layouts, mounted shares, and local ports tied to one installation;
- scheduled-task names or service paths containing private labels;
- instructions tied to a specific workstation.

### Secrets and live data

- API tokens, private keys, cookies, credentials, and connection strings;
- subscription URLs and signed download links;
- database dumps, hardware identifiers, and production request samples;
- real allowlists, PAC/WPAD data, and internal certificates.

### Session residue

- chat narration and reviewer history;
- "we discovered", "on my machine", or "the author did not push";
- production incident timelines when the reusable rule is enough;
- notes that content was sanitized or extracted from a private setup.

## Replacement rules

- Use `example.com`, `HOST`, `OWNER/REPOSITORY`, `<PROJECT_ROOT>`, and other
  obvious placeholders.
- Use RFC 5737 documentation IP ranges for network examples.
- Use synthetic fixture values that cannot be mistaken for live credentials.
- State general constraints directly; do not explain which private detail was
  removed.
- Preserve upstream attribution and license notices.

## Automated gate

Scan every public text-bearing surface:

- Markdown and frontmatter;
- source, scripts, command files, and shell files;
- JSON/YAML settings, rules, and hooks;
- fixtures, templates, and examples.

The forbidden list should include:

- known identifiers from the source inventory;
- generic secret shapes;
- absolute-path forms for supported operating systems;
- author-machine and session-history phrases;
- obsolete private paths and names that must not return.

Do not add a broad exception when a pattern matches legitimate text. Narrow the
pattern or rewrite the public text so the exception remains explicit.

## Git metadata gate

Before push:

```text
git config --local user.name
git config --local user.email
git log --format="%H %an <%ae>%n%b"
git remote -v
```

Check:

- author emails use an approved public noreply address;
- co-author trailers use approved public identities;
- commit messages do not contain private paths or incident context;
- remotes point to the intended public owner;
- no global git configuration was changed for this repository;
- the target is a fresh directory without a copied source `.git`, or the
  retain-history exception applied after `git rev-list --objects --all`
  classified every historical object public. Do not remove or rewrite origin
  to continue retain-history or to pass this check. If `origin` exists and
  is not the intended new OWNER/REPOSITORY, stop and use a fresh target.

## Human-language pass

After code review, read public prose separately. A static pattern list will not
catch:

- dry text that still reveals an unpublished private system;
- agent-specific naming presented as a portable standard;
- vague claims such as "battle-tested" or "production-ready";
- operational stories that should be a one-line constraint.

Rewrite as: action, file, condition, limit, and verification.
