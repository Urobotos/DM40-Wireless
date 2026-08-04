@echo off
cd /d "%~dp0"
echo ============================================
echo  DM40 Wireless - Nuitka + MSVC Build
echo ============================================
echo.

REM --- Validate virtual environment ---
if not exist .venv\Scripts\python.exe (
    echo [ERROR] Virtual environment not found. Run install.bat first.
    pause
    exit /b 1
)

set "PY=.venv\Scripts\python.exe"

REM --- Kill running instance (avoids file-lock errors) ---
taskkill /IM "DM40 Wireless.exe" /F >nul 2>&1
timeout /t 1 /nobreak >nul

REM --- Ensure Nuitka is installed ---
echo [1/4] Checking Nuitka installation...
"%PY%" -m pip install --upgrade nuitka >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install Nuitka.
    pause
    exit /b 1
)

REM --- Auto-detect and activate MSVC compiler toolchain ---
echo [2/4] Activating MSVC compiler...
set "MSVC_VARS="

REM Priority 1: vswhere.exe (VS installer tool)
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if exist "%VSWHERE%" (
    for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -property installationPath 2^>nul`) do (
        if exist "%%i\VC\Auxiliary\Build\vcvars64.bat" (
            set "MSVC_VARS=%%i\VC\Auxiliary\Build\vcvars64.bat"
        )
    )
)

REM Priority 2: scan common VS install directories
if not defined MSVC_VARS (
    for %%e in (Professional Community Enterprise BuildTools) do (
        for %%y in (2026 2025 2022) do (
            if exist "D:\Software\Microsoft Visual Studio\%%y\%%e\VC\Auxiliary\Build\vcvars64.bat" (
                set "MSVC_VARS=D:\Software\Microsoft Visual Studio\%%y\%%e\VC\Auxiliary\Build\vcvars64.bat"
            )
        )
    )
)

REM Priority 3: default Program Files installs
if not defined MSVC_VARS (
    for %%e in (Professional Community Enterprise BuildTools) do (
        for %%y in (2026 2025 2022) do (
            if exist "%ProgramFiles%\Microsoft Visual Studio\%%y\%%e\VC\Auxiliary\Build\vcvars64.bat" (
                set "MSVC_VARS=%ProgramFiles%\Microsoft Visual Studio\%%y\%%e\VC\Auxiliary\Build\vcvars64.bat"
            )
        )
    )
)

if not defined MSVC_VARS (
    echo [ERROR] MSVC vcvars64.bat not found.
    echo   Install Visual Studio 2022+ with "Desktop development with C++" workload.
    echo   If VS is installed in a custom path, set MSVC_VARS manually in this script.
    pause
    exit /b 1
)

echo   Found: %MSVC_VARS%
call "%MSVC_VARS%"
if errorlevel 1 (
    echo [ERROR] MSVC environment setup failed.
    pause
    exit /b 1
)

REM --- Nuitka build (standalone folder; avoids onefile AV false positives) ---
echo [3/4] Building with Nuitka --standalone...
if exist "dist\app.dist" rmdir /S /Q "dist\app.dist"
if exist "dist\DM40 Wireless" rmdir /S /Q "dist\DM40 Wireless"

"%PY%" -m nuitka ^
  --standalone ^
  --windows-console-mode=disable ^
  --windows-icon-from-ico=images/app.ico ^
  --enable-plugin=tk-inter ^
  --include-data-dir=images=images ^
  --include-data-files=i18n/en-US.toml=i18n/en-US.toml ^
  --include-package=bleak ^
  --include-package=winrt ^
  --output-dir=dist ^
  --output-filename="DM40 Wireless.exe" ^
  --assume-yes-for-downloads ^
  --remove-output ^
  --msvc=latest ^
  app.pyw

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

REM --- Verify output and prepare distribution folder ---
echo [4/4] Verifying output and copying external assets...
if not exist "dist\app.dist\DM40 Wireless.exe" (
    echo [ERROR] Output exe not found in dist\app.dist\
    pause
    exit /b 1
)

REM Rename Nuitka default folder to a clear distribution name
move /Y "dist\app.dist" "dist\DM40 Wireless" >nul
if errorlevel 1 (
    echo [ERROR] Failed to rename dist\app.dist to dist\DM40 Wireless
    pause
    exit /b 1
)

REM Copy i18n language files next to the exe (external, editable)
if exist "i18n" (
    if not exist "dist\DM40 Wireless\i18n" mkdir "dist\DM40 Wireless\i18n"
    xcopy /Y /E "i18n\*.toml" "dist\DM40 Wireless\i18n\" >nul 2>&1
    echo   i18n\ copied to dist\DM40 Wireless\i18n\
)

REM Copy settings template as default config
if not exist "dist\DM40 Wireless\settings.json" (
    copy /Y "settings.example.json" "dist\DM40 Wireless\settings.json" >nul 2>&1
    echo   settings.example.json copied to dist\DM40 Wireless\settings.json
)

echo.
echo ============================================
echo  Build succeeded
echo  Output folder: dist\DM40 Wireless\
echo.
echo  Distribution folder contents:
echo    dist\DM40 Wireless\DM40 Wireless.exe
echo    dist\DM40 Wireless\           (runtime DLLs / bundled data)
echo    dist\DM40 Wireless\i18n\      (language files)
echo    dist\DM40 Wireless\settings.json
echo ============================================
echo.
echo  Note: Keep the whole folder together - do not move the exe alone.
pause
