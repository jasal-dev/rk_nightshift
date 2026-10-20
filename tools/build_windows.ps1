# Exports the Windows build. Needs the Godot 4.7.2 Windows export templates installed.
#   default: builds\windows\Nightshift.exe       (single exe, pck embedded)
#   -Steam:  builds\steam\content\Nightshift.exe + Nightshift.pck (pck separate, so Steam patches stay small)
# Steam upload: fill the IDs in tools\steam\*.vdf, then
#   steamcmd +login <user> +run_app_build <repo>\tools\steam\app_build.vdf +quit
param(
    [switch]$Steam,
    [string]$Godot = "C:\Users\jaakk\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe"
)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if ($Steam) { $Preset = "Windows Steam"; $Out = "builds\steam\content\Nightshift.exe" }
else { $Preset = "Windows Desktop"; $Out = "builds\windows\Nightshift.exe" }
New-Item -ItemType Directory -Force (Split-Path $Out) | Out-Null
& $Godot --headless --path . --import
& $Godot --headless --path . --export-release $Preset $Out
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $Out)) { throw "Export failed" }
Get-ChildItem (Split-Path $Out) | ForEach-Object { "{0} ({1:N1} MB)" -f $_.FullName, ($_.Length / 1MB) }
