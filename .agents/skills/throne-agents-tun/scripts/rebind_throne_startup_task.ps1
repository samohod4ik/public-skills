# Requires elevation. Point an existing Highest Throne logon task at
# start_throne_autostart.cmd with a baked Python path, then disable the
# Limited flags task. Do not toggle Throne UI "start with Windows" after
# this; it rewrites the action back to bare Throne.exe.
param(
    [Parameter(Mandatory = $true)][string]$ThroneDir,
    [string]$Python = '',
    [string]$TaskName = 'Throne',
    [string]$FlagsTaskName = 'ThroneAutostartFlags'
)

$ErrorActionPreference = 'Stop'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$role = New-Object Security.Principal.WindowsPrincipal($identity)
if (-not $role.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Run elevated'
}
$ThroneDir = [IO.Path]::GetFullPath($ThroneDir)
$cmd = Join-Path $PSScriptRoot 'start_throne_autostart.cmd'
if (-not (Test-Path -LiteralPath $cmd)) {
    throw "Missing $cmd"
}
if (-not (Test-Path -LiteralPath (Join-Path $ThroneDir 'Throne.exe'))) {
    throw "No Throne.exe under $ThroneDir"
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
$task = Get-ScheduledTask -TaskName $TaskName
$action = New-ScheduledTaskAction -Execute $cmd -Argument ('"{0}" "{1}"' -f $ThroneDir, $Python) -WorkingDirectory $ThroneDir
Set-ScheduledTask -TaskName $TaskName -Action $action -Principal $task.Principal -Trigger $task.Triggers -Settings $task.Settings | Out-Null
$after = Get-ScheduledTask -TaskName $TaskName
if ($after.Principal.RunLevel -ne 'Highest') {
    throw "RunLevel is $($after.Principal.RunLevel), expected Highest"
}
$flags = Get-ScheduledTask -TaskName $FlagsTaskName -ErrorAction SilentlyContinue
if ($null -ne $flags) {
    Disable-ScheduledTask -TaskName $FlagsTaskName | Out-Null
    Write-Output ("FlagsTaskDisabled={0}" -f $FlagsTaskName)
} else {
    Write-Output ("FlagsTaskAbsent={0}" -f $FlagsTaskName)
}
Write-Output ("Execute={0}" -f $after.Actions.Execute)
Write-Output ("Arguments={0}" -f $after.Actions.Arguments)
Write-Output ("RunLevel={0}" -f $after.Principal.RunLevel)
Write-Output ("Python={0}" -f $Python)
