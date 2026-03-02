"""
ARIA — Chainlit UI con streaming
3 agentes: Agua | Sector | Matching

Run:
    chainlit run aria/ui/app.py --port 8000
"""

from dotenv import load_dotenv

load_dotenv()  # Cargar .env antes de imports de LangChain (traces LangSmith)

import json

import chainlit as cl
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from aria.agents.orchestrator import (
    AGENT_META,
    AGENT_TOOLS,
    WEB_KEYWORDS,
    graph,
)
from aria.agents.prompts import ROUTER_SYSTEM
from aria.config import settings

WELCOME = (
    "## Bienvenido a **ARIA** — Adaptive Intelligence for Advisory\n\n"
    "Soy el asistente especializado para el sector de **perfumería y cosmética**. "
    "Puedo ayudarte con:\n\n"
    "\U0001f4a7 **Optimización del agua** — CIP, huella hídrica, Dry Factory, UWWTD, normativa ambiental\n"
    "\U0001f3ed **Sector cosmético** — madurez digital, roadmaps, estrategia, NIS2, benchmarks sectoriales\n"
    "\U0001f50d **Matching de soluciones** — catálogo DIGIPYC de proveedores y herramientas tecnológicas\n\n"
    "**¿En qué puedo ayudarte hoy?**"
)

TOOLS_LABELS = {
    "agua_corpus_search":    "Corpus Agua",
    "sector_corpus_search":  "Corpus Sector",
    "matching_corpus_search":"Catálogo DIGIPYC",
    "agua_web_search":       "Web (normativa ambiental)",
    "sector_web_search":     "Web (digitalización)",
}


@cl.on_chat_start
async def on_start():
    cl.user_session.set("session_id", cl.context.session.id)
    await cl.Message(content=WELCOME).send()


@cl.on_message
async def on_message(message: cl.Message):
    session_id = cl.user_session.get("session_id", "default")
    config = {"configurable": {"thread_id": session_id}}
    question = message.content

    # Step 1: Routing
    status_msg = cl.Message(content="*Analizando tu pregunta...*")
    await status_msg.send()

    router_result = await cl.make_async(_run_router)(question)
    agent_name = router_result.get("agent", "sector_agent")
    if agent_name not in AGENT_META:
        agent_name = "sector_agent"
    reason = router_result.get("reason", "")
    meta = AGENT_META[agent_name]
    tools_cfg = AGENT_TOOLS.get(agent_name) or AGENT_TOOLS["sector_agent"]
    has_web = tools_cfg.get("has_web", False)
    corpus_tool = tools_cfg.get("corpus")
    web_tool = tools_cfg.get("web")

    status_msg.content = (
        f"{meta['emoji']} **{meta['label']}** seleccionado\n"
        f"> _{reason}_\n\n"
        f"*Buscando en documentos...*"
    )
    await status_msg.update()

    try:
        # Step 2: Retrieval
        tools_used = []
        if not corpus_tool:
            raise ValueError("No hay corpus configurado para este agente")
        corpus_result = await cl.make_async(corpus_tool.invoke)(question)
        tools_used.append(corpus_tool.name)
        context_parts = [f"## Documentos del corpus\n\n{corpus_result}"]

        if has_web and web_tool:
            needs_web = any(kw in question.lower() for kw in WEB_KEYWORDS)
            if needs_web:
                status_msg.content = (
                    f"{meta['emoji']} **{meta['label']}** seleccionado\n"
                    f"> _{reason}_\n\n"
                    f"*Buscando información actualizada en web...*"
                )
                await status_msg.update()
                web_result = await cl.make_async(web_tool.invoke)(question)
                tools_used.append(web_tool.name)
                context_parts.append(f"## Búsqueda web actualizada\n\n{web_result}")

        context = "\n\n---\n\n".join(context_parts)
        tools_str = " + ".join(TOOLS_LABELS.get(t, t) for t in tools_used)
        header = (
            f"{meta['emoji']} **{meta['label']}**"
            + (f"  |  _{reason}_" if reason else "")
            + f"\n> Fuentes: {tools_str}\n\n---\n\n"
        )

        status_msg.content = header
        await status_msg.update()

        # Step 3: Streaming synthesis
        synthesis_prompt = (
            f"Contexto recuperado:\n\n{context}\n\n---\n\n"
            f"Pregunta del usuario: {question}\n\n"
            "Genera tu respuesta citando siempre las fuentes."
        )

        llm = ChatOllama(
            model=settings.ollama_llm_model,
            base_url=settings.ollama_base_url,
            temperature=0.1,
            num_predict=2048,
        )

        full_text = header
        async for chunk in llm.astream([
            SystemMessage(content=tools_cfg["prompt"]),
            HumanMessage(content=synthesis_prompt),
        ]):
            if chunk.content:
                full_text += chunk.content
                await status_msg.stream_token(chunk.content)

        status_msg.content = full_text
        await status_msg.update()

        # Guardar en memoria del grafo para multi-turn
        await cl.make_async(graph.invoke)(
            {
                "messages": [
                    HumanMessage(content=question),
                    AIMessage(content=full_text),
                ],
                "active_agent":   agent_name,
                "question":       question,
                "routing_reason": reason,
            },
            config=config,
        )
    except Exception as e:
        await cl.Message(
            content=f"**Error (corpus o síntesis):** {type(e).__name__}: {str(e)[:400]}\n\n"
            "Comprueba: túnel SSH activo, Qdrant local en `./qdrant_data`, Ollama en RunPod."
        ).send()


def _run_router(question: str) -> dict:
    """Ejecuta el router LLM para seleccionar el agente."""
    llm = ChatOllama(
        model=settings.ollama_router_model,
        base_url=settings.ollama_base_url,
        temperature=0.0,
        num_predict=60,
    )
    response = llm.invoke([
        SystemMessage(content=ROUTER_SYSTEM),
        HumanMessage(content=f"Pregunta: {question}"),
    ])

    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1].replace("json", "").strip()
        parsed = json.loads(raw)
        agent = parsed.get("agent", "sector_agent")
        reason = parsed.get("reason", "")
    except (json.JSONDecodeError, KeyError):
        agent = "sector_agent"
        reason = "Fallback"

    if agent not in AGENT_META:
        agent = "sector_agent"

    return {"agent": agent, "reason": reason}


@cl.on_chat_end
async def on_end():
    pass
