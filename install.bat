@echo off
cd /d "%~dp0"
echo DM40 Wireless - install dependencies
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo Python is not in PATH. Install Python 3.11+ from https://www.python.org/
    echo Check "Add python to PATH" during installation.
    pause
    exit /b 1
)

if not exist .venv\Scripts\python.exe (
    echo Creating virtual environment .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create venv.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Package install failed.
    pause
    exit /b 1
)

echo.
echo Done. Launch "DM40 Wireless.bat"
pause
