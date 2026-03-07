"""
Test rápido del flujo ARIA desde CLI — para ver errores sin Chainlit.
Uso: python scripts/test_aria_cli.py
"""
import asyncio
import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv()


async def main():
    print("=== Test ARIA CLI ===\n")

    # 1. Config
    from aria.config import settings
    print(f"Ollama: {settings.ollama_base_url}")
    print(f"Qdrant: {settings.qdrant_url}\n")

    # 2. Router
    print("[1] Router (Ollama)...")
    from aria.ui.app import _run_router
    try:
        router = _run_router("Qué es la madurez digital?")
        print(f"    OK -> {router['agent']}: {router['reason'][:60]}...")
    except Exception as e:
        print(f"    ERROR: {type(e).__name__}: {e}")
        return

    # 3. Corpus
    print("\n[2] Corpus (Qdrant + embeddings)...")
    from aria.agents.orchestrator import AGENT_TOOLS
    tools_cfg = AGENT_TOOLS[router["agent"]]
    try:
        corpus = tools_cfg["corpus"].invoke("Qué es la madurez digital?")
        print(f"    OK - {len(corpus)} caracteres de contexto")
    except Exception as e:
        print(f"    ERROR: {type(e).__name__}: {e}")
        return

    # 4. Síntesis (streaming)
    print("\n[3] Síntesis (Ollama streaming)...")
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_ollama import ChatOllama

    llm = ChatOllama(
        model=settings.ollama_llm_model,
        base_url=settings.ollama_base_url,
        temperature=0.1,
        num_predict=200,
    )
    prompt = f"Contexto:\n{corpus[:500]}...\n\nPregunta: Qué es la madurez digital? Responde en 2-3 frases."
    try:
        full = ""
        async for chunk in llm.astream([
            SystemMessage(content=tools_cfg["prompt"][:500]),
            HumanMessage(content=prompt),
        ]):
            if chunk.content:
                full += chunk.content
        print(f"    OK - respuesta ({len(full)} chars)")
        print(f"    Preview: {full[:150]}...")
    except Exception as e:
        print(f"    ERROR: {type(e).__name__}: {e}")
        return

    print("\n=== Todo OK. Chainlit debería funcionar igual. ===")


if __name__ == "__main__":
    asyncio.run(main())
