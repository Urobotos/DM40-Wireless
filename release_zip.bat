@echo off
cd /d "%~dp0"
setlocal

if not exist "dist\DM40 Wireless\DM40 Wireless.exe" (
    echo Nejdriv spust build_exe.bat
    pause
    exit /b 1
)

if not exist release mkdir release

set "OUT=release\DM40-Wireless-win64.zip"
if exist "%OUT%" del /F /Q "%OUT%"

powershell -NoProfile -Command "Compress-Archive -Path 'dist\DM40 Wireless\*' -DestinationPath '%OUT%' -Force"
if errorlevel 1 (
    echo Zip se nepodaril.
    pause
    exit /b 1
)

echo.
echo Hotovo: %OUT%
echo Nahraj tento soubor jako GitHub Release asset.
pause
