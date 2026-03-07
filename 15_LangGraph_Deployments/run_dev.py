"""Inicia langgraph dev con las variables de .env cargadas."""
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env antes de iniciar el servidor
load_dotenv(Path(__file__).resolve().parent / ".env")

cwd = Path(__file__).resolve().parent
subprocess.run(["uv", "run", "langgraph", "dev"], cwd=cwd, env=os.environ.copy())
