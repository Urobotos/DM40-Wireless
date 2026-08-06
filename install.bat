@echo off
chcp 65001 >nul
setlocal EnableExtensions

REM --- ANSI colors ---
for /F %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"

set "RST=%ESC%[0m"
set "RED=%ESC%[91m"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "ORANGE=%ESC%[33m"
set "BLUE=%ESC%[94m"
set "CYAN=%ESC%[96m"
set "WHITE=%ESC%[97m"
set "GRAY=%ESC%[90m"

REM --- Message tags ---
set "STEP=%CYAN%"
set "SUCCESS=%GREEN%[SUCCESS]%RST%"
set "ERROR=%RED%[ERROR]%RST%"
set "WARNING=%ORANGE%[WARNING]%RST%"
set "NOTE=%YELLOW%[NOTE]%RST%"
set "INFO=%GRAY%[INFO]%RST%"
set "SKIP=%GRAY%[SKIP]%RST%"

cd /d "%~dp0"

echo %CYAN%╔════════════════════════════════════════════════════════════════════════╗%RST%
echo %CYAN%║%RST%                     %WHITE%DM40 Wireless - Installation%RST%                       %CYAN%║%RST%
echo %CYAN%║%RST%                   %GRAY%Bluetooth Multimeter Desktop App%RST%                     %CYAN%║%RST%
echo %CYAN%╚════════════════════════════════════════════════════════════════════════╝%RST%
echo.

echo %CYAN%██████╗ ███╗   ███╗██╗  ██╗ ██████╗%RST%
echo %CYAN%██╔══██╗████╗ ████║██║  ██║██╔═████╗%RST%
echo %CYAN%██║  ██║██╔████╔██║███████║██║██╔██║%RST%
echo %CYAN%██║  ██║██║╚██╔╝██║╚════██║████╔╝██║%RST%
echo %CYAN%██████╔╝██║ ╚═╝ ██║     ██║╚██████╔╝%RST%
echo %CYAN%╚═════╝ ╚═╝     ╚═╝     ╚═╝ ╚═════╝ %RST%
echo.
echo %BLUE%██╗    ██╗██╗██████╗ ███████╗██╗     ███████╗███████╗███████╗%RST%
echo %BLUE%██║    ██║██║██╔══██╗██╔════╝██║     ██╔════╝██╔════╝██╔════╝%RST%
echo %BLUE%██║ █╗ ██║██║██████╔╝█████╗  ██║     █████╗  ███████╗███████╗%RST%
echo %BLUE%██║███╗██║██║██╔══██╗██╔══╝  ██║     ██╔══╝  ╚════██║╚════██║%RST%
echo %BLUE%╚███╔███╔╝██║██║  ██║███████╗███████╗███████╗███████║███████║%RST%
echo %BLUE% ╚══╝╚══╝ ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝╚══════╝%RST%
echo.

echo %STEP%[1/2]%RST% %WHITE%Installing dependencies...%RST%
echo.
where python >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Python is not in PATH. Install Python 3.11+ from https://www.python.org/
    echo Check "Add python to PATH" during installation.
    pause
    exit /b 1
)

if not exist .venv\Scripts\python.exe (
    echo %INFO% Creating virtual environment .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo %ERROR% Failed to create venv.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo %ERROR% Package install failed.
    pause
    exit /b 1
)

echo.
echo %SUCCESS% Dependencies installed.
echo.

REM --- Install Nuitka for building ---
echo %STEP%[2/2]%RST% %WHITE%Installing Nuitka (for build_exe.bat)...%RST%
echo.

python -c "import nuitka" >nul 2>&1
if errorlevel 1 (
    python -m pip install nuitka
    if errorlevel 1 (
        echo %ERROR% Nuitka install failed. Build will not be available.
        pause
        exit /b 1
    )
    echo %SUCCESS% Nuitka installed.
) else (
    echo %SKIP% Nuitka is already installed.
)

echo.
echo %CYAN%╔════════════════════════════════════════════════════════════════════════╗%RST%
echo %CYAN%║%RST%                      %GREEN%Installation was successful! %RST%                     %CYAN%║%RST%
echo %CYAN%╟————————————————————————————————————————————————————————————————————————╢%RST%
echo %CYAN%║%RST%                                                                        %CYAN%║%RST%
echo %CYAN%║%RST% %WHITE%◦ For development, launch:%RST% %YELLOW%DM40 Wireless.bat%RST%                           %CYAN%║%RST%
echo %CYAN%║%RST% %WHITE%◦ To build, run:%RST% %YELLOW%build_exe.bat%RST%                                         %CYAN%║%RST%
echo %CYAN%║%RST%                                                                        %CYAN%║%RST%
echo %CYAN%╚════════════════════════════════════════════════════════════════════════╝%RST%
echo.
pause
