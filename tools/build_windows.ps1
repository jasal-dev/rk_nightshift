# Exports the Windows build to builds/windows/Nightshift.exe (single exe, pck embedded).
# Needs the Godot 4.7.2 Windows export templates installed. Override the editor with -Godot.
param(
    [string]$Godot = "C:\Users\jaakk\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe",
    [string]$Out = "builds\windows\Nightshift.exe"
)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force (Split-Path $Out) | Out-Null
& $Godot --headless --path . --import
& $Godot --headless --path . --export-release "Windows Desktop" $Out
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $Out)) { throw "Export failed" }
$f = Get-Item $Out
"{0} ({1:N1} MB)" -f $f.FullName, ($f.Length / 1MB)
