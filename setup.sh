#!/usr/bin/env bash
# ==============================================================================
# setup.sh - Instalador en 1 solo comando para el repositorio de Visión por Computador
# ==============================================================================
set -e

echo "======================================================================"
echo "📚 Inicializando Entorno de Apuntes y Textbooks de Visión por Computador"
echo "======================================================================"

# 1. Comprobar / Instalar uv
if ! command -v uv &> /dev/null; then
    echo "⚙️  'uv' no encontrado en el sistema. Instalando uv automáticamente..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✓ uv está listo ($(uv --version))"

# 2. Ejecutar el orquestador Python con todas las dependencias aisladas
uv run --with pymupdf,pymupdf4llm,lancedb,fastembed,pyyaml python3 scripts/setup_repo.py "$@"
