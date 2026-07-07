@echo off
title AutomataLab

cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Error al ejecutar. Asegurate de correr install_windows.bat primero.
    pause
)
