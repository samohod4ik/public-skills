# Install: Devin

## Hosted Devin

Hosted Devin reads committed `.agents/skills/<name>/SKILL.md`. Do not copy skills into `.devin/skills`.

## Devin CLI

Devin CLI loads project skills from `.devin/skills/<name>/SKILL.md`. It does not treat a gitignored Windows junction as an install.

Do not commit `.devin/skills/`; it is gitignored. Create the copy or link on the machine that runs the CLI.

### POSIX

```sh
mkdir -p .devin/skills
for d in .agents/skills/*; do
  name=$(basename "$d")
  ln -sfn "$(pwd)/$d" ".devin/skills/$name"
done
```

Copy instead of link:

```sh
mkdir -p .devin/skills
cp -R .agents/skills/. .devin/skills/
```

### Windows (PowerShell)

```powershell
New-Item -ItemType Directory -Force -Path .devin\skills | Out-Null
Get-ChildItem .agents\skills -Directory | ForEach-Object {
  $dest = Join-Path '.devin\skills' $_.Name
  if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
  cmd /c "mklink /J `"$dest`" `"$($_.FullName)`""
}
```

If both `.agents/skills` and `.devin/skills` exist, keep them identical or delete one. Duplicate trees that drift will confuse hosted Devin if it also scans `.devin/skills`.

Review-gate text is the paragraph in `AGENTS.md`. Hooks: `.devin/hooks.v1.json`. The matcher is `tool_name`, not git command text. See [hooks.md](hooks.md).
