@echo off
cd /d "%~dp0"
echo Building DM40 Wireless (PyInstaller)...
echo.

if not exist .venv\Scripts\python.exe (
    echo Virtual environment not found. Run install.bat first.
    pause
    exit /b 1
)

set "PY=.venv\Scripts\python.exe"

REM Close running app — otherwise build\ or dist\ may be locked (WinError 5)
taskkill /IM "DM40 Wireless.exe" /F >nul 2>&1
timeout /t 1 /nobreak >nul

"%PY%" -m pip install --upgrade pyinstaller
if errorlevel 1 exit /b 1

REM --onedir: spolehlivejsi pro Bleak/BLE nez --onefile (doporuceno)
"%PY%" -m PyInstaller --noconfirm --clean ^
  --name "DM40 Wireless" ^
  --windowed ^
  --onedir ^
  --add-data "images;images" ^
  --collect-all bleak ^
  app.pyw

if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

if not exist "dist\DM40 Wireless\settings.json" (
  copy /Y settings.example.json "dist\DM40 Wireless\settings.json" >nul 2>&1
)

REM Copy i18n language files for distribution
if exist "i18n" (
  if not exist "dist\DM40 Wireless\i18n" mkdir "dist\DM40 Wireless\i18n"
  xcopy /Y /E "i18n\*.toml" "dist\DM40 Wireless\i18n\" >nul 2>&1
)

echo.
echo Done: dist\DM40 Wireless\DM40 Wireless.exe
echo Copy the whole folder "dist\DM40 Wireless" for distribution.
pause
