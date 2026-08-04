@echo off
cd /d "%~dp0"
setlocal

REM --- Validate build output (Nuitka --standalone folder) ---
if not exist "dist\DM40 Wireless\DM40 Wireless.exe" (
    echo [ERROR] Run build_exe.bat first.
    echo   Expected: dist\DM40 Wireless\DM40 Wireless.exe
    pause
    exit /b 1
)

REM --- Ensure external assets exist in the dist folder ---
echo [1/2] Checking i18n and settings in dist folder...
if exist "i18n" (
    if not exist "dist\DM40 Wireless\i18n" mkdir "dist\DM40 Wireless\i18n"
    xcopy /Y /E "i18n\*.toml" "dist\DM40 Wireless\i18n\" >nul
)
if not exist "dist\DM40 Wireless\settings.json" (
    copy /Y "settings.example.json" "dist\DM40 Wireless\settings.json" >nul
)

REM --- Create ZIP archive (folder at zip root) ---
if not exist release mkdir release
set "OUT=release\DM40-Wireless-win64.zip"
if exist "%OUT%" del /F /Q "%OUT%"

echo [2/2] Creating archive...
powershell -NoProfile -Command ^
  "Compress-Archive -Path 'dist\DM40 Wireless' -DestinationPath '%OUT%' -Force"
if errorlevel 1 (
    echo [ERROR] Zip failed.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Release ready: %OUT%
echo  Archive contents:
echo    DM40 Wireless\
echo      DM40 Wireless.exe
echo      (runtime DLLs / bundled data)
echo      i18n\
echo      settings.json
echo ============================================
echo.
echo  Users must extract the whole folder and keep files together.
pause
