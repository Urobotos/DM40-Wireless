@echo off
cd /d "%~dp0"
echo Building DM40 Wireless (PyInstaller)...
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo Python not found in PATH.
    pause
    exit /b 1
)

python -m pip install --upgrade pyinstaller
if errorlevel 1 exit /b 1

REM --onedir: spolehlivejsi pro Bleak/BLE nez --onefile (doporuceno)
python -m PyInstaller --noconfirm --clean ^
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

echo.
echo Done: dist\DM40 Wireless\DM40 Wireless.exe
echo Copy the whole folder "dist\DM40 Wireless" for distribution.
pause
