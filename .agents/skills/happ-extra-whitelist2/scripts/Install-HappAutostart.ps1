<#
.SYNOPSIS
  Ensure a current-user Scheduled Task starts Happ with --autostart at logon.
.DESCRIPTION
  Autostart ≠ autoconnect. --autostart only launches Happ (often minimized).
  It does not by itself bring the VPN/TUN up.

  By default this script also registers the delayed happ://connect nudge
  via Set-HappAutoconnect.ps1 (30-60s after logon, after Happ.exe). Pass
  -SkipAutoconnectNudge to install launch-only.

.NOTES
  EN: Discovers Happ.exe; does not assume a single install path.
  RU: Ищет Happ.exe; один фиксированный путь не обязателен.
  Never kills Happ; never calls happ://disconnect.
  Do not run this when Throne Agents only is the primary tunnel (no second System Proxy).
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
  [string] $TaskName = 'Happ Proxy Autostart',
  [string] $HappExe = '',
  [switch] $SkipAutoconnectNudge,
  [ValidateRange(30, 60)]
  [int] $AutoconnectDelaySeconds = 45
)

$ErrorActionPreference = 'Stop'

if (-not $HappExe) {
  $candidates = @(
    (Join-Path ${env:ProgramFiles} 'FlyFrogLLC\Happ\Happ.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'FlyFrogLLC\Happ\Happ.exe')
  )
  $HappExe = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}

if (-not $HappExe -or -not (Test-Path $HappExe)) {
  throw "Happ.exe not found. Pass -HappExe with the discovered path (common vendor locations vary)."
}

$action = New-ScheduledTaskAction -Execute $HappExe -Argument '--autostart'
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

if ($PSCmdlet.ShouldProcess($TaskName, "Register task → $HappExe --autostart")) {
  Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
  Write-Host "OK: Scheduled Task '$TaskName' → $HappExe --autostart (launch only; not VPN connect)"
}

if (-not $SkipAutoconnectNudge) {
  $nudge = Join-Path $PSScriptRoot 'Set-HappAutoconnect.ps1'
  if (-not (Test-Path $nudge)) {
    throw "Missing $nudge (autoconnect nudge). Re-clone the repo or pass -SkipAutoconnectNudge."
  }
  $child = @{ DelaySeconds = $AutoconnectDelaySeconds }
  if ($WhatIfPreference) { $child['WhatIf'] = $true }
  if ($WhatIfPreference -or $PSCmdlet.ShouldProcess('Happ Proxy Autoconnect Nudge', 'Register delayed happ://connect after Happ.exe')) {
    & $nudge @child
  }
}
