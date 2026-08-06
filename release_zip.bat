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
echo %CYAN%║%RST%                 %WHITE%DM40 Wireless - Creating a release zip%RST%                 %CYAN%║%RST%
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

REM --- Validate build output (Nuitka --standalone folder) ---
if not exist "dist\DM40 Wireless\DM40 Wireless.exe" (
    echo %ERROR% Run build_exe.bat first.
    echo   Expected: dist\DM40 Wireless\DM40 Wireless.exe
    pause
    exit /b 1
)

REM --- Ensure external assets exist in the dist folder ---
echo %STEP%[1/2]%RST% %WHITE%Checking i18n\ and settings.json in dist folder...%RST%
echo.

if not exist "dist\DM40 Wireless\i18n" (
	mkdir "dist\DM40 Wireless\i18n"
    xcopy /Y /E "i18n\*.toml" "dist\DM40 Wireless\i18n\" >nul
	echo %INFO% .toml files was copied to the directory: dist\DM40 Wireless\i18n
)
if not exist "dist\DM40 Wireless\settings.json" (
    copy /Y "settings.example.json" "dist\DM40 Wireless\settings.json" >nul
	echo %INFO% settings.json was created in path: dist\DM40 Wireless\
)

echo %SUCCESS% Checking done.

REM --- Create ZIP archive (folder at zip root) ---
if not exist release mkdir release
set "OUT=release\DM40-Wireless-win64.zip"
if exist "%OUT%" del /F /Q "%OUT%"

echo.
echo %STEP%[2/2]%RST% %WHITE%Creating archive...%RST%

if not exist "tools\7-Zip\7za.exe" (
    echo.
    echo %ERROR% tools\7-Zip\7za.exe not found.
    pause
    exit /b 1
)

pushd dist
..\tools\7-Zip\7za.exe a -tzip -bso0 -bsp1 "..\%OUT%" "DM40 Wireless\"
if errorlevel 1 (
    popd
    echo.
    echo %ERROR% Zip failed.
    pause
    exit /b 1
)
popd

echo.
echo %SUCCESS% Archive created.

echo.
echo %CYAN%╔════════════════════════════════════════════════════════════════════════╗%RST%
echo %CYAN%║%RST%               %GREEN%Creating a release zip was successful! %RST%                  %CYAN%║%RST%
echo %CYAN%╟————————————————————————————————————————————————————————————————————————╢%RST%
echo %CYAN%║%RST% %WHITE%Release ready:%RST% %OUT%                         %CYAN%║%RST%
echo %CYAN%║                                                                        %CYAN%║%RST%
echo %CYAN%║%RST% %WHITE%Archive contents:%RST%                                                      %CYAN%║%RST%
echo %CYAN%║%RST%   DM40 Wireless\                                                       %CYAN%║%RST%
echo %CYAN%║%RST%   ├── i18n\                                                            %CYAN%║%RST%
echo %CYAN%║%RST%   ├── settings.json                                                    %CYAN%║%RST%
echo %CYAN%║%RST%   └── *.dll  (runtime DLLs and bundled data)                           %CYAN%║%RST%
echo %CYAN%║                                                                        %CYAN%║%RST%
echo %CYAN%╚════════════════════════════════════════════════════════════════════════╝%RST%
echo.
echo %NOTE% Users must extract the whole folder and keep files together.
pause