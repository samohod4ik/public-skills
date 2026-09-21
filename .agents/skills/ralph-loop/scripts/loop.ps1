<#
    Ralph Loop runner - Windows/PowerShell.
    Shipped adapter is Cursor CLI (`agent`). Other CLIs replace Invoke-Executor.
    Every iteration spawns a NEW executor process (fresh context).
    State between iterations lives only on disk (IMPLEMENTATION_PLAN.md,
    PROGRESS.md) and in this directory's git history.

    Keep this script itself pure ASCII. Windows PowerShell 5.1 without a BOM can
    misread non-ASCII bytes in .ps1 files and produce parse errors far from the
    actual problem.

    Usage:
      cd my-ralph-project
      .\loop.ps1
      .\loop.ps1 -Model claude-opus-4-8-thinking-high -MaxIterations 1   # Gate 0 / irreversible step
      .\loop.ps1 -MaxIterations 5

    Requirements:
      - Cursor CLI installed and logged in: `agent --version` works (`agent login` if not).
        Install: irm 'https://cursor.com/install?win32=true' | iex
      - git available in PATH
#>

param(
    [string]$Model = "claude-sonnet-5-thinking-high",
    [int]$MaxIterations = 0,      # 0 = unlimited, stop only on RALPH_STATUS
    [int]$SleepSeconds = 3,
    [int]$MaxConsecutiveFailures = 3,
    [string]$Executor = "cursor"   # shipped adapter is Cursor CLI; other CLIs replace
                                     # Invoke-Executor (see SKILL.md "Executor backends")
)

$ErrorActionPreference = "Continue"
$RalphDir = $PSScriptRoot
if (Test-Path (Join-Path $RalphDir "PROMPT.md")) {
    # scripts/ copied alongside the project files (typical scaffolded layout)
} else {
    # scripts/ still inside the skill folder - assume caller cd'd into their project
    $RalphDir = Get-Location
}
Set-Location $RalphDir

function Invoke-Executor([string]$PromptText, [string]$LogFile) {
    switch ($Executor) {
        "cursor" {
            agent -p --force --trust --model $Model --output-format text $PromptText 2>&1 |
                Tee-Object -FilePath $LogFile
            return $LASTEXITCODE
        }
        default {
            Write-Error "Unknown or unverified executor '$Executor'. Edit this function to wire it in - see SKILL.md 'Executor backends'."
            return 1
        }
    }
}

if (-not (Get-Command agent -ErrorAction SilentlyContinue) -and $Executor -eq "cursor") {
    Write-Error "Cursor CLI 'agent' not found in PATH. Install: irm 'https://cursor.com/install?win32=true' | iex"
    exit 1
}

if (-not (Test-Path (Join-Path $RalphDir ".git"))) {
    git init | Out-Null
    Get-ChildItem $RalphDir -File | Where-Object { $_.Name -ne ".env" } | ForEach-Object { git add $_.Name }
    git commit -m "ralph: init harness" --quiet | Out-Null
    Write-Host "Initialized git repo in $RalphDir (for iteration audit trail)."
}

New-Item -ItemType Directory -Force -Path (Join-Path $RalphDir "logs") | Out-Null

$iteration = 0
$consecutiveFailures = 0

while ($true) {
    if ($MaxIterations -gt 0 -and $iteration -ge $MaxIterations) {
        Write-Host "Reached iteration limit ($MaxIterations). Stopping." -ForegroundColor Yellow
        break
    }
    $iteration++

    $ts = Get-Date -Format o
    Write-Host "`n=== Ralph iteration $iteration | executor=$Executor model=$Model | $ts ===" -ForegroundColor Cyan

    $prompt = Get-Content -Raw -Path (Join-Path $RalphDir "PROMPT.md")
    $logFile = Join-Path $RalphDir "logs\iteration_$($iteration.ToString('000')).log"

    $exitCode = Invoke-Executor -PromptText $prompt -LogFile $logFile

    if ($exitCode -ne 0) {
        $consecutiveFailures++
        Write-Host "Executor exited with code $exitCode (failure $consecutiveFailures of $MaxConsecutiveFailures in a row)." -ForegroundColor Red
        if ($consecutiveFailures -ge $MaxConsecutiveFailures) {
            Write-Host "Too many consecutive executor failures. Stopping loop - check executor auth/setup." -ForegroundColor Red
            break
        }
        Start-Sleep -Seconds $SleepSeconds
        continue
    }
    $consecutiveFailures = 0

    $lastStatusLine = Select-String -Path (Join-Path $RalphDir "PROGRESS.md") -Pattern '^RALPH_STATUS:' -ErrorAction SilentlyContinue |
        Select-Object -Last 1

    if ($lastStatusLine) {
        Write-Host $lastStatusLine.Line -ForegroundColor Yellow
    } else {
        Write-Host "Warning: executor did not append RALPH_STATUS to PROGRESS.md this iteration." -ForegroundColor Red
    }

    git add -A
    git commit -m "ralph: iteration $iteration ($ts)" --quiet | Out-Null

    if ($lastStatusLine -and $lastStatusLine.Line -match 'RALPH_STATUS:\s*(BLOCKED|DONE)') {
        Write-Host "Loop stopped: $($Matches[1])" -ForegroundColor Red
        break
    }

    Start-Sleep -Seconds $SleepSeconds
}

Write-Host "`nRalph loop finished after $iteration iteration(s). See PROGRESS.md and logs\." -ForegroundColor Cyan
