"""Script para verificar que las API keys funcionan."""
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env desde el directorio del proyecto
load_dotenv(Path(__file__).resolve().parent / ".env")

import os

print("OPENAI_API_KEY:", "OK" if os.getenv("OPENAI_API_KEY", "").startswith("sk-") else "FALTA")
print("TAVILY_API_KEY:", "OK" if os.getenv("TAVILY_API_KEY", "").startswith("tvly") else "FALTA")

from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1-nano")
response = model.invoke("Di hola en una palabra")
print("OpenAI test:", response.content)
print("\nLas claves funcionan correctamente.")
