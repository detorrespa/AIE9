"""
Script para verificar que la API key de OpenAI esta configurada correctamente
"""

import os
from dotenv import load_dotenv

print("=" * 80)
print("VERIFICACION DE API KEY")
print("=" * 80)

# Cargar variables de entorno
load_dotenv()

# Verificar que existe
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("\n[ERROR] No se encontro OPENAI_API_KEY en el archivo .env")
    print("\nAsegurate de que:")
    print("  1. El archivo .env existe en el directorio actual")
    print("  2. Contiene la linea: OPENAI_API_KEY=tu-clave-aqui")
    print("  3. Reemplazaste 'tu-clave-aqui' con tu API key real")
    exit(1)

if api_key == "tu-api-key-aqui":
    print("\n[ERROR] Todavia no has reemplazado el placeholder")
    print("\nEdita el archivo .env y reemplaza 'tu-api-key-aqui' con tu API key real")
    exit(1)

# Verificar formato
if not api_key.startswith("sk-"):
    print(f"\n[WARNING] La API key no parece tener el formato correcto")
    print(f"           Las keys de OpenAI suelen empezar con 'sk-' o 'sk-proj-'")
    print(f"           Tu key empieza con: {api_key[:10]}...")
else:
    print(f"\n[OK] API key encontrada y cargada correctamente")
    print(f"     Primeros caracteres: {api_key[:10]}...")
    print(f"     Longitud: {len(api_key)} caracteres")

# Intentar conectar con OpenAI (sin hacer una llamada real)
try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    print("\n[OK] Cliente de OpenAI inicializado correctamente")
    print("\n" + "=" * 80)
    print("[SUCCESS] Todo configurado correctamente!")
    print("=" * 80)
    print("\nAhora puedes:")
    print("  1. Ejecutar: uv run jupyter notebook")
    print("  2. Abrir: notebooks/Enhanced_RAG_Assignment.ipynb")
    print("  3. Ejecutar todas las celdas")
    
except ImportError:
    print("\n[WARNING] Modulo 'openai' no encontrado")
    print("          Ejecuta: uv sync -p 3.12")
except Exception as e:
    print(f"\n[ERROR] Error al inicializar cliente: {e}")
    print("        Verifica que tu API key sea correcta")
