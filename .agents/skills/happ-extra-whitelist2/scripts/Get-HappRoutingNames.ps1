<#
.SYNOPSIS
  Read-only: summarize routing profiles and per-subscription selections.
.NOTES
  Never prints subscription URLs. Does not kill Happ.
  HAPP 4.0.5+ stores routing per subscription. This file cannot identify which
  subscription owns the currently connected server. Confirm that in the UI.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$path = Join-Path $env:LOCALAPPDATA 'Happ\routing.json'
if (-not (Test-Path $path)) {
  Write-Host "missing: $path"
  exit 1
}

$j = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
$names = @($j.routings | ForEach-Object { $_.name })
Write-Host ("routings=" + ($names -join ', '))
$subConfigs = @($j.subConfigs | Where-Object { $null -ne $_ })
if ($null -ne $j.PSObject.Properties['subConfigs']) {
  Write-Host 'routingMode=per-subscription'
  Write-Host "subscriptionSlots=$($subConfigs.Count)"
  for ($i = 0; $i -lt $subConfigs.Count; $i++) {
    $sub = $subConfigs[$i]
    $matches = @($j.routings | Where-Object {
      $_.subscriptionId -eq $sub.subscriptionId -and $_.name -eq $sub.selectedProfile
    })
    Write-Host "subscriptionSlot=$($i + 1) enabled=$($sub.enabled) selectedProfile=$($sub.selectedProfile) profilePresent=$($matches.Count -gt 0)"
  }
  Write-Host 'NOTE: slots are not the active subscription. Check Servers > active subscription > Routing in HAPP.'
} else {
  Write-Host 'routingMode=legacy-or-unknown'
  Write-Host "activeRoutingName=$($j.activeRoutingName)"
  Write-Host "useRouting=$($j.useRouting)"
  Write-Host 'NOTE: confirm HAPP is older than 4.0.5 before using these global fields as routing evidence.'
}
