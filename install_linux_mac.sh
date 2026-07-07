#!/usr/bin/env bash
# AutomataLab - Instalador de dependencias (Linux / macOS)

set -e

echo ""
echo "  ===================================================="
echo "    AutomataLab - Instalador de dependencias"
echo "    Python + Tkinter + Graphviz + Pillow"
echo "  ===================================================="
echo ""

# 1. Verificar Python
echo "[1/5] Verificando Python 3..."
if command -v python3 &>/dev/null; then
    PY=python3
    PIP=pip3
elif command -v python &>/dev/null; then
    PY=python
    PIP=pip
else
    echo ""
    echo "  [ERROR] Python 3 no esta instalado."
    echo ""
    echo "  Instalalo con:"
    echo "    Ubuntu/Debian:  sudo apt install python3 python3-pip"
    echo "    Fedora:         sudo dnf install python3 python3-pip"
    echo "    macOS:          brew install python3"
    echo ""
    exit 1
fi
PYVER=$($PY --version 2>&1 | cut -d' ' -f2)
echo "  [OK] Python $PYVER encontrado ($PY)"
echo ""

# 2. Verificar tkinter
echo "[2/5] Verificando Tkinter..."
if $PY -c "import tkinter" 2>/dev/null; then
    echo "  [OK] Tkinter disponible"
else
    echo ""
    echo "  [ERROR] Tkinter no esta disponible."
    echo ""
    echo "  Instalalo con:"
    echo "    Ubuntu/Debian:  sudo apt install python3-tk"
    echo "    Fedora:         sudo dnf install python3-tkinter"
    echo "    macOS:          Viene con Python de python.org o brew"
    echo ""
    if command -v apt &>/dev/null; then
        echo "  ¿Instalar python3-tk automaticamente? [s/N]"
        read -r respuesta
        if [[ "$respuesta" =~ ^[sS]$ ]]; then
            sudo apt install -y python3-tk
        else
            exit 1
        fi
    else
        exit 1
    fi
fi
echo ""

# 3. Instalar Pillow
echo "[3/5] Verificando Pillow..."
if $PY -c "from PIL import Image" 2>/dev/null; then
    echo "  [OK] Pillow ya esta instalado"
else
    echo "  Instalando Pillow..."
    $PY -m pip install Pillow --quiet 2>/dev/null || pip install Pillow --quiet
    if $PY -c "from PIL import Image" 2>/dev/null; then
        echo "  [OK] Pillow instalado"
    else
        echo ""
        echo "  [ERROR] No se pudo instalar Pillow."
        echo "  Intenta manualmente: $PIP install Pillow"
        exit 1
    fi
fi
echo ""

# 4. Instalar graphviz (Python)
echo "[4/5] Verificando graphviz (Python)..."
if $PY -c "import graphviz" 2>/dev/null; then
    echo "  [OK] graphviz (Python) ya esta instalado"
else
    echo "  Instalando graphviz..."
    $PY -m pip install graphviz --quiet 2>/dev/null || pip install graphviz --quiet
    if $PY -c "import graphviz" 2>/dev/null; then
        echo "  [OK] graphviz (Python) instalado"
    else
        echo ""
        echo "  [ERROR] No se pudo instalar graphviz."
        echo "  Intenta manualmente: $PIP install graphviz"
        exit 1
    fi
fi
echo ""

# 5. Verificar Graphviz (sistema)
echo "[5/5] Verificando Graphviz (motor del sistema)..."
if command -v dot &>/dev/null; then
    GVVER=$(dot -V 2>&1 | grep -oP 'graphviz version \K[0-9.]+' || echo "desconocida")
    echo "  [OK] Graphviz $GVVER encontrado"
else
    echo ""
    echo "  [AVISO] Graphviz (dot) no esta instalado en el sistema."
    echo ""
    echo "  El programa necesita Graphviz para generar diagramas."
    echo ""
    echo "  Instalalo con:"
    echo "    Ubuntu/Debian:  sudo apt install graphviz"
    echo "    Fedora:         sudo dnf install graphviz"
    echo "    macOS:          brew install graphviz"
    echo "    Arch:           sudo pacman -S graphviz"
    echo ""
    if command -v apt &>/dev/null; then
        echo "  ¿Instalar graphviz automaticamente? [s/N]"
        read -r respuesta
        if [[ "$respuesta" =~ ^[sS]$ ]]; then
            sudo apt install -y graphviz
        else
            exit 1
        fi
    else
        exit 1
    fi
fi
echo ""

# Verificacion final
echo ""
echo "  ===================================================="
echo "    Todas las dependencias estan instaladas correctamente"
echo "  ===================================================="
echo ""
echo "  Para ejecutar AutomataLab:"
echo ""
echo "    cd automatas_app"
echo "    $PY main.py"
echo ""
echo "  O ejecuta: ./ejecutar.sh"
echo ""
