@echo off
cd /d "%~dp0"
setlocal

REM --- Validate build output ---
if not exist "dist\DM40 Wireless.exe" (
    echo [ERROR] Run build_exe.bat first.
    pause
    exit /b 1
)

REM --- Prepare staging directory ---
set "STAGE=release_staging"
if exist "%STAGE%" rmdir /S /Q "%STAGE%"
mkdir "%STAGE%"

echo [1/3] Copying executable...
copy /Y "dist\DM40 Wireless.exe" "%STAGE%\" >nul

echo [2/3] Copying i18n language files...
if exist "i18n" (
    mkdir "%STAGE%\i18n"
    xcopy /Y /E "i18n\*.toml" "%STAGE%\i18n\" >nul
)

echo [3/3] Copying settings template...
copy /Y "settings.example.json" "%STAGE%\settings.json" >nul

REM --- Create ZIP archive ---
if not exist release mkdir release
set "OUT=release\DM40-Wireless-win64.zip"
if exist "%OUT%" del /F /Q "%OUT%"

echo Creating archive...
powershell -NoProfile -Command ^
  "Compress-Archive -Path '%STAGE%\*' -DestinationPath '%OUT%' -Force"
if errorlevel 1 (
    echo [ERROR] Zip failed.
    rmdir /S /Q "%STAGE%"
    pause
    exit /b 1
)

REM --- Cleanup ---
rmdir /S /Q "%STAGE%"

echo.
echo ============================================
echo  Release ready: %OUT%
echo  Archive contents:
echo    DM40 Wireless.exe
echo    i18n\
echo    settings.json
echo ============================================
pause
