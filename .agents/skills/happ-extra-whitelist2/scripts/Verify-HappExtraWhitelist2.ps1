<#
.SYNOPSIS
  Smoke-verify Happ Extra Whitelist2 setup without printing secrets.
.DESCRIPTION
  Checks process, subscription-refresh registry, autostart task, delayed
  autoconnect nudge task, and routing.json. Does not assume Extra Whitelist2
  DE/NL remarks exist (those are UI-side when present). Never prints URLs.

  Pass -SkipAutoconnectCheck when Install-HappAutostart.ps1 was run with
  -SkipAutoconnectNudge.
#>
[CmdletBinding()]
param(
  [int] $ExpectedMinutes = 60,
  [string] $TaskName = 'Happ Proxy Autostart',
  [string] $AutoconnectTaskName = 'Happ Proxy Autoconnect Nudge',
  [switch] $SkipAutoconnectCheck
)

$ErrorActionPreference = 'Continue'
$fail = 0
function Ok($m) { Write-Host "PASS $m" }
function Bad($m) { Write-Host "FAIL $m"; $script:fail++ }

$proc = Get-Process Happ -ErrorAction SilentlyContinue
if ($proc) { Ok "Happ process running (pid $($proc.Id -join ','))" } else { Bad 'Happ process not running' }

$reg = 'HKCU:\Software\Happ\OrganizationDefaults\Preferences\Subscriptions'
if (Test-Path $reg) {
  $p = Get-ItemProperty $reg
  $mins = $p.subsUpdateTimerInMinutes
  if (-not $mins) { $mins = $p.subsAutoUpdateInterval }
  if ("$mins" -eq "$ExpectedMinutes") { Ok "subs interval = $ExpectedMinutes" } else { Bad "subs interval='$mins' expected $ExpectedMinutes" }
  if ("$($p.subsAutoUpdate)".ToLower() -eq 'true') { Ok 'subsAutoUpdate=true' } else { Bad "subsAutoUpdate=$($p.subsAutoUpdate)" }
} else { Bad "registry missing: $reg" }

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($task) { Ok "autostart task '$TaskName' present (launch only)" } else { Bad "autostart task '$TaskName' missing" }

if ($SkipAutoconnectCheck) {
  Ok "autoconnect nudge check skipped (-SkipAutoconnectCheck)"
} else {
  $ac = Get-ScheduledTask -TaskName $AutoconnectTaskName -ErrorAction SilentlyContinue
  if ($ac) { Ok "autoconnect nudge task '$AutoconnectTaskName' present (happ://connect)" } else { Bad "autoconnect nudge task '$AutoconnectTaskName' missing" }
}

$rj = Join-Path $env:LOCALAPPDATA 'Happ\routing.json'
if (Test-Path $rj) {
  $j = Get-Content $rj -Raw -Encoding UTF8 | ConvertFrom-Json
  if ($j.useRouting -eq $true) { Ok "useRouting=true active=$($j.activeRoutingName)" } else { Bad "useRouting=$($j.useRouting)" }
  $names = @($j.routings | ForEach-Object { $_.name })
  Ok ("routing profiles: " + ($(if ($names.Count) { $names -join ', ' } else { '(none)' })))
} else { Bad 'routing.json missing' }

Write-Host 'NOTE: Extra Whitelist2 DE/NL is a preference when those remarks exist; this script does not read encrypted subs.db.'
Write-Host 'NOTE: autostart ≠ autoconnect. If Happ is up but TUN/proxy is down, soft happ://connect — do not kill Happ.'
Write-Host 'NOTE: do not enable Throne System Proxy beside Happ System Proxy.'
if ($fail -gt 0) { Write-Host "RESULT: $fail failure(s)"; exit 1 } else { Write-Host 'RESULT: OK'; exit 0 }
