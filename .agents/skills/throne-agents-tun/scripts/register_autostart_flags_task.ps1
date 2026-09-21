# Register a Limited logon task that writes Remember/TUN/Agents-only flags.
# Does not start Throne. Prefer this OR the rebound Highest wrapper, not both.
param(
    [Parameter(Mandatory = $true)][string]$ThroneDir,
    [string]$Python = '',
    [string]$TaskName = 'ThroneAutostartFlags'
)

$ErrorActionPreference = 'Stop'
$ThroneDir = [IO.Path]::GetFullPath($ThroneDir)
$exe = Join-Path $ThroneDir 'Throne.exe'
if (-not (Test-Path -LiteralPath $exe)) {
    throw "No Throne.exe under $ThroneDir"
}
$writer = Join-Path $PSScriptRoot 'write_autostart_flags.cmd'
if (-not (Test-Path -LiteralPath $writer)) {
    throw "Missing $writer"
}
if (-not $Python) {
    $found = Get-Command python.exe -ErrorAction SilentlyContinue |
        Where-Object { $_.Source -notmatch '\\WindowsApps\\' } |
        Select-Object -First 1
    if (-not $found) {
        throw 'python.exe not on PATH (or only WindowsApps stub); pass -Python'
    }
    $Python = $found.Source
}
$Python = [IO.Path]::GetFullPath($Python)
if ($Python -match '\\WindowsApps\\') {
    throw "WindowsApps python stub: $Python; pass -Python"
}
if (-not (Test-Path -LiteralPath $Python)) {
    throw "Missing $Python"
}
$configDir = Join-Path $ThroneDir 'config'
if (-not (Test-Path -LiteralPath $configDir)) {
    New-Item -ItemType Directory -Path $configDir | Out-Null
}
$log = Join-Path $configDir 'autostart-flags.log'
$userId = if ($env:USERDOMAIN) { "$env:USERDOMAIN\$env:USERNAME" } else { $env:USERNAME }
$arg = '"{0}" "{1}" "{2}"' -f $ThroneDir, $Python, $log
$action = New-ScheduledTaskAction -Execute $writer -Argument $arg -WorkingDirectory $ThroneDir
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $userId
$principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 2)
$settings.Priority = 4
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Write-Output "Registered $TaskName (Limited, logon, priority 4)"
Write-Output "Python=$Python"
Write-Output "ThroneDir=$ThroneDir"
Write-Output "Log=$log"
