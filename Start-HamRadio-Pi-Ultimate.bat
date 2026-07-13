@echo off
setlocal
cd /d "%~dp0"
set "QT_QUICK_CONTROLS_STYLE=Basic"
set "QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu"

where pyw >nul 2>&1
if %errorlevel%==0 (
    start "" pyw -3 "%~dp0src\app.py"
    exit /b 0
)

where pythonw >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw "%~dp0src\app.py"
    exit /b 0
)

python "%~dp0src\app.py"
