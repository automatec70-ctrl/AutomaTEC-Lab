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
:: 1. Verificar / Instalar Python
:: ----------------------------------------------------------
echo [1/5] Verificando Python 3...

:CHECK_PYTHON
where python >nul 2>&1
if %errorlevel% neq 0 goto INSTALL_PYTHON

python -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [AVISO] Se encontro Python pero es version anterior a 3.8.
    goto INSTALL_PYTHON
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
echo  [OK] Python %PYVER% encontrado
goto CHECK_TKINTER

:INSTALL_PYTHON
echo  Python no encontrado o version insuficiente. Instalando automaticamente...
echo.

:: Intentar con winget primero
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo  Usando winget para instalar Python 3.11...
    winget install --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    if !errorlevel! equ 0 (
        echo  [OK] Python instalado con winget.
        :: Actualizar PATH para esta sesion
        for /f "usebackq tokens=*" %%p in (`where /r "%LOCALAPPDATA%\Programs\Python" python.exe 2^>nul`) do set "PYPATH=%%p"
        if not "!PYPATH!"=="" (
            set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;!PATH!"
        )
        goto VERIFY_PYTHON_OK
    )
    echo  [AVISO] winget no pudo instalar Python. Intentando con descarga directa...
)

:: Fallback: descargar instalador desde python.org con curl
echo  Descargando instalador de Python 3.11 desde python.org...
set "PY_INSTALLER=%TEMP%\python_installer.exe"
curl -L -o "!PY_INSTALLER!" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" --progress-bar
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] No se pudo descargar Python automaticamente.
    echo  Por favor descargalo manualmente desde:
    echo  https://www.python.org/downloads/
    echo  y marca "Add Python to PATH" al instalar.
    echo.
    pause
    exit /b 1
)

echo  Ejecutando instalador de Python (instalacion silenciosa)...
"!PY_INSTALLER!" /quiet InstallAllUsers=0 PrependPath=1 Include_tcltk=1 Include_pip=1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] La instalacion de Python fallo.
    echo  Intenta instalarlo manualmente desde:
    echo  https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
del "!PY_INSTALLER!" >nul 2>&1

:: Actualizar PATH para esta sesion
set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;!PATH!"

:VERIFY_PYTHON_OK
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Python se instalo pero no se encontro en el PATH.
    echo  Cierra esta ventana, abre una nueva terminal y ejecuta
    echo  install_windows.bat de nuevo.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
echo  [OK] Python %PYVER% instalado correctamente
echo.

:: ----------------------------------------------------------
:: 2. Verificar Tkinter
:: ----------------------------------------------------------
:CHECK_TKINTER
echo [2/5] Verificando Tkinter...
python -c "import tkinter" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Tkinter disponible
    echo.
    goto CHECK_PILLOW
)

echo  [AVISO] Tkinter no disponible. Reinstalando Python con soporte tcl/tk...
echo.

:: Descargar e instalar Python con Include_tcltk=1
set "PY_INSTALLER=%TEMP%\python_installer.exe"

:: Detectar version instalada para usar el mismo instalador
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PYVER_FULL=%%v"
set "PY_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"

curl -L -o "!PY_INSTALLER!" "!PY_URL!" --progress-bar
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] No se pudo descargar el instalador de Python.
    echo  Reinstala Python manualmente desde https://www.python.org/downloads/
    echo  y marca "tcl/tk and IDLE" en instalacion personalizada.
    echo.
    pause
    exit /b 1
)

echo  Reinstalando Python con Tkinter habilitado...
"!PY_INSTALLER!" /quiet InstallAllUsers=0 PrependPath=1 Include_tcltk=1 Include_pip=1
del "!PY_INSTALLER!" >nul 2>&1

python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] No se pudo habilitar Tkinter automaticamente.
    echo  Reinstala Python manualmente desde https://www.python.org/downloads/
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
:CHECK_PILLOW
echo [3/5] Verificando Pillow...
python -c "from PIL import Image" >nul 2>&1
if %errorlevel% neq 0 (
    echo  Instalando Pillow...
    python -m pip install Pillow --quiet
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
:: 5. Verificar / Instalar Graphviz (motor del sistema - dot)
:: ----------------------------------------------------------
echo [5/5] Verificando Graphviz (motor del sistema)...
where dot >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Graphviz encontrado en el sistema
    echo.
    goto ALL_DONE
)

echo  Graphviz no encontrado. Instalando automaticamente...
echo.

:: Intentar con winget
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo  Usando winget para instalar Graphviz...
    winget install --id Graphviz.Graphviz --silent --accept-package-agreements --accept-source-agreements
    if !errorlevel! equ 0 (
        :: Actualizar PATH para esta sesion
        set "PATH=C:\Program Files\Graphviz\bin;!PATH!"
        where dot >nul 2>&1
        if !errorlevel! equ 0 (
            echo  [OK] Graphviz instalado con winget.
            echo.
            goto ALL_DONE
        )
    )
    echo  [AVISO] winget no pudo instalar Graphviz. Intentando con descarga directa...
)

:: Fallback: descargar instalador .exe desde graphviz.org
echo  Descargando instalador de Graphviz desde graphviz.org...
set "GV_INSTALLER=%TEMP%\graphviz_installer.exe"
curl -L -o "!GV_INSTALLER!" "https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/12.2.1/windows_10_cmake_Release_graphviz-install-12.2.1-win64.exe" --progress-bar
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] No se pudo descargar Graphviz automaticamente.
    echo  Por favor instalalo manualmente desde:
    echo  https://graphviz.org/download/
    echo  y ejecuta install_windows.bat de nuevo.
    echo.
    pause
    exit /b 1
)

echo  Ejecutando instalador de Graphviz...
"!GV_INSTALLER!" /S
del "!GV_INSTALLER!" >nul 2>&1

:: Agregar al PATH de esta sesion
set "PATH=C:\Program Files\Graphviz\bin;!PATH!"

where dot >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [AVISO] Graphviz se instalo pero requiere reiniciar la terminal.
    echo  Cierra esta ventana, abre una nueva y ejecuta ejecutar.bat
    echo.
    pause
    exit /b 0
)
echo  [OK] Graphviz instalado correctamente
echo.

:: ----------------------------------------------------------
:: Listo
:: ----------------------------------------------------------
:ALL_DONE
echo.
echo  ====================================================
echo    Todas las dependencias instaladas correctamente
echo    Puedes usar ejecutar.bat para iniciar AutomataLab
echo  ====================================================
echo.
pause
