"""
ARIA — RAGAS Evaluation (OpenAI GPT-4.1-mini as judge)
15 preguntas: 5 agua + 5 sector + 5 matching

Uso:
    python scripts/ragas_eval.py              # Fase 1 + 2 completo
    python scripts/ragas_eval.py --phase2     # Solo RAGAS (usa caché Fase 1)
"""

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import warnings
import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    from ragas import EvaluationDataset, SingleTurnSample, evaluate
    from ragas.dataset_schema import MultiTurnSample
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import (
        ContextEntityRecall, FactualCorrectness, Faithfulness,
        LLMContextRecall, NoiseSensitivity, ResponseRelevancy,
    )
    from ragas.metrics import AnswerCorrectness, AnswerSimilarity, TopicAdherenceScore
    from ragas.run_config import RunConfig
    import ragas.messages as r

from rich.console import Console
from rich.table import Table

from aria.config import settings
from aria.tools.retriever import _make_retriever

load_dotenv()

console = Console(force_terminal=True)

CACHE_FILE     = Path("./ragas_phase1_cache.json")
EVALUATOR_MODEL = "gpt-4.1-mini"

# ── Limpieza de respuestas ────────────────────────────────────────────────────

def clean_response(answer: str) -> str:
    """Elimina headers de ARIA para que RAGAS evalúe solo el contenido."""
    answer = re.sub(r'^[^\n]*\*\*Optimización del Agua\*\*[^\n]*\n', '', answer)
    answer = re.sub(r'^[^\n]*\*\*Sector Cosmético\*\*[^\n]*\n', '', answer)
    answer = re.sub(r'^[^\n]*\*\*Matching de Soluciones\*\*[^\n]*\n', '', answer)
    answer = re.sub(r'^>\s*Fuentes:[^\n]*\n', '', answer, flags=re.MULTILINE)
    answer = re.sub(r'^---\s*\n', '', answer, flags=re.MULTILINE)
    answer = re.sub(r'\*\*WARNING:\*\*[^\n]*(?:\n\[Web:[^\]]*\])?\s*$', '', answer)
    return answer.strip()


def deduplicate_contexts(contexts: list[str]) -> list[str]:
    seen, unique = set(), []
    for ctx in contexts:
        norm = ctx.strip()
        if norm and norm not in seen:
            seen.add(norm)
            unique.append(ctx)
    return unique


# ── Golden Dataset — 15 preguntas ─────────────────────────────────────────────

GOLDEN_DATASET = [
    # ── agua_agent (5) ──────────────────────────────────────────────────────
    {
        "question": "¿Cuál es la principal fuente de consumo de agua en una fábrica cosmética y cómo se puede reducir?",
        "ground_truth": "La principal fuente son los procesos de limpieza CIP. Se puede reducir mediante automatización de lavados, reutilización del agua de rechazo de osmosis inversa y estandarización de protocolos.",
        "expected_agent": "agua_agent",
        "reference_topics": ["agua", "cosmetica", "CIP", "eficiencia hidrica"],
    },
    {
        "question": "¿Qué establece la directiva UWWTD sobre el tratamiento de aguas residuales?",
        "ground_truth": "La UWWTD establece normas para la recogida, tratamiento y vertido de aguas residuales urbanas, exigiendo tratamiento con reducción de DBO5 y sólidos en suspensión.",
        "expected_agent": "agua_agent",
        "reference_topics": ["agua", "UWWTD", "normativa", "aguas residuales"],
    },
    {
        "question": "¿Qué es el concepto Dry Factory y cómo se aplica al sector cosmético?",
        "ground_truth": "Dry Factory es un modelo que minimiza el consumo de agua aplicando CIP optimizado, recirculación, osmosis inversa y formulaciones waterless.",
        "expected_agent": "agua_agent",
        "reference_topics": ["agua", "Dry Factory", "cosmetica", "sostenibilidad"],
    },
    {
        "question": "¿Cómo se calcula la huella hídrica en la industria cosmética?",
        "ground_truth": "Se calcula siguiendo ISO 14046, considerando agua directa en producción y agua indirecta en la cadena de suministro de materias primas.",
        "expected_agent": "agua_agent",
        "reference_topics": ["agua", "huella hidrica", "ISO 14046", "cosmetica"],
    },
    {
        "question": "¿Qué tecnologías avanzadas de tratamiento de efluentes existen para la industria cosmética?",
        "ground_truth": "Osmosis inversa, tratamiento biológico avanzado, electrocoagulación y sistemas de tratamiento de aguas con alto COD sin generación de fangos.",
        "expected_agent": "agua_agent",
        "reference_topics": ["agua", "efluentes", "tratamiento", "cosmetica"],
    },

    # ── sector_agent (5) ─────────────────────────────────────────────────────
    {
        "question": "¿Cuál es el nivel de madurez digital del sector cosmético en España?",
        "ground_truth": "El sector cosmético en España presenta madurez digital media-baja, con diferencias entre grandes empresas y PYMEs. Las áreas de mejora incluyen ERP/MES, ciberseguridad e IoT.",
        "expected_agent": "sector_agent",
        "reference_topics": ["transformacion digital", "madurez digital", "cosmetica", "España"],
    },
    {
        "question": "¿Qué implica la directiva NIS2 para el sector cosmético?",
        "ground_truth": "NIS2 establece requisitos de ciberseguridad para infraestructuras conectadas, afectando a fábricas con IoT y SCADA, requiriendo gestión de riesgos y notificación de incidentes.",
        "expected_agent": "sector_agent",
        "reference_topics": ["transformacion digital", "NIS2", "ciberseguridad", "cosmetica"],
    },
    {
        "question": "¿Cómo está estructurado el roadmap de digitalización del sector cosmético español?",
        "ground_truth": "El roadmap incluye diagnóstico de madurez, priorización de áreas, selección de tecnologías ERP/MES/PLM, definición de KPIs y plan de formación con cronograma.",
        "expected_agent": "sector_agent",
        "reference_topics": ["transformacion digital", "roadmap", "cosmetica", "ERP"],
    },
    {
        "question": "¿Cuáles son los objetivos del proyecto DIGIPYC para el sector?",
        "ground_truth": "DIGIPYC impulsa la digitalización del sector de perfumería y cosmética mediante diagnóstico sectorial, catálogo de soluciones tecnológicas y hoja de ruta de transformación digital.",
        "expected_agent": "sector_agent",
        "reference_topics": ["transformacion digital", "DIGIPYC", "sector cosmetico"],
    },
    {
        "question": "¿Cuáles son las principales barreras para la adopción de IoT en el sector cosmético?",
        "ground_truth": "Las barreras son: coste de implementación, falta de personal cualificado, integración con sistemas legacy, preocupaciones de ciberseguridad y resistencia al cambio organizacional.",
        "expected_agent": "sector_agent",
        "reference_topics": ["transformacion digital", "IoT", "barreras", "cosmetica"],
    },

    # ── matching_agent (5) ───────────────────────────────────────────────────
    {
        "question": "¿Qué soluciones tecnológicas están disponibles en el catálogo DIGIPYC para control de producción?",
        "ground_truth": "El catálogo DIGIPYC incluye sistemas MES para control de producción batch, plataformas IoT para monitorización y soluciones ERP integradas específicas para el sector cosmético.",
        "expected_agent": "matching_agent",
        "reference_topics": ["soluciones tecnologicas", "DIGIPYC", "MES", "produccion"],
    },
    {
        "question": "¿Qué herramienta del catálogo DIGIPYC permite usar IA para optimizar formulaciones cosméticas?",
        "ground_truth": "El catálogo DIGIPYC incluye soluciones de IA para formulación que permiten reducir el ensayo-error y optimizar el desarrollo de nuevas fórmulas cosméticas.",
        "expected_agent": "matching_agent",
        "reference_topics": ["soluciones tecnologicas", "IA", "formulacion", "cosmetica"],
    },
    {
        "question": "¿Qué soluciones de visión artificial para control de calidad están en el catálogo DIGIPYC?",
        "ground_truth": "El catálogo incluye soluciones de visión artificial para inspección de calidad, detección de defectos en packaging y verificación de etiquetado en línea de producción.",
        "expected_agent": "matching_agent",
        "reference_topics": ["soluciones tecnologicas", "vision artificial", "calidad", "packaging"],
    },
    {
        "question": "¿Qué soluciones de ciberseguridad para entornos OT/IoT industriales hay en el catálogo DIGIPYC?",
        "ground_truth": "El catálogo DIGIPYC incluye soluciones de ciberseguridad industrial para proteger entornos OT y sistemas IoT conectados en fábricas cosméticas, alineadas con NIS2.",
        "expected_agent": "matching_agent",
        "reference_topics": ["soluciones tecnologicas", "ciberseguridad", "OT", "NIS2"],
    },
    {
        "question": "¿Qué proveedores de trazabilidad de ingredientes aparecen en el catálogo DIGIPYC?",
        "ground_truth": "El catálogo incluye soluciones de trazabilidad de ingredientes y cadena de suministro para el sector cosmético, con tecnologías blockchain e IA.",
        "expected_agent": "matching_agent",
        "reference_topics": ["soluciones tecnologicas", "trazabilidad", "ingredientes", "blockchain"],
    },
]


# ── Fase 1: Ejecutar preguntas en ARIA ────────────────────────────────────────

def run_aria_for_evaluation(questions: list[dict]) -> list[dict]:
    from aria.agents.orchestrator import graph

    results = []
    for i, item in enumerate(questions):
        question = item["question"]
        expected = item["expected_agent"]

        console.print(f"[cyan][{i+1}/{len(questions)}][/cyan] {question[:65]}...")

        config = {"configurable": {"thread_id": f"ragas-eval-v3-{i}"}}
        result = graph.invoke(
            {
                "messages": [HumanMessage(content=question)],
                "active_agent": "",
                "question": question,
                "routing_reason": "",
            },
            config=config,
        )

        actual_agent = result["active_agent"]
        answer       = result["messages"][-1].content

        category  = actual_agent.replace("_agent", "")
        retriever = _make_retriever(categories=[category], k=8)
        contexts  = deduplicate_contexts([d.page_content for d in retriever.invoke(question)])

        routing_ok = actual_agent == expected
        console.print(
            f"  Agente: {actual_agent} "
            f"{'[green]OK[/green]' if routing_ok else '[red]MISS[/red]'} "
            f"| Contextos: {len(contexts)}"
        )

        results.append({
            "question":       question,
            "answer":         answer,
            "contexts":       contexts,
            "ground_truth":   item["ground_truth"],
            "expected_agent": expected,
            "actual_agent":   actual_agent,
            "routing_correct": routing_ok,
        })

    CACHE_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f"[green]Fase 1 cacheada en {CACHE_FILE}[/green]")
    return results


# ── Fase 2A: RAG metrics ──────────────────────────────────────────────────────

def run_rag_evaluation(results: list[dict]):
    console.rule("[bold cyan]RAGAS — RAG Metrics (GPT-4.1-mini)[/bold cyan]")

    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model=EVALUATOR_MODEL, max_tokens=8192))
    evaluator_emb = LangchainEmbeddingsWrapper(OpenAIEmbeddings())

    samples = [
        SingleTurnSample(
            user_input=res["question"],
            response=clean_response(res["answer"]),
            retrieved_contexts=deduplicate_contexts(res["contexts"]) or ["No context"],
            reference=res["ground_truth"],
        )
        for res in results
    ]

    run_config = RunConfig(timeout=600, max_retries=5, max_workers=4)
    return evaluate(
        dataset=EvaluationDataset(samples=samples),
        metrics=[Faithfulness(), LLMContextRecall(), FactualCorrectness(),
                 ResponseRelevancy(), ContextEntityRecall(), NoiseSensitivity()],
        llm=evaluator_llm,
        embeddings=evaluator_emb,
        run_config=run_config,
    )


# ── Fase 2B: Agent metrics ────────────────────────────────────────────────────

async def run_agent_evaluation(results: list[dict], golden: list[dict]):
    console.rule("[bold cyan]RAGAS — Agent Metrics (GPT-4.1-mini)[/bold cyan]")

    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model=EVALUATOR_MODEL, max_tokens=8192))
    evaluator_emb = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
    similarity = AnswerSimilarity(embeddings=evaluator_emb)
    goal_scorer = AnswerCorrectness(llm=evaluator_llm, embeddings=evaluator_emb, answer_similarity=similarity)
    topic_scorer = TopicAdherenceScore(llm=evaluator_llm, mode="precision")

    agent_scores = []
    for i, (res, gold) in enumerate(zip(results, golden)):
        console.print(f"[cyan][{i+1}/{len(results)}][/cyan] {res['question'][:50]}...")
        cleaned = clean_response(res.get("answer", ""))
        trace = [r.HumanMessage(content=res["question"]),
                 r.AIMessage(content=cleaned, tool_calls=[])]

        try:
            goal_score = await goal_scorer.single_turn_ascore(
                SingleTurnSample(user_input=res["question"], response=cleaned, reference=gold["ground_truth"])
            )
        except Exception as e:
            console.print(f"  [yellow]AnswerCorrectness error: {e}[/yellow]")
            goal_score = None

        try:
            topic_score = await topic_scorer.multi_turn_ascore(
                MultiTurnSample(user_input=trace, reference_topics=gold["reference_topics"])
            )
        except Exception as e:
            console.print(f"  [yellow]TopicAdherence error: {e}[/yellow]")
            topic_score = None

        agent_scores.append({
            "question":            res["question"],
            "actual_agent":        res["actual_agent"],
            "agent_goal_accuracy": float(goal_score) if goal_score is not None else None,
            "topic_adherence":     float(topic_score) if topic_score is not None else None,
        })
        console.print(f"  Goal={goal_score}  Topic={topic_score}")

    return agent_scores


# ── Resultados ────────────────────────────────────────────────────────────────

RAG_METRIC_COLS = [
    ("faithfulness",                     "Faith"),
    ("context_recall",                   "CtxRec"),
    ("factual_correctness(mode=f1)",     "FactCorr"),
    ("answer_relevancy",                 "RespRel"),
    ("context_entity_recall",            "EntRec"),
    ("noise_sensitivity(mode=relevant)", "Noise"),
]

def print_results(results, rag_results, agent_scores):
    correct = sum(1 for r_ in results if r_["routing_correct"])
    total   = len(results)
    console.rule("[bold]Routing Accuracy[/bold]")
    console.print(f"  {correct}/{total} ({correct/total*100:.0f}%)")

    df = rag_results.to_pandas()
    console.print(f"[dim]Columnas RAGAS: {list(df.columns)}[/dim]")

    # Tabla por pregunta
    table = Table(title="RAGAS RAG — por pregunta")
    table.add_column("Pregunta", max_width=35)
    table.add_column("Agente", width=8)
    for _, label in RAG_METRIC_COLS:
        table.add_column(label, justify="right")

    for i, row in df.iterrows():
        q     = results[i]["question"][:33]
        agent = results[i]["actual_agent"].replace("_agent", "")
        vals  = [f"{row.get(col):.3f}" if row.get(col) is not None and pd.notna(row.get(col)) else "N/A"
                 for col, _ in RAG_METRIC_COLS]
        table.add_row(q, agent, *vals)
    console.print(table)

    # Promedios globales
    console.rule("[bold]RAG — Promedios Globales[/bold]")
    for col, label in RAG_METRIC_COLS:
        if col in df.columns and not df[col].dropna().empty:
            console.print(f"  {label:<30} {df[col].dropna().mean():.3f}")

    # Promedios por agente
    console.rule("[bold]RAG — Por Agente[/bold]")
    for agent_name in ["agua_agent", "sector_agent", "matching_agent"]:
        indices = [i for i, r_ in enumerate(results) if r_["actual_agent"] == agent_name]
        if indices:
            console.print(f"\n  [bold]{agent_name}[/bold]")
            for col, label in RAG_METRIC_COLS:
                if col in df.columns:
                    vals = [df.iloc[j][col] for j in indices if pd.notna(df.iloc[j].get(col))]
                    if vals:
                        console.print(f"    {label:<30} {sum(vals)/len(vals):.3f}")

    # Agent metrics
    console.rule("[bold]Agent Metrics[/bold]")
    agent_table = Table(title="RAGAS Agent — por pregunta")
    agent_table.add_column("Pregunta", max_width=35)
    agent_table.add_column("Agente", width=8)
    agent_table.add_column("GoalAcc", justify="right")
    agent_table.add_column("TopicAdh", justify="right")
    for s in agent_scores:
        ga = f"{s['agent_goal_accuracy']:.3f}" if s["agent_goal_accuracy"] is not None else "N/A"
        ta = f"{s['topic_adherence']:.3f}"     if s["topic_adherence"]     is not None else "N/A"
        agent_table.add_row(s["question"][:33], s["actual_agent"].replace("_agent",""), ga, ta)
    console.print(agent_table)

    console.rule("[bold]Agent — Promedios Globales[/bold]")
    for metric in ["agent_goal_accuracy", "topic_adherence"]:
        vals = [s[metric] for s in agent_scores if s[metric] is not None]
        if vals:
            console.print(f"  {metric:<30} {sum(vals)/len(vals):.3f}")

    # Guardar JSON + CSV
    output_path = Path("./ragas_evaluation_results.json")
    export = {
        "routing_accuracy": correct / total,
        "rag_global": {
            label: round(float(df[col].dropna().mean()), 4)
            for col, label in RAG_METRIC_COLS
            if col in df.columns and not df[col].dropna().empty
        },
        "agent_global": {
            metric: round(sum(s[metric] for s in agent_scores if s[metric] is not None) /
                         max(1, sum(1 for s in agent_scores if s[metric] is not None)), 4)
            for metric in ["agent_goal_accuracy", "topic_adherence"]
        },
    }
    output_path.write_text(json.dumps(export, ensure_ascii=False, indent=2), encoding="utf-8")
    rag_results.to_pandas().to_csv("./ragas_evaluation_results.csv", index=False, encoding="utf-8")
    console.print(f"\n[green]Resultados guardados.[/green]")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ARIA RAGAS Evaluation — 3 agentes")
    parser.add_argument("--phase2", action="store_true", help="Usar caché de Fase 1")
    args = parser.parse_args()

    console.rule("[bold cyan]ARIA — Evaluación RAGAS (15 preguntas, 3 agentes)[/bold cyan]")
    console.print(f"[dim]Evaluator: {EVALUATOR_MODEL}[/dim]")

    if args.phase2 and CACHE_FILE.exists():
        console.print(f"[yellow]Usando caché: {CACHE_FILE}[/yellow]")
        results = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    else:
        results = run_aria_for_evaluation(GOLDEN_DATASET)

    rag_results  = run_rag_evaluation(results)
    agent_scores = asyncio.run(run_agent_evaluation(results, GOLDEN_DATASET))
    print_results(results, rag_results, agent_scores)


if __name__ == "__main__":
    main()
