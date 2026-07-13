@echo off
setlocal EnableExtensions
title HamRadio-Pi Ultimate Installer
cd /d "%~dp0"

echo.
echo ============================================================
echo          HamRadio-Pi Ultimate 4.4.1 Installer
echo ============================================================
echo.
echo This installer will:
echo   - find Python
echo   - install PyQt6 and PyQt6-WebEngine
echo   - verify Qt and WebEngine
echo   - create Desktop and Start Menu shortcuts
echo   - start HamRadio-Pi Ultimate
echo.
pause

set "PY_CMD="

where py >nul 2>&1
if %errorlevel%==0 set "PY_CMD=py -3"

if not defined PY_CMD (
    where python >nul 2>&1
    if %errorlevel%==0 set "PY_CMD=python"
)

if not defined PY_CMD (
    echo.
    echo Python 3 was not found.
    echo Opening the official Python download page.
    echo During installation, tick "Add Python to PATH".
    start "" "https://www.python.org/downloads/windows/"
    echo.
    pause
    exit /b 1
)

echo.
echo Updating pip...
%PY_CMD% -m pip install --upgrade pip
if errorlevel 1 goto :failed

echo.
echo Installing Qt, QML and WebEngine...
%PY_CMD% -m pip install --upgrade PyQt6 PyQt6-WebEngine
if errorlevel 1 goto :failed

echo.
echo Verifying installation...
%PY_CMD% -c "from PyQt6.QtCore import QT_VERSION_STR; from PyQt6.QtQml import QQmlApplicationEngine; from PyQt6.QtWebEngineQuick import QtWebEngineQuick; print('Qt', QT_VERSION_STR, '- QML OK - WebEngine OK')"
if errorlevel 1 goto :failed

echo.
echo Creating shortcuts...

set "VBS_FILE=%TEMP%\hamradio_pi_shortcuts_%RANDOM%.vbs"

> "%VBS_FILE%" echo Set shell = CreateObject("WScript.Shell")
>>"%VBS_FILE%" echo project = "%~dp0"
>>"%VBS_FILE%" echo target = project ^& "Start-HamRadio-Pi-Ultimate.bat"
>>"%VBS_FILE%" echo iconFile = project ^& "assets\branding\hamradio-pi-256.png"
>>"%VBS_FILE%" echo desktop = shell.SpecialFolders("Desktop")
>>"%VBS_FILE%" echo startMenu = shell.SpecialFolders("Programs")
>>"%VBS_FILE%" echo Set link = shell.CreateShortcut(desktop ^& "\HamRadio-Pi Ultimate.lnk")
>>"%VBS_FILE%" echo link.TargetPath = target
>>"%VBS_FILE%" echo link.WorkingDirectory = project
>>"%VBS_FILE%" echo link.Description = "HamRadio-Pi Ultimate"
>>"%VBS_FILE%" echo link.Save
>>"%VBS_FILE%" echo Set link2 = shell.CreateShortcut(startMenu ^& "\HamRadio-Pi Ultimate.lnk")
>>"%VBS_FILE%" echo link2.TargetPath = target
>>"%VBS_FILE%" echo link2.WorkingDirectory = project
>>"%VBS_FILE%" echo link2.Description = "HamRadio-Pi Ultimate"
>>"%VBS_FILE%" echo link2.Save

cscript //nologo "%VBS_FILE%"
del /q "%VBS_FILE%" >nul 2>&1

echo.
echo Installation complete.
echo Starting HamRadio-Pi Ultimate...
start "" "%~dp0Start-HamRadio-Pi-Ultimate.bat"
exit /b 0

:failed
echo.
echo Installation failed.
echo Please copy the complete text shown in this window.
echo.
pause
exit /b 1
