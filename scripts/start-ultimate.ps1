$ProjectRoot = Split-Path -Parent $PSScriptRoot
$env:QT_QUICK_CONTROLS_STYLE = "Basic"
python "$ProjectRoot\src\app.py"
