<#
.SYNOPSIS
  Local Windows fallback for Happ auto-CONNECT after logon (not the same as --autostart).
.DESCRIPTION
  Official Happ auto-connect is delivered by the subscription provider
  (HTTP headers or #subscription-autoconnect lines). This script does not
  write subscription URLs or invent Preferences registry values.

  What it CAN set locally:
    - A current-user Scheduled Task that waits until Happ.exe is running,
      then soft-nudges happ://connect 30-60s after logon (after --autostart).
    - Inspection of existing HKCU Happ Preference value *names* that already
      look like autoconnect (report only; no invented keys).

  Live-session soft-apply: if Happ is already running and System Proxy is
  already on (ProxyEnable=1) to a Happ-like local listen, do not fire
  immediate happ://connect just to "apply" autoconnect. This script only
  registers the delayed logon nudge; skip immediate connect on a healthy
  live tunnel (avoids remote-session blips). Confirm the nudge after
  reboot or a fresh logon.

  happ://connect is a local protocol nudge (not the vendor header API).
  Prefer lastused (last selected server). Prefer Extra Whitelist2 DE then NL
  when those remarks exist in the user's subscription.

.NOTES
  EN: Never kills Happ; never calls happ://disconnect.
  RU: Никогда не убивает Happ и не вызывает happ://disconnect.
  Official autoconnect: https://www.happ.su/main/dev-docs/app-management
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
  [string] $TaskName = 'Happ Proxy Autoconnect Nudge',
  [ValidateRange(30, 60)]
  [int] $DelaySeconds = 45,
  [switch] $InspectOnly
)

$ErrorActionPreference = 'Stop'

function Write-OfficialAutoconnectGuidance {
  Write-Host @'
--- Happ autoconnect ---
EN: Autostart launches Happ. Autoconnect brings the tunnel up.
    OFFICIAL (subscription provider; do not commit URLs). Prefer lastused:
      HTTP headers:
        subscription-autoconnect: 1
        subscription-autoconnect-type: lastused
      or subscription body:
        #subscription-autoconnect: 1
        #subscription-autoconnect-type: lastused
    Types: lastused | lowestdelay | random
    Source: https://www.happ.su/main/dev-docs/app-management
    Local UI: if this Happ build shows Settings auto-connect /
    Автоподключение, enable it. No public registry value is documented.
    LOCAL NUDGE (this script): delayed happ://connect after Happ.exe.
    Live session already healthy (ProxyEnable + Happ-like local proxy):
    do not fire immediate happ://connect; only ensure this logon task.
    lastused = last selected server. Prefer Extra Whitelist2 DE then NL
    when those remarks exist.

RU: Автозапуск только открывает Happ. Автоподключение поднимает туннель.
    Официально задаёт провайдер подписки (URL в репозиторий не писать).
    Предпочтительно lastused. Локальный тумблер в Settings — если есть.
    Реестровых ключей автоподключения вендор не документирует.
    Локальный nudge: happ://connect после старта Happ.exe.
    Живая сессия уже с System Proxy Happ — не вызывать connect сразу.
    Extra Whitelist2 DE→NL — только если такие remark есть в подписке.
---
'@
}

function Show-ExistingAutoconnectPreferenceNames {
  $root = 'HKCU:\Software\Happ'
  if (-not (Test-Path $root)) {
    Write-Host "NOTE: $root not present (Happ may not have written Preferences yet)."
    return
  }

  $found = 0
  $keys = @($root) + @(Get-ChildItem -Path $root -Recurse -ErrorAction SilentlyContinue | ForEach-Object { $_.PSPath })
  foreach ($key in $keys) {
    $item = Get-Item -LiteralPath $key -ErrorAction SilentlyContinue
    if (-not $item) { continue }
    foreach ($name in $item.GetValueNames()) {
      if ($name -match '(?i)auto[-_]?connect|lastused|autoconnect') {
        $found++
        Write-Host "NOTE: existing Preference name (value redacted): $name @ $($item.Name)"
      }
    }
  }
  if ($found -eq 0) {
    Write-Host 'NOTE: no existing HKCU Happ Preference names matched autoconnect/lastused.'
    Write-Host 'NOTE: not creating invented registry values. Official lastused is provider-only.'
  }
}

function Show-LiveSessionSoftApplyGuidance {
  # Advisory only. Must not throw: this script's job is the delayed task.
  $happUp = [bool](Get-Process Happ -ErrorAction SilentlyContinue)
  $inet = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
  $item = Get-ItemProperty -LiteralPath $inet -ErrorAction SilentlyContinue
  $enabled = $false
  $server = ''
  if ($item) {
    $enabled = ($item.ProxyEnable -as [int]) -eq 1
    $server = [string]$item.ProxyServer
  }
  $looksLocal = $server -match '(?i)(127\.0\.0\.1|localhost):\d+'
  if ($happUp -and $enabled -and $looksLocal) {
    Write-Host 'NOTE: live session looks healthy (Happ running; ProxyEnable=1; Happ-like local proxy).'
    Write-Host 'NOTE: do not fire immediate happ://connect to apply autoconnect; only ensure this delayed logon nudge.'
    return
  }
  if ($happUp -and $enabled) {
    Write-Host 'NOTE: Happ is running and ProxyEnable is on, but ProxyServer is not a local Happ-like listen; not treating as a healthy Happ tunnel.'
    return
  }
  Write-Host 'NOTE: live session does not look like an already-up Happ System Proxy; still only scheduling the logon nudge (no immediate connect).'
}

Write-OfficialAutoconnectGuidance
Show-ExistingAutoconnectPreferenceNames
Show-LiveSessionSoftApplyGuidance

if ($InspectOnly) {
  Write-Host 'OK: inspect-only (no Scheduled Task change).'
  return
}

# Wait until Happ.exe exists, then soft-connect. Never Stop-Process / disconnect.
$nudgeScript = @'
$deadline = (Get-Date).AddSeconds(90)
do {
  if (Get-Process Happ -ErrorAction SilentlyContinue) { break }
  Start-Sleep -Seconds 2
} while ((Get-Date) -lt $deadline)
if (Get-Process Happ -ErrorAction SilentlyContinue) {
  try { Start-Process "happ://connect" } catch { Write-Error $_ }
}
'@
$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($nudgeScript))
$ps1 = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$action = New-ScheduledTaskAction -Execute $ps1 -Argument "-NoProfile -WindowStyle Hidden -EncodedCommand $encoded"
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$trigger.Delay = 'PT{0}S' -f $DelaySeconds
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable `
  -MultipleInstances IgnoreNew

if ($PSCmdlet.ShouldProcess($TaskName, "Register delayed happ://connect (+${DelaySeconds}s after logon, after Happ.exe)")) {
  Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
  Write-Host "OK: Scheduled Task '$TaskName' → wait for Happ.exe then happ://connect after ${DelaySeconds}s (soft; does not kill Happ)"
}
