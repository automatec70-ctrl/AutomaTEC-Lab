#!/usr/bin/env bash
# Ejecutar AutomataLab
cd "$(dirname "$0")"
python3 main.py 2>/dev/null || python main.py
