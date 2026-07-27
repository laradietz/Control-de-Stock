@echo off
title Creando aplicacion ControlStock Gian...
color 0A
cls
echo ============================================
echo   CREADOR DE APLICACION - Ferreteria Gian
echo ============================================
echo.
echo Este proceso puede tardar 3 a 5 minutos.
echo No cierres esta ventana.
echo.

:: Verificar Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado.
    echo Instala Python desde https://www.python.org/downloads/
    echo y asegurate de tildar "Add Python to PATH"
    pause
    exit
)

echo [1/3] Instalando dependencias necesarias...
pip install pyinstaller openpyxl reportlab matplotlib pillow --quiet
if %errorlevel% neq 0 (
    echo ERROR al instalar dependencias.
    pause
    exit
)

echo.
echo [2/3] Creando el ejecutable (esto tarda unos minutos)...
echo.

pyinstaller --onefile --windowed ^
  --name "ControlStock_Gian" ^
  --add-data "db;db" ^
  --add-data "exports;exports" ^
  --add-data "docs;docs" ^
  --hidden-import "openpyxl" ^
  --hidden-import "reportlab" ^
  --hidden-import "matplotlib" ^
  --hidden-import "PIL" ^
  --hidden-import "tkinter" ^
  --hidden-import "sqlite3" ^
  main.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR al crear el ejecutable.
    pause
    exit
)

echo.
echo [3/3] Armando la carpeta final para entregar al cliente...

:: Crear carpeta de entrega
if exist "ControlStock_Gian_APP" rmdir /s /q "ControlStock_Gian_APP"
mkdir "ControlStock_Gian_APP"
mkdir "ControlStock_Gian_APP\db"
mkdir "ControlStock_Gian_APP\exports"
mkdir "ControlStock_Gian_APP\exports\comprobantes"
mkdir "ControlStock_Gian_APP\docs"
mkdir "ControlStock_Gian_APP\db\backups"

:: Copiar ejecutable
copy "dist\ControlStock_Gian.exe" "ControlStock_Gian_APP\"

:: Copiar base de datos
copy "db\ferreteria.db" "ControlStock_Gian_APP\db\"

:: Copiar documentacion
copy "docs\Documentacion_Tecnica_Ferreteria.docx" "ControlStock_Gian_APP\docs\" 2>nul
copy "docs\diagrama_uml.png" "ControlStock_Gian_APP\docs\" 2>nul

:: Crear archivo de instrucciones simplificado
echo FERRETERIA GIAN - Sistema de Control de Stock > "ControlStock_Gian_APP\LEEME.txt"
echo. >> "ControlStock_Gian_APP\LEEME.txt"
echo Para abrir el programa: >> "ControlStock_Gian_APP\LEEME.txt"
echo   Doble clic en ControlStock_Gian.exe >> "ControlStock_Gian_APP\LEEME.txt"
echo. >> "ControlStock_Gian_APP\LEEME.txt"
echo Usuario: dueno >> "ControlStock_Gian_APP\LEEME.txt"
echo Contrasena: 1234 >> "ControlStock_Gian_APP\LEEME.txt"
echo. >> "ControlStock_Gian_APP\LEEME.txt"
echo IMPORTANTE: No muevas ni borres ninguna carpeta. >> "ControlStock_Gian_APP\LEEME.txt"
echo Los datos se guardan en la carpeta db\ >> "ControlStock_Gian_APP\LEEME.txt"
echo Las boletas y reportes se guardan en exports\ >> "ControlStock_Gian_APP\LEEME.txt"

cls
echo ============================================
echo   LISTO! Aplicacion creada correctamente.
echo ============================================
echo.
echo La carpeta "ControlStock_Gian_APP" contiene
echo todo lo que necesita el cliente:
echo.
echo   ControlStock_Gian_APP\
echo   ├── ControlStock_Gian.exe   (el programa)
echo   ├── db\                     (datos)
echo   ├── exports\                (reportes y boletas)
echo   ├── docs\                   (documentacion)
echo   └── LEEME.txt
echo.
echo Podés comprimir esa carpeta en un ZIP y
echo enviarsela al cliente. El cliente solo hace
echo doble clic en ControlStock_Gian.exe
echo.
echo Si Windows bloquea el .exe la primera vez:
echo   clic derecho - Mas informacion - Ejecutar de todas formas
echo.
pause
