"""
ARIA Multi-Agent Orchestrator — 3 agentes especializados.

Graph: START -> router -> [agua_agent | sector_agent | matching_agent] -> END

Agentes:
  agua_agent    : gestión hídrica + normativa ambiental (RAG + web)
  sector_agent  : conocimiento sectorial cosmético (RAG + web)
  matching_agent: catálogo de soluciones y proveedores DIGIPYC (solo RAG)
"""

import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from aria.agents.prompts import (
    AGUA_SYSTEM,
    MATCHING_SYSTEM,
    ROUTER_SYSTEM,
    SECTOR_SYSTEM,
)
from aria.agents.state import ARIAState
from aria.config import settings
from aria.tools.retriever import agua_corpus_search, matching_corpus_search, sector_corpus_search
from aria.tools.web_search import agua_web_search, sector_web_search

AGENT_META = {
    "agua_agent":    {"emoji": "💧", "label": "Optimización del Agua",    "color": "#10B981"},
    "sector_agent":  {"emoji": "🏭", "label": "Sector Cosmético",         "color": "#6366F1"},
    "matching_agent":{"emoji": "🔍", "label": "Matching de Soluciones",   "color": "#F59E0B"},
}

AGENT_TOOLS = {
    "agua_agent": {
        "corpus": agua_corpus_search,
        "web":    agua_web_search,
        "prompt": AGUA_SYSTEM,
        "has_web": True,
    },
    "sector_agent": {
        "corpus": sector_corpus_search,
        "web":    sector_web_search,
        "prompt": SECTOR_SYSTEM,
        "has_web": True,
    },
    "matching_agent": {
        "corpus": matching_corpus_search,
        "web":    None,
        "prompt": MATCHING_SYSTEM,
        "has_web": False,  # El catálogo es suficiente; no necesita web
    },
}

# Señales de que se necesita información actualizada de internet
WEB_KEYWORDS = [
    "actual", "hoy", "2024", "2025", "2026", "precio", "coste",
    "convocatoria", "estado de transposicion", "ultima", "reciente",
    "vigente", "nueva", "actualizada", "cambio", "plazo", "ayuda", "subvencion",
]


def _router_llm() -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_router_model,
        base_url=settings.ollama_base_url,
        temperature=0.0,
        num_predict=60,
    )


def _agent_llm() -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_llm_model,
        base_url=settings.ollama_base_url,
        temperature=0.1,
        num_predict=2048,
    )


# ── Graph Nodes ──────────────────────────────────────────────────────────────

def router_node(state: ARIAState) -> dict:
    """Analiza la pregunta y selecciona el agente correcto."""
    question = state["messages"][-1].content

    response = _router_llm().invoke([
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
        reason = "Fallback por parsing"

    if agent not in AGENT_META:
        agent = "sector_agent"

    return {
        "active_agent": agent,
        "question": question,
        "routing_reason": reason,
    }


def agent_node(state: ARIAState) -> dict:
    """
    Ejecuta el agente seleccionado:
    1. Recuperación del corpus (siempre)
    2. Búsqueda web si la pregunta lo requiere (solo agua y sector)
    3. Síntesis con el prompt especializado del agente
    """
    agent_name  = state["active_agent"]
    question    = state["question"]
    tools_cfg   = AGENT_TOOLS[agent_name]
    tools_used  = []

    # 1. Corpus RAG (siempre)
    corpus_result = tools_cfg["corpus"].invoke(question)
    tools_used.append(tools_cfg["corpus"].name)
    context_parts = [f"## Documentos del corpus\n\n{corpus_result}"]

    # 2. Web search (solo agentes con web y si la pregunta lo requiere)
    if tools_cfg["has_web"]:
        needs_web = any(kw in question.lower() for kw in WEB_KEYWORDS)
        if needs_web:
            web_result = tools_cfg["web"].invoke(question)
            tools_used.append(tools_cfg["web"].name)
            context_parts.append(f"## Búsqueda web actualizada\n\n{web_result}")

    context = "\n\n---\n\n".join(context_parts)

    # 3. Síntesis
    conversation_history = [
        m for m in state["messages"]
        if isinstance(m, (HumanMessage, AIMessage))
    ]

    synthesis_prompt = (
        f"Contexto recuperado:\n\n{context}\n\n---\n\n"
        f"Pregunta del usuario: {question}\n\n"
        "Genera tu respuesta citando siempre las fuentes."
    )

    response = _agent_llm().invoke([
        SystemMessage(content=tools_cfg["prompt"]),
        *conversation_history[:-1],
        HumanMessage(content=synthesis_prompt),
    ])

    # Construir header de respuesta
    meta = AGENT_META[agent_name]
    tools_labels = {
        "agua_corpus_search":    "Corpus Agua",
        "sector_corpus_search":  "Corpus Sector",
        "matching_corpus_search":"Catálogo DIGIPYC",
        "agua_web_search":       "Web (normativa ambiental)",
        "sector_web_search":     "Web (digitalización)",
    }
    tools_str = " + ".join(tools_labels.get(t, t) for t in tools_used)

    header = (
        f"{meta['emoji']} **{meta['label']}**"
        + (f"  |  _{state['routing_reason']}_" if state["routing_reason"] else "")
        + f"\n> Fuentes: {tools_str}"
    )

    full_response = f"{header}\n\n---\n\n{response.content}"
    return {"messages": [AIMessage(content=full_response)]}


def route_to_agent(state: ARIAState) -> str:
    return state["active_agent"]


# ── Build Graph ──────────────────────────────────────────────────────────────

def build_graph():
    """Construye y compila el grafo ARIA con 3 agentes y memoria."""
    builder = StateGraph(ARIAState)

    builder.add_node("router",         router_node)
    builder.add_node("agua_agent",     agent_node)
    builder.add_node("sector_agent",   agent_node)
    builder.add_node("matching_agent", agent_node)

    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "agua_agent":     "agua_agent",
            "sector_agent":   "sector_agent",
            "matching_agent": "matching_agent",
        },
    )
    builder.add_edge("agua_agent",     END)
    builder.add_edge("sector_agent",   END)
    builder.add_edge("matching_agent", END)

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


graph = build_graph()
