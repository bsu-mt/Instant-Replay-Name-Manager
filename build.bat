@echo off
title Instant Replay Name Manager Builder

echo ========================================================
echo        Instant Replay Name MANAGER - EXE BUILDER
echo ========================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python first.
    pause
    exit /b
)

:: 2. Install PyInstaller
echo [1/3] Installing/Updating PyInstaller...
pip install pyinstaller -U
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install PyInstaller.
    pause
    exit /b
)

:: 3. Run build command
:: --noconsole: Hide console window
:: --onefile: Bundle into a single exe file
:: --name: Specify output filename
:: --icon: Set the executable icon
echo.
echo [2/3] Building EXE file (this may take a minute)...
pyinstaller --noconsole --onefile --name "IRMN" --icon=icon.ico irnm.py


if %errorlevel% neq 0 (
    echo [ERROR] Build failed.
    pause
    exit /b
)

:: 4. Clean up temporary files
echo.
echo [3/3] Cleaning up temporary files...
rmdir /s /q build
del /q IRMN.spec

echo.
echo ========================================================
echo    SUCCESS! BUILD COMPLETE
echo ========================================================
echo.
echo Your software is located in the "dist" folder.
echo.
echo You can now close this window.
pause