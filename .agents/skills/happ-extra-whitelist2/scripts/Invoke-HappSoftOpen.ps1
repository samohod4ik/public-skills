<#
.SYNOPSIS
  Soft-nudge Happ via happ://open (no disconnect/kill).
.DESCRIPTION
  Opens / focuses Happ. Does not connect the tunnel. For auto-CONNECT after
  the process is up, use Invoke-HappSoftConnect.ps1 (happ://connect).

  EN: Never kill Happ. RU: Не убивать Happ; не вызывать happ://disconnect.
#>
[CmdletBinding()]
param()
Start-Process 'happ://open'
Write-Host 'OK: started happ://open'
