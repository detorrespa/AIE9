#!/bin/bash
# ============================================================
# ARIA — Setup de Ollama en RunPod (con Network Volume)
# Ejecutar DENTRO del pod de RunPod (vía SSH o terminal web)
# Modelos en /workspace/.ollama → persisten al reiniciar el pod
# ============================================================

set -e

echo "=== ARIA: Configurando Ollama en RunPod (Network Volume) ==="

# 0. Dependencies
apt-get update -qq && apt-get install -y -qq zstd

# 1. Install Ollama
echo "[1/5] Instalando Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# 2. Crear directorio en Network Volume
echo "[2/5] Configurando modelos en /workspace/.ollama (persistente)..."
mkdir -p /workspace/.ollama
export OLLAMA_MODELS=/workspace/.ollama

# 3. Script de arranque para futuras sesiones
echo "[3/5] Creando /workspace/start_ollama.sh..."
cat > /workspace/start_ollama.sh << 'EOF'
#!/bin/bash
export OLLAMA_MODELS=/workspace/.ollama
nohup ollama serve > /workspace/ollama.log 2>&1 &
sleep 3
ollama list
EOF
chmod +x /workspace/start_ollama.sh

# 4. Start Ollama con modelos en /workspace
echo "[4/5] Iniciando Ollama server..."
OLLAMA_MODELS=/workspace/.ollama nohup ollama serve > /workspace/ollama.log 2>&1 &
sleep 5

# 5. Pull models (solo si no existen)
echo "[5/5] Descargando modelos en /workspace/.ollama..."
if ! OLLAMA_MODELS=/workspace/.ollama ollama list 2>/dev/null | grep -q nomic-embed-text; then
  echo "  → nomic-embed-text..."
  OLLAMA_MODELS=/workspace/.ollama ollama pull nomic-embed-text
fi
if ! OLLAMA_MODELS=/workspace/.ollama ollama list 2>/dev/null | grep -q gemma3:27b; then
  echo "  → gemma3:27b (esto puede tardar varios minutos)..."
  OLLAMA_MODELS=/workspace/.ollama ollama pull gemma3:27b
fi

echo ""
echo "=== ✓ Setup completado ==="
echo "Modelos en /workspace/.ollama (persisten al reiniciar pod)"
echo "Para arrancar Ollama en futuras sesiones: /workspace/start_ollama.sh"
OLLAMA_MODELS=/workspace/.ollama ollama list
