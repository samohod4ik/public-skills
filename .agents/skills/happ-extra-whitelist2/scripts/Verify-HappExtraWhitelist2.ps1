<#
.SYNOPSIS
  Smoke-verify Happ Extra Whitelist2 setup without printing secrets.
.DESCRIPTION
  Checks process, subscription-refresh registry, autostart task, delayed
  autoconnect nudge task, and routing.json. On HAPP 4.0.5+, requires a manual
  UI confirmation of the active subscription's selected routing profile.
  Does not assume Extra Whitelist2 DE/NL remarks exist. Never prints URLs.

  Pass -SkipAutoconnectCheck when Install-HappAutostart.ps1 was run with
  -SkipAutoconnectNudge. Pass -ConfirmedLegacyHapp only after checking that
  the installed HAPP version is older than 4.0.5.
#>
[CmdletBinding()]
param(
  [int] $ExpectedMinutes = 60,
  [string] $TaskName = 'Happ Proxy Autostart',
  [string] $AutoconnectTaskName = 'Happ Proxy Autoconnect Nudge',
  [switch] $SkipAutoconnectCheck,
  [string] $UiConfirmedRoutingProfile,
  [switch] $ConfirmedLegacyHapp
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
  $j = Get-Content -LiteralPath $rj -Raw -Encoding UTF8 | ConvertFrom-Json
  $names = @($j.routings | ForEach-Object { $_.name })
  Ok ("routing profiles: " + ($(if ($names.Count) { $names -join ', ' } else { '(none)' })))
  $subConfigs = @($j.subConfigs | Where-Object { $null -ne $_ })
  if ($null -ne $j.PSObject.Properties['subConfigs']) {
    if ([string]::IsNullOrWhiteSpace($UiConfirmedRoutingProfile)) {
      Bad 'Active subscription routing unverified. Check Servers > active subscription > Routing, then pass -UiConfirmedRoutingProfile with the selected name.'
    } else {
      $selected = @($subConfigs | Where-Object {
        $_.enabled -eq $true -and $_.selectedProfile -eq $UiConfirmedRoutingProfile
      })
      $matching = @($selected | Where-Object {
        $sub = $_
        @($j.routings | Where-Object {
          $_.subscriptionId -eq $sub.subscriptionId -and $_.name -eq $sub.selectedProfile
        }).Count -gt 0
      })
      if ($matching.Count -gt 0) {
        Ok "UI-confirmed profile '$UiConfirmedRoutingProfile' has an enabled subscription selection and a matching profile"
      } else {
        Bad "UI-confirmed profile '$UiConfirmedRoutingProfile' has no enabled subscription selection with a matching profile"
      }
    }
  } else {
    if (-not $ConfirmedLegacyHapp) {
      Bad 'No subConfigs field. Confirm HAPP is older than 4.0.5 before passing -ConfirmedLegacyHapp; global fields are otherwise inconclusive.'
    } elseif ($j.useRouting -eq $true -and -not [string]::IsNullOrWhiteSpace($j.activeRoutingName) -and $names -contains $j.activeRoutingName) {
      Ok "confirmed legacy useRouting=true active=$($j.activeRoutingName)"
    } else {
      Bad "confirmed legacy routing invalid: useRouting=$($j.useRouting) active=$($j.activeRoutingName)"
    }
  }
} else { Bad 'routing.json missing' }

Write-Host 'NOTE: Extra Whitelist2 DE/NL is a preference when those remarks exist; this script does not read encrypted subs.db.'
Write-Host 'NOTE: routing.json cannot prove which subscription owns the active server; -UiConfirmedRoutingProfile requires an actual UI check.'
Write-Host 'NOTE: autostart ≠ autoconnect. If Happ is up but TUN/proxy is down, soft happ://connect — do not kill Happ.'
Write-Host 'NOTE: do not enable Throne System Proxy beside Happ System Proxy.'
if ($fail -gt 0) { Write-Host "RESULT: $fail failure(s)"; exit 1 } else { Write-Host 'RESULT: OK'; exit 0 }
