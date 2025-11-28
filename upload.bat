@echo off
setlocal enabledelayedexpansion

REM Check if a port was provided
if "%~1"=="" (
    echo Error: Please provide the serial port as an argument.
    echo Usage: upload.cmd COM3
    exit /b 1
)

REM Configuration
set PORT=%~1
set LOCAL_DIR=src
set REMOTE_DIR=/pyboard

echo Connecting to %PORT% for file synchronization...
echo --- rshell rsync output ---

REM 1. Sync only changed files
rshell -p %PORT% rsync %LOCAL_DIR%/ %REMOTE_DIR%/
if errorlevel 1 (
    echo --- rsync failed! Aborting soft reset. ---
    exit /b 1
)

echo --- rshell soft reset output ---

REM 2. Soft reset via REPL
rshell -p %PORT% repl "~ import machine ~ machine.soft_reset() ~"

echo -----------------------------------
echo ✅ Synchronization and soft reset complete for port %PORT%.
exit /b 0