$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
python -m pip install --upgrade PyQt6 PyQt6-WebEngine
python ".\src\app.py"
