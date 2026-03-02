#!/bin/bash
# ============================================================
# ARIA — Setup de Ollama en un Pod de RunPod
# Ejecutar DENTRO del pod de RunPod (vía SSH o terminal web)
# ============================================================

set -e

echo "=== ARIA: Configurando Ollama en RunPod ==="

# 1. Install Ollama
echo "[1/4] Instalando Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# 2. Configure Ollama to listen on all interfaces
echo "[2/4] Configurando OLLAMA_HOST..."
export OLLAMA_HOST=0.0.0.0
echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.bashrc

# 3. Start Ollama server in background
echo "[3/4] Iniciando Ollama server..."
ollama serve &
sleep 5

# 4. Pull required models
echo "[4/4] Descargando modelos..."
echo "  → Gemma 3:27B (esto puede tardar varios minutos)..."
ollama pull gemma3:27b

echo "  → nomic-embed-text..."
ollama pull nomic-embed-text

echo ""
echo "=== ✓ Setup completado ==="
echo "Ollama escuchando en puerto 11434"
echo "Modelos disponibles:"
ollama list
