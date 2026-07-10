@echo off
setlocal enabledelayedexpansion

title AutomataLab - Instalador de dependencias

echo.
echo  ====================================================
echo    AutomataLab - Instalador de dependencias
echo    Python + Tkinter + Graphviz + Pillow
echo  ====================================================
echo.

:: ----------------------------------------------------------
:: 1. Verificar Python
:: ----------------------------------------------------------
echo [1/5] Verificando Python 3...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Python no esta instalado o no esta en el PATH.
    echo.
    echo  Descarga Python 3.10+ desde: https://www.python.org/downloads/
    echo  Asegurate de marcar "Add Python to PATH" al instalar.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
echo  [OK] Python %PYVER% encontrado
echo.

:: ----------------------------------------------------------
:: 2. Verificar Tkinter
:: ----------------------------------------------------------
echo [2/5] Verificando Tkinter...
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Tkinter no esta disponible.
    echo.
    echo  En Windows, Tkinter viene con Python.
    echo  Reinstala Python desde https://www.python.org/downloads/
    echo  y marca "tcl/tk and IDLE" en instalacion personalizada.
    echo.
    pause
    exit /b 1
)
echo  [OK] Tkinter disponible
echo.

:: ----------------------------------------------------------
:: 3. Instalar Pillow
:: ----------------------------------------------------------
echo [3/5] Verificando Pillow...
python -c "from PIL import Image" >nul 2>&1
if %errorlevel% neq 0 (
    echo  Instalando Pillow...
    python -m pip install Pillow --quiet
    if !errorlevel! neq 0 (
        pip install Pillow --quiet
    )
)

python -c "from PIL import Image" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] No se pudo instalar Pillow.
    echo  Intenta manualmente:  python -m pip install Pillow
    echo.
    pause
    exit /b 1
)
echo  [OK] Pillow instalado
echo.

:: ----------------------------------------------------------
:: 4. Instalar graphviz (paquete Python)
:: ----------------------------------------------------------
echo [4/5] Verificando graphviz (Python)...
python -c "import graphviz" >nul 2>&1
if %errorlevel% neq 0 (
    echo  Instalando graphviz...
    python -m pip install graphviz --quiet
    if !errorlevel! neq 0 (
        pip install graphviz --quiet
    )
)

python -c "import graphviz" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] No se pudo instalar graphviz.
    echo  Intenta manualmente:  python -m pip install graphviz
    echo.
    pause
    exit /b 1
)
echo  [OK] graphviz (Python) instalado
echo.

:: ----------------------------------------------------------
:: 5. Verificar Graphviz (sistema - ejecutable dot)
:: ----------------------------------------------------------
echo [5/5] Verificando Graphviz (motor del sistema)...
where dot >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [AVISO] Graphviz (dot) no esta instalado en el sistema.
    echo.
    echo  El programa necesita el motor Graphviz para generar
    echo  los diagramas de automatas.
    echo.
    echo  Opciones para instalarlo:
    echo.
    echo  1. Descarga el instalador desde:
    echo     https://graphviz.org/download/
    echo     (Busca "Windows" y descarga el .msi o .exe)
    echo.
    echo  2. Con Chocolatey:
    echo     choco install graphviz
    echo.
    echo  3. Con winget:
    echo     winget install graphviz
    echo.
    echo  IMPORTANTE: Despues de instalar Graphviz, CIERRA y
    echo  REABRE esta terminal para que el PATH se actualice.
    echo.
    echo  Luego ejecuta este script de nuevo para verificar.
    echo.
    pause
    exit /b 1
)
echo  [OK] Graphviz encontrado en el sistema
echo.

:: ----------------------------------------------------------
:: Verificacion final
:: ----------------------------------------------------------
echo.
echo  ====================================================
echo    Todas las dependencias estan instaladas correctamente
echo  ====================================================
echo.
echo  Para ejecutar AutomataLab:
echo.
echo    cd automatas_app
echo    python main.py
echo.
echo  O haz doble clic en: ejecutar.bat
echo.
pause
