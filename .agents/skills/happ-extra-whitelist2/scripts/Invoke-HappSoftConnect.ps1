<#
.SYNOPSIS
  Soft-nudge Happ via happ://connect (no disconnect/kill).
.DESCRIPTION
  Local protocol nudge (not the official subscription-autoconnect header).
  Use when Happ is already running (or starting) but the TUN / System Proxy
  tunnel is down. Calling this when the tunnel is already healthy / already
  up is optional and usually should be skipped (can blip remote sessions).

  Default skip is a WinINET heuristic only (Happ running + ProxyEnable=1 +
  Happ-like local ProxyServer). It is not a TUN probe. Pass -Force if the
  operator already sees the tunnel down. Registry-read failures fail open
  and still fire happ://connect. Never call happ://disconnect.

  EN: Connect only. Skip when System Proxy already looks up unless -Force.
  RU: Только подключить. Пропуск если System Proxy уже похож на Happ, кроме -Force.
#>
[CmdletBinding()]
param(
  [switch] $Force
)

function Test-HappLikeSystemProxyUp {
  $happUp = [bool](Get-Process Happ -ErrorAction SilentlyContinue)
  if (-not $happUp) { return $false }
  $inet = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
  $item = Get-ItemProperty -LiteralPath $inet -ErrorAction SilentlyContinue
  if (-not $item) { return $false }
  $enabled = ($item.ProxyEnable -as [int]) -eq 1
  $server = [string]$item.ProxyServer
  $looksLocal = $server -match '(?i)(127\.0\.0\.1|localhost):\d+'
  return ($enabled -and $looksLocal)
}

if (-not $Force -and (Test-HappLikeSystemProxyUp)) {
  Write-Host 'NOTE: tunnel already looks healthy (Happ running; ProxyEnable=1; Happ-like local proxy).'
  Write-Host 'NOTE: happ://connect is optional when already up; skipping to avoid a live-session blip.'
  Write-Host 'NOTE: this skip is WinINET-only (not a TUN check). Re-run with -Force if the tunnel is actually down.'
  Write-Host 'OK: skipped happ://connect (already healthy; never disconnect/kill)'
  return
}

if ($Force) {
  Write-Host 'NOTE: -Force: firing happ://connect even if System Proxy already looks up.'
}

Start-Process 'happ://connect'
Write-Host 'OK: started happ://connect'
