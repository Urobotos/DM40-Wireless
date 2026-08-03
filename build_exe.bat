@echo off
cd /d "%~dp0"
echo ============================================
echo  DM40 Wireless – Nuitka + MSVC Build
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

REM --- Nuitka build ---
echo [3/4] Building with Nuitka --onefile...
"%PY%" -m nuitka ^
  --onefile ^
  --windows-console-mode=disable ^
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

REM --- Verify output and copy external assets ---
echo [4/4] Verifying output and copying external assets...
if not exist "dist\DM40 Wireless.exe" (
    echo [ERROR] Output exe not found.
    pause
    exit /b 1
)

REM Copy i18n language files (external, not packed in exe)
if exist "i18n" (
    if not exist "dist\i18n" mkdir "dist\i18n"
    xcopy /Y /E "i18n\*.toml" "dist\i18n\" >nul 2>&1
    echo   i18n\ copied to dist\i18n\
)

REM Copy settings template as default config
if not exist "dist\settings.json" (
    copy /Y "settings.example.json" "dist\settings.json" >nul 2>&1
    echo   settings.example.json copied to dist\settings.json
)

echo.
echo ============================================
echo  Build succeeded
echo  Output: dist\DM40 Wireless.exe
echo.
echo  Distribution folder contents:
echo    dist\DM40 Wireless.exe
echo    dist\i18n\          (language files)
echo    dist\settings.json   (default config)
echo ============================================
pause
