<#
.SYNOPSIS
  Read-only: print activeRoutingName, useRouting, and routing profile names.
.NOTES
  Never prints subscription URLs. Does not kill Happ.
  EN: Routing names only — not Extra Whitelist2 server remarks (those live in the subscription).
  RU: Только имена профилей маршрутизации; remark серверов не читаются.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$path = Join-Path $env:LOCALAPPDATA 'Happ\routing.json'
if (-not (Test-Path $path)) {
  Write-Host "missing: $path"
  exit 1
}

$j = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
Write-Host "activeRoutingName=$($j.activeRoutingName)"
Write-Host "useRouting=$($j.useRouting)"
$names = @($j.routings | ForEach-Object { $_.name })
Write-Host ("routings=" + ($names -join ', '))
if ($null -ne $j.routingNames) {
  $rn = @($j.routingNames)
  Write-Host ("routingNames=" + ($rn -join ', '))
}
