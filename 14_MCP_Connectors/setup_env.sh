#!/bin/bash
# Session 14: Setup de entorno en WSL
# Ejecutar desde la carpeta 14_MCP_Connectors: bash setup_env.sh

set -e

echo "=== 1. Verificar python3-venv ==="
if ! python3 -m venv --help &>/dev/null; then
    echo "Instalando python3-venv..."
    sudo apt-get update
    sudo apt-get install -y python3.12-venv
fi

echo "=== 2. Crear entorno virtual ==="
python3 -m venv .venv

echo "=== 3. Activar y instalar dependencias ==="
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== 4. Registrar kernel de Jupyter ==="
python -m ipykernel install --user --name=14-mcp-connectors --display-name="Python (14 MCP Connectors)"

echo ""
echo "=== ¡Listo! ==="
echo "Activa el entorno con: source .venv/bin/activate"
echo "Usa el kernel 'Python (14 MCP Connectors)' en tu notebook."
