@echo off
chcp 65001 > nul
title Abhiram C S - Portfolio Server
cd /d "%~dp0"

echo =======================================================
echo   Starting Abhiram C S Portfolio & Backend Server...
echo =======================================================
echo.

:: Detect Python executable
set PYTHON_CMD=

:: Try python command
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto RUN
)

:: Try py launcher
py -3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py -3
    goto RUN
)

:: Try direct User AppData Python path
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto RUN
)

echo [ERROR] Python was not found in PATH or standard installation directories.
echo Please run: winget install Python.Python.3.13
pause
exit /b 1

:RUN
echo Using Python: %PYTHON_CMD%
echo.
%PYTHON_CMD% -m pip install -r requirements.txt --quiet
echo.
echo Starting server...
echo Serving at: http://127.0.0.1:5000
echo Leads Dashboard: http://127.0.0.1:5000/leads
echo.
%PYTHON_CMD% app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Server stopped with error.
    pause
)
