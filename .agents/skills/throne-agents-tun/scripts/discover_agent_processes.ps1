#Requires -Version 5.1
<#
.SYNOPSIS
    Read-only discovery of local agent executables for Throne Agents-only TUN.

.DESCRIPTION
    Prints JSON to stdout. Does not edit Throne, TUN, or throne.db.
    Emits process names and paths only. Catalog regexes are unioned later by
    scripts/render_agents_only_rules.py. Skips bare node.exe unless the path is
    cursor-agent\versions\<ver>\node.exe. ChatGPT.exe is path-only under OpenAI.Codex.
    language_server_windows_x64.exe is path-only under extensions\windsurf\bin.
#>
[CmdletBinding()]
param(
    [switch]$InstalledOnly,
    [string]$SnapshotPath
)

$ErrorActionPreference = 'Stop'

function Test-CursorAgentNode {
    param([string]$Path)
    if (-not $Path) { return $false }
    return $Path -match '(?i)[\\/]cursor-agent[\\/]versions[\\/][^\\/]+[\\/]node\.exe$'
}

function Add-Unique {
    param($List, [string]$Value)
    if ($Value -and -not $List.Contains($Value)) {
        [void]$List.Add($Value)
    }
}

function ConvertTo-JsonStringArray {
    param($List)
    $parts = New-Object System.Collections.Generic.List[string]
    foreach ($v in @($List)) {
        if ($null -eq $v -or $v -eq '') { continue }
        [void]$parts.Add(($v | ConvertTo-Json -Compress))
    }
    if ($parts.Count -eq 0) { return '[]' }
    return '[' + ($parts -join ',') + ']'
}

function Add-ClassifiedProcess {
    param([string]$Name, [string]$Path)
    $family = Classify-Path -Name $Name -Path $Path
    if (-not $family) { return }
    $leaf = if ($Path) { Split-Path -Leaf $Path } else { $Name }
    if ($Name -and -not (Test-PathOnlyLeaf $Name) -and -not (Test-PathOnlyLeaf $leaf)) {
        Add-Unique $families[$family].process_names $Name
    }
    if ($Path) {
        Add-Unique $families[$family].process_paths $Path
    }
}

$families = [ordered]@{
    cursor = [ordered]@{ process_names = [System.Collections.Generic.List[string]]::new(); process_paths = [System.Collections.Generic.List[string]]::new(); path_regexes = [System.Collections.Generic.List[string]]::new() }
    claude = [ordered]@{ process_names = [System.Collections.Generic.List[string]]::new(); process_paths = [System.Collections.Generic.List[string]]::new(); path_regexes = [System.Collections.Generic.List[string]]::new() }
    codex  = [ordered]@{ process_names = [System.Collections.Generic.List[string]]::new(); process_paths = [System.Collections.Generic.List[string]]::new(); path_regexes = [System.Collections.Generic.List[string]]::new() }
    devin  = [ordered]@{ process_names = [System.Collections.Generic.List[string]]::new(); process_paths = [System.Collections.Generic.List[string]]::new(); path_regexes = [System.Collections.Generic.List[string]]::new() }
}

function Test-PathOnlyLeaf {
    param([string]$Leaf)
    $lower = $Leaf.ToLowerInvariant()
    return ($lower -eq 'node.exe' -or $lower -eq 'chatgpt.exe' -or $lower -eq 'language_server_windows_x64.exe')
}

function Classify-Path {
    param([string]$Name, [string]$Path)
    if (-not $Path) { return $null }
    $leaf = Split-Path -Leaf $Path
    if ($leaf -ieq 'node.exe') {
        if (Test-CursorAgentNode $Path) { return 'cursor' }
        return $null
    }
    if ($leaf -ieq 'ChatGPT.exe') {
        if ($Path -match '(?i)OpenAI\.Codex') { return 'codex' }
        return $null
    }
    if ($leaf -ieq 'language_server_windows_x64.exe') {
        if ($Path -match '(?i)extensions[\\/]windsurf[\\/]bin[\\/]') { return 'devin' }
        return $null
    }
    if ($Name -ieq 'Cursor.exe' -or $leaf -ieq 'Cursor.exe') { return 'cursor' }
    if ($leaf -ieq 'claude.exe') { return 'claude' }
    if ($Path -match '(?i)WindowsApps[\\/]OpenAI\.Codex' -and $leaf -ieq 'codex.exe') {
        return 'codex'
    }
    if ($leaf -ieq 'codex.exe') { return 'codex' }
    if ($leaf -ieq 'devin.exe') { return 'devin' }
    return $null
}

$probePaths = @(
    (Join-Path $env:LOCALAPPDATA 'Programs\cursor\Cursor.exe'),
    (Join-Path $env:USERPROFILE '.local\bin\claude.exe'),
    (Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps\Claude.exe'),
    (Join-Path $env:LOCALAPPDATA 'Programs\OpenAI\Codex\bin\codex.exe'),
    (Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin\codex.exe'),
    (Join-Path $env:USERPROFILE '.local\bin\devin.exe')
)
Get-PSDrive -PSProvider FileSystem | ForEach-Object {
    if (-not $_.Root) { return }
    $probePaths += @(
        (Join-Path $_.Root 'Devin\Devin.exe'),
        (Join-Path $_.Root 'Devin\resources\app\extensions\windsurf\devin\bin\devin.exe'),
        (Join-Path $_.Root 'Devin\resources\app\extensions\windsurf\bin\language_server_windows_x64.exe')
    )
}

if ($SnapshotPath) {
    $snap = Get-Content -LiteralPath $SnapshotPath -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($proc in @($snap)) {
        Add-ClassifiedProcess -Name ([string]$proc.Name) -Path ([string]$proc.ExecutablePath)
    }
} else {
    foreach ($candidate in $probePaths) {
        if (Test-Path -LiteralPath $candidate) {
            $leaf = Split-Path -Leaf $candidate
            Add-ClassifiedProcess -Name $leaf -Path $candidate
        }
    }

    if (-not $InstalledOnly) {
        $filter = "Name='Cursor.exe' OR Name='Claude.exe' OR Name='claude.exe' OR Name='codex.exe' OR Name='Codex.exe' OR Name='ChatGPT.exe' OR Name='devin.exe' OR Name='Devin.exe' OR Name='node.exe' OR Name='language_server_windows_x64.exe'"
        Get-CimInstance Win32_Process -Filter $filter | ForEach-Object {
            Add-ClassifiedProcess -Name $_.Name -Path $_.ExecutablePath
        }
    }
}

$familyJson = New-Object System.Collections.Generic.List[string]
foreach ($id in @('cursor', 'claude', 'codex', 'devin')) {
    [void]$familyJson.Add(
        ('"{0}":{{"process_names":{1},"process_paths":{2},"path_regexes":{3}}}' -f
            $id,
            (ConvertTo-JsonStringArray $families[$id].process_names),
            (ConvertTo-JsonStringArray $families[$id].process_paths),
            (ConvertTo-JsonStringArray $families[$id].path_regexes))
    )
}
'{{"families":{{{0}}},"skipped_unqualified_node":true}}' -f ($familyJson -join ',')
