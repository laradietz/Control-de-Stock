@echo off
title Creando instalador de Ferreteria Gian...
color 0A
cls

echo =================================================
echo   FERRETERIA GIAN - Creador de Instalador
echo =================================================
echo.
echo  Este proceso va a crear un instalador profesional
echo  (.exe) que el cliente puede usar para instalar
echo  el sistema como cualquier programa de Windows.
echo.
echo  Duracion estimada: 5 a 10 minutos
echo  No cierres esta ventana.
echo.
echo =================================================
pause

:: ── PASO 1: Verificar Python ──────────────────────
echo.
echo [1/5] Verificando Python...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Python no esta instalado.
    echo  Instala Python desde: https://www.python.org/downloads/
    echo  Asegurate de tildar "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
python --version
echo  Python OK

:: ── PASO 2: Instalar dependencias ─────────────────
echo.
echo [2/5] Instalando dependencias de Python...
pip install pyinstaller openpyxl reportlab matplotlib pillow --quiet
if %errorlevel% neq 0 (
    echo  ERROR al instalar dependencias.
    pause
    exit /b 1
)
echo  Dependencias OK

:: ── PASO 3: Generar el .exe con PyInstaller ───────
echo.
echo [3/5] Generando el ejecutable (tarda 3-5 minutos)...
echo.

if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "ControlStock_Gian.spec" del "ControlStock_Gian.spec"

pyinstaller --onefile --windowed ^
  --name "ControlStock_Gian" ^
  --icon "icono.ico" ^
  --hidden-import "openpyxl" ^
  --hidden-import "openpyxl.styles" ^
  --hidden-import "reportlab" ^
  --hidden-import "reportlab.lib" ^
  --hidden-import "reportlab.platypus" ^
  --hidden-import "matplotlib" ^
  --hidden-import "matplotlib.backends.backend_tkagg" ^
  --hidden-import "PIL" ^
  --hidden-import "PIL.Image" ^
  --hidden-import "PIL.ImageDraw" ^
  --hidden-import "tkinter" ^
  --hidden-import "tkinter.ttk" ^
  --hidden-import "sqlite3" ^
  --hidden-import "hashlib" ^
  --collect-all "reportlab" ^
  --collect-all "openpyxl" ^
  main.py

if %errorlevel% neq 0 (
    echo.
    echo  ERROR al crear el ejecutable.
    echo  Revisa los mensajes de error arriba.
    pause
    exit /b 1
)

if not exist "dist\ControlStock_Gian.exe" (
    echo  ERROR: No se genero el .exe
    pause
    exit /b 1
)
echo.
echo  Ejecutable generado correctamente.

:: ── PASO 4: Verificar/instalar Inno Setup ─────────
echo.
echo [4/5] Verificando Inno Setup...

set ISCC=""
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
)

if %ISCC%=="" (
    echo  Inno Setup no encontrado. Descargando e instalando...
    echo  (necesitas conexion a internet)
    echo.
    curl -L -o "%TEMP%\innosetup.exe" "https://files.jrsoftware.org/is/6/innosetup-6.3.3.exe"
    if %errorlevel% neq 0 (
        echo  No se pudo descargar. Instala manualmente desde:
        echo  https://jrsoftware.org/isdl.php
        pause
        exit /b 1
    )
    "%TEMP%\innosetup.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
    timeout /t 5 /nobreak > nul
    if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
        set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    )
    if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
        set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
    )
)

if %ISCC%=="" (
    echo  No se pudo instalar Inno Setup automaticamente.
    echo  Instala manualmente desde: https://jrsoftware.org/isdl.php
    echo  Luego ejecuta este script de nuevo.
    pause
    exit /b 1
)
echo  Inno Setup encontrado: %ISCC%

:: ── PASO 5: Crear el instalador ───────────────────
echo.
echo [5/5] Creando el instalador profesional...
echo.

if exist "INSTALADOR" rmdir /s /q "INSTALADOR"
mkdir "INSTALADOR"

%ISCC% "setup.iss"

if %errorlevel% neq 0 (
    echo  ERROR al crear el instalador.
    pause
    exit /b 1
)

:: ── RESULTADO ──────────────────────────────────────
cls
color 0A
echo.
echo =================================================
echo   LISTO! El instalador fue creado correctamente.
echo =================================================
echo.
echo  Archivo generado:
echo  INSTALADOR\Instalar_ControlStock_Gian.exe
echo.
echo  Ese unico archivo es todo lo que necesita
echo  el cliente para instalar el sistema.
echo.
echo  Lo que ve el cliente al instalarlo:
echo   - Asistente de instalacion profesional
echo   - Se instala en "Archivos de programa"
echo   - Acceso directo en el Escritorio
echo   - Acceso directo en el Menu Inicio
echo   - Aparece en "Agregar o quitar programas"
echo   - Icono propio de ferreteria
echo.
echo  Contrasena inicial: 1234 (usuario: dueno)
echo.
echo =================================================
echo.

:: Abrir la carpeta con el instalador
explorer "INSTALADOR"
pause
