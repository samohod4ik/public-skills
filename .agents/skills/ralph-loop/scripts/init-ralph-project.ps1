<#
    Scaffold a new Ralph Loop project from this skill's templates.

    Usage:
      .\init-ralph-project.ps1 C:\path\to\my-project "One-line description of the task"
#>

param(
    [Parameter(Mandatory = $true)][string]$ProjectDir,
    [Parameter(Mandatory = $true)][string]$ProjectName
)

$SkillDir = Split-Path -Parent $PSScriptRoot
$TemplatesDir = Join-Path $SkillDir "templates"

New-Item -ItemType Directory -Force -Path $ProjectDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectDir "logs") | Out-Null

foreach ($file in @("AGENTS.md", "PROMPT.md", "IMPLEMENTATION_PLAN.md", "PROGRESS.md")) {
    $src = Join-Path $TemplatesDir "$file.template"
    $dst = Join-Path $ProjectDir $file
    if (Test-Path $dst) {
        Write-Host "Skipping $file (already exists)"
        continue
    }
    $content = Get-Content -Raw -Path $src
    $content = $content -replace '\{\{PROJECT_NAME\}\}', $ProjectName
    $content = $content -replace '\{\{HARNESS_DIR\}\}', $ProjectDir
    Set-Content -Path $dst -Value $content -NoNewline
    Write-Host "Created $dst"
}

Copy-Item (Join-Path $SkillDir "scripts\loop.ps1") -Destination (Join-Path $ProjectDir "loop.ps1") -Force
Copy-Item (Join-Path $SkillDir "scripts\loop.sh") -Destination (Join-Path $ProjectDir "loop.sh") -Force
Write-Host "Copied loop.ps1 / loop.sh"

$envFile = Join-Path $ProjectDir ".env"
if (-not (Test-Path $envFile)) {
    "# Secrets for this Ralph project. Do not commit." | Set-Content -Path $envFile
}
$gitignore = Join-Path $ProjectDir ".gitignore"
if (-not (Test-Path $gitignore)) {
    @(".env", "logs/", "*.log") | Set-Content -Path $gitignore
}

Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit $ProjectDir\AGENTS.md - fill in {{REAL_TARGET_ENV_PATH}} and any task-specific rules"
Write-Host "  2. Edit $ProjectDir\IMPLEMENTATION_PLAN.md - turn Phase placeholders into concrete checkboxes"
Write-Host "  3. cd $ProjectDir; .\loop.ps1"
