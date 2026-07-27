@echo off
title Ferreteria Gian - Control de Stock
echo Iniciando Sistema de Control de Stock - Ferreteria Gian...
echo.
cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo iniciar el programa.
    echo Asegurate de tener Python instalado y haber ejecutado:
    echo pip install openpyxl reportlab matplotlib pillow
    echo.
    pause
)
