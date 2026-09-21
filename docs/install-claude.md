# Install: Claude Code

Claude Code discovers project skills only at `.claude/skills/<name>/SKILL.md`. It does not load `.agents/skills`.

Do not commit `.claude/skills/`; it is gitignored. Create the copy or link on the machine that runs Claude Code.

## POSIX

From the repository root:

```sh
mkdir -p .claude/skills
for d in .agents/skills/*; do
  name=$(basename "$d")
  ln -sfn "$(pwd)/$d" ".claude/skills/$name"
done
```

Copy instead of link:

```sh
mkdir -p .claude/skills
cp -R .agents/skills/. .claude/skills/
```

If both `.agents/skills` and `.claude/skills` exist, keep them identical or delete the extra tree.

## Windows (PowerShell)

Junction (no admin):

```powershell
New-Item -ItemType Directory -Force -Path .claude\skills | Out-Null
Get-ChildItem .agents\skills -Directory | ForEach-Object {
  $dest = Join-Path '.claude\skills' $_.Name
  if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
  cmd /c "mklink /J `"$dest`" `"$($_.FullName)`""
}
```

Copy:

```powershell
New-Item -ItemType Directory -Force -Path .claude\skills | Out-Null
Copy-Item -Recurse -Force .agents\skills\* .claude\skills\
```

A gitignored junction is local install, not a repository feature.

Rules: `.claude/rules/review-gate.md`. Hooks: `.claude/settings.json` (the `hooks/` directory is not auto-loaded). See [hooks.md](hooks.md).
