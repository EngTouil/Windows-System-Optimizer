@echo off
title System Optimizer Builder
echo ===========================================
echo   SYSTEM OPTIMIZER: PROFESSIONAL BUILDER
echo ===========================================

:: 1. Cleanup old build files
echo [1/3] Cleaning up old artifacts...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist SystemOptimizer.spec del /f /q SystemOptimizer.spec

:: 2. Run PyInstaller
echo [2/3] Compiling Project (This may take 1-2 minutes)...
pyinstaller --noconfirm --onefile --windowed ^
--icon="assets/icon.ico" ^
--add-data "assets;assets" ^
--add-data "core;core" ^
--add-data "ui;ui" ^
--add-data "utils;utils" ^
--collect-all customtkinter ^
--collect-all psutil ^
--hidden-import winreg ^
--hidden-import pystray ^
--hidden-import PIL ^
--hidden-import PIL.Image ^
--hidden-import PIL.ImageDraw ^
--hidden-import csv ^
--hidden-import ctypes ^
--name "SystemOptimizer" ^
main.py

:: 3. Verification
if %ERRORLEVEL% EQU 0 (
    echo ===========================================
    echo   SUCCESS: Build complete!
    echo   Your exe is in: dist/SystemOptimizer.exe
    echo ===========================================
) else (
    echo ===========================================
    echo   ERROR: Build failed. Check the logs above.
    echo ===========================================
)

pause