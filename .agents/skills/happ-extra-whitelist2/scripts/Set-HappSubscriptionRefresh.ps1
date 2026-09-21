<#
.SYNOPSIS
  Set Happ subscription auto-update interval to 60 minutes (Windows registry).
.NOTES
  Does not print or require subscription URLs. Soft — does not restart or kill Happ.
  EN: Refresh interval only; not autostart and not autoconnect.
  RU: Только интервал обновления подписки; это не автозапуск и не автоподключение.
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
  [int] $Minutes = 60
)

$ErrorActionPreference = 'Stop'
$path = 'HKCU:\Software\Happ\OrganizationDefaults\Preferences\Subscriptions'
if (-not (Test-Path $path)) {
  if ($PSCmdlet.ShouldProcess($path, 'Create registry key')) {
    New-Item -Path $path -Force | Out-Null
  }
}

$values = @{
  subsUpdateTimerInMinutes = [string]$Minutes
  subsAutoUpdateInterval   = [string]$Minutes
  subsAutoUpdate           = 'true'
  subsUpdateOnOpen         = 'true'
}

foreach ($k in $values.Keys) {
  if ($PSCmdlet.ShouldProcess("$path::$k", "Set $($values[$k])")) {
    New-ItemProperty -Path $path -Name $k -Value $values[$k] -PropertyType String -Force | Out-Null
  }
}

Write-Host "OK: Happ subscription refresh set to $Minutes minute(s) (auto-update on)."
