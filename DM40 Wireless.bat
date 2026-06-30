@echo off
cd /d "%~dp0"

if exist .venv\Scripts\pythonw.exe (
    start "" .venv\Scripts\pythonw.exe app.pyw
) else (
    start "" pythonw app.pyw
)
