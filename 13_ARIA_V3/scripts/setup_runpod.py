"""
ARIA — Script de setup del entorno RunPod.

Uso:
    python scripts/setup_runpod.py [--tunnel] [--pull] [--status]

Flags:
    --tunnel  Abrir tunnel SSH hacia el pod de RunPod
    --pull    Descargar modelos necesarios en Ollama (Gemma 3:27B + nomic-embed-text)
    --status  Mostrar estado actual del entorno
    (sin flags) Ejecuta todo: tunnel + pull + status
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aria.runpod.setup import print_status, pull_required_models
from aria.runpod.tunnel import tunnel


def main():
    parser = argparse.ArgumentParser(description="ARIA RunPod Setup")
    parser.add_argument("--tunnel", action="store_true", help="Abrir tunnel SSH")
    parser.add_argument("--pull", action="store_true", help="Descargar modelos en Ollama")
    parser.add_argument("--status", action="store_true", help="Mostrar estado del entorno")
    args = parser.parse_args()

    run_all = not (args.tunnel or args.pull or args.status)

    if args.tunnel or run_all:
        success = tunnel.open()
        if not success and run_all:
            print("\n⚠️  No se pudo establecer el tunnel. Verifica tu .env y la conexión SSH.")
            print("   Puedes configurar OLLAMA_BASE_URL directamente si el pod expone el puerto.")
            return

    if args.pull or run_all:
        pull_required_models()

    if args.status or run_all:
        print_status()


if __name__ == "__main__":
    main()
