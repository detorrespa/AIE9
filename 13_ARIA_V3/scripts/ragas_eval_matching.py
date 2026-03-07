"""
ARIA — RAGAS Evaluation solo para el agente matching
5 preguntas sobre catálogo DIGIPYC, soluciones tecnológicas y proveedores.

Uso:
    python scripts/ragas_eval_matching.py              # Fase 1 + 2 completo
    python scripts/ragas_eval_matching.py --phase2   # Solo RAGAS (usa caché Fase 1)
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

from aria.tools.retriever import _make_retriever

load_dotenv()

console = Console(force_terminal=True)

CACHE_FILE = Path("./ragas_matching_phase1_cache.json")
EVALUATOR_MODEL = "gpt-4.1-mini"

# ── Golden Dataset — 5 preguntas matching (ground truth de matching_profiles.json) ─

GOLDEN_MATCHING = [
    {
        "question": "¿Qué soluciones tecnológicas están disponibles en el catálogo DIGIPYC para control de producción?",
        "ground_truth": "ACK LOGIC ofrece Gladdis Smed, sistemas BATCH y MES (Manufacturing Execution System) para Paperless Factory, integración SCADA/DCS con ERP. NEKTIU & DataAI tiene APS (Advanced Planning & Scheduling), integración ERP/MES/CRM. BARBARA ofrece MLOps en edge y metros predictivos virtuales. ÓRBITA INGENIERÍA tiene visión artificial para inspección de etiquetas y packaging en línea.",
        "reference_topics": ["MES", "produccion", "BATCH", "ACK LOGIC", "NEKTIU"],
    },
    {
        "question": "¿Qué herramienta del catálogo DIGIPYC permite usar IA para optimizar formulaciones cosméticas?",
        "ground_truth": "OGA.ai ofrece oga.Alchemy, plataforma SaaS de IA para optimización de formulaciones cosméticas y químicas, replicación de fórmulas y sustitución de ingredientes. HI IBERIA tiene FragIA con RAG, simulaciones bioquímicas y NLP para formulación de fragancias y cosméticos. AINIA ofrece plataforma SaaS NPD y SKINSPECTOR (robótica colaborativa + visión espectral + IA para evaluación de piel).",
        "reference_topics": ["IA", "formulacion", "OGA.ai", "FragIA", "HI IBERIA"],
    },
    {
        "question": "¿Qué soluciones de visión artificial para control de calidad están en el catálogo DIGIPYC?",
        "ground_truth": "AINIA tiene Termoseal (visión térmica para detección de defectos en sellados) y SKINSPECTOR (visión espectral + IA para evaluación de piel y producto). ÓRBITA INGENIERÍA ofrece visión artificial para inspección 360° de etiquetas en envases cilíndricos y detección de defectos en packaging. VICOMTECH tiene control de calidad automatizado y procesamiento visual.",
        "reference_topics": ["vision artificial", "calidad", "AINIA", "ÓRBITA", "Termoseal"],
    },
    {
        "question": "¿Qué soluciones de ciberseguridad para entornos OT/IoT industriales hay en el catálogo DIGIPYC?",
        "ground_truth": "FUNDITEC ofrece ciberseguridad OT/IoT, cumplimiento NIS2, alineado con IEC 62443. GMV tiene GMV-CERT, SOAR, pruebas de penetración para activos OT. IRONTEC ofrece CISO as a Service, EDR, SASE, ZTNA y cumplimiento NIS2/ENS. RANDSTAD DIGITAL tiene SOCaaS semiautomatizado con SIEM. XITASO IBERIA hace consultoría en ciberseguridad (NIS2, IEC 62443).",
        "reference_topics": ["ciberseguridad", "OT", "NIS2", "FUNDITEC", "GMV"],
    },
    {
        "question": "¿Qué proveedores de trazabilidad de ingredientes aparecen en el catálogo DIGIPYC?",
        "ground_truth": "FUNDITEC ofrece trazabilidad de cadena de suministro con Smart Contracts (blockchain), detección de anomalías en proveedores. CODE CONTRACT tiene gemelo digital certificado con blockchain, certificación inmutable de origen y calidad de ingredientes, trazabilidad de agua. Ambos cubren trazabilidad de materias primas e ingredientes para el sector cosmético.",
        "reference_topics": ["trazabilidad", "blockchain", "FUNDITEC", "CODE CONTRACT", "ingredientes"],
    },
]


def clean_response(answer: str) -> str:
    """Elimina headers de ARIA para que RAGAS evalúe solo el contenido."""
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


# ── Fase 1: Ejecutar preguntas en ARIA (solo matching) ─────────────────────────

def run_matching_for_evaluation(questions: list[dict]) -> list[dict]:
    from aria.agents.orchestrator import graph

    retriever = _make_retriever(categories=["matching"], k=8)
    results = []

    for i, item in enumerate(questions):
        question = item["question"]
        console.print(f"[cyan][{i+1}/{len(questions)}][/cyan] {question[:65]}...")

        config = {"configurable": {"thread_id": f"ragas-matching-{i}"}}
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
        answer = result["messages"][-1].content
        contexts = deduplicate_contexts([d.page_content for d in retriever.invoke(question)])

        routing_ok = actual_agent == "matching_agent"
        console.print(
            f"  Agente: {actual_agent} "
            f"{'[green]OK[/green]' if routing_ok else '[yellow]MISS[/yellow]'} "
            f"| Contextos: {len(contexts)}"
        )

        results.append({
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "ground_truth": item["ground_truth"],
            "reference_topics": item["reference_topics"],
            "actual_agent": actual_agent,
        })

    CACHE_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f"[green]Fase 1 cacheada en {CACHE_FILE}[/green]")
    return results


# ── Fase 2A: RAG metrics ──────────────────────────────────────────────────────

def run_rag_evaluation(results: list[dict]):
    console.rule("[bold cyan]RAGAS — RAG Metrics (matching agent)[/bold cyan]")

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
        metrics=[
            Faithfulness(),
            LLMContextRecall(),
            FactualCorrectness(),
            ResponseRelevancy(),
            ContextEntityRecall(),
            NoiseSensitivity(),
        ],
        llm=evaluator_llm,
        embeddings=evaluator_emb,
        run_config=run_config,
    )


# ── Fase 2B: Agent metrics ──────────────────────────────────────────────────────

async def run_agent_evaluation(results: list[dict], golden: list[dict]):
    console.rule("[bold cyan]RAGAS — Agent Metrics (matching)[/bold cyan]")

    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model=EVALUATOR_MODEL, max_tokens=8192))
    evaluator_emb = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
    similarity = AnswerSimilarity(embeddings=evaluator_emb)
    goal_scorer = AnswerCorrectness(llm=evaluator_llm, embeddings=evaluator_emb, answer_similarity=similarity)
    topic_scorer = TopicAdherenceScore(llm=evaluator_llm, mode="precision")

    agent_scores = []
    for i, (res, gold) in enumerate(zip(results, golden)):
        console.print(f"[cyan][{i+1}/{len(results)}][/cyan] {res['question'][:50]}...")
        cleaned = clean_response(res.get("answer", ""))
        trace = [r.HumanMessage(content=res["question"]), r.AIMessage(content=cleaned, tool_calls=[])]

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
            "question": res["question"],
            "agent_goal_accuracy": float(goal_score) if goal_score is not None else None,
            "topic_adherence": float(topic_score) if topic_score is not None else None,
        })
        console.print(f"  Goal={goal_score}  Topic={topic_score}")

    return agent_scores


# ── Resultados ────────────────────────────────────────────────────────────────

RAG_METRIC_COLS = [
    ("faithfulness", "Faith"),
    ("context_recall", "CtxRec"),
    ("factual_correctness(mode=f1)", "FactCorr"),
    ("answer_relevancy", "RespRel"),
    ("context_entity_recall", "EntRec"),
    ("noise_sensitivity(mode=relevant)", "Noise"),
]


def print_results(results, rag_results, agent_scores):
    correct = sum(1 for r in results if r.get("actual_agent") == "matching_agent")
    total = len(results)
    if total:
        console.rule("[bold]Routing (matching esperado)[/bold]")
        console.print(f"  {correct}/{total} ({100*correct/total:.0f}%)")

    df = rag_results.to_pandas()
    console.print(f"[dim]Columnas RAGAS: {list(df.columns)}[/dim]")

    # Tabla por pregunta
    table = Table(title="RAGAS RAG — matching agent (5 preguntas)")
    table.add_column("Pregunta", max_width=45)
    for _, label in RAG_METRIC_COLS:
        table.add_column(label, justify="right")

    for i, row in df.iterrows():
        q = results[i]["question"][:43]
        vals = [
            f"{row.get(col):.3f}" if row.get(col) is not None and pd.notna(row.get(col)) else "N/A"
            for col, _ in RAG_METRIC_COLS
        ]
        table.add_row(q, *vals)
    console.print(table)

    # Promedios RAG
    console.rule("[bold]RAG — Promedios[/bold]")
    for col, label in RAG_METRIC_COLS:
        if col in df.columns and not df[col].dropna().empty:
            console.print(f"  {label:<30} {df[col].dropna().mean():.3f}")

    # Agent metrics
    console.rule("[bold]Agent Metrics[/bold]")
    agent_table = Table(title="RAGAS Agent — matching")
    agent_table.add_column("Pregunta", max_width=45)
    agent_table.add_column("GoalAcc", justify="right")
    agent_table.add_column("TopicAdh", justify="right")
    for s in agent_scores:
        ga = f"{s['agent_goal_accuracy']:.3f}" if s["agent_goal_accuracy"] is not None else "N/A"
        ta = f"{s['topic_adherence']:.3f}" if s["topic_adherence"] is not None else "N/A"
        agent_table.add_row(s["question"][:43], ga, ta)
    console.print(agent_table)

    console.rule("[bold]Agent — Promedios[/bold]")
    for metric in ["agent_goal_accuracy", "topic_adherence"]:
        vals = [s[metric] for s in agent_scores if s[metric] is not None]
        if vals:
            console.print(f"  {metric:<30} {sum(vals)/len(vals):.3f}")

    # Guardar
    output_path = Path("./ragas_matching_results.json")
    export = {
        "routing_accuracy": round(correct / total, 4) if total else None,
        "rag_metrics": {
            label: round(float(df[col].dropna().mean()), 4)
            for col, label in RAG_METRIC_COLS
            if col in df.columns and not df[col].dropna().empty
        },
        "agent_metrics": {
            metric: round(
                sum(s[metric] for s in agent_scores if s[metric] is not None)
                / max(1, sum(1 for s in agent_scores if s[metric] is not None)),
                4,
            )
            for metric in ["agent_goal_accuracy", "topic_adherence"]
        },
    }
    output_path.write_text(json.dumps(export, ensure_ascii=False, indent=2), encoding="utf-8")
    rag_results.to_pandas().to_csv("./ragas_matching_results.csv", index=False, encoding="utf-8")
    console.print(f"\n[green]Resultados: {output_path}[/green]")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ARIA RAGAS — solo agente matching")
    parser.add_argument("--phase2", action="store_true", help="Usar caché de Fase 1")
    args = parser.parse_args()

    console.rule("[bold cyan]ARIA — RAGAS Matching (5 preguntas)[/bold cyan]")
    console.print(f"[dim]Evaluator: {EVALUATOR_MODEL}[/dim]")

    if args.phase2 and CACHE_FILE.exists():
        console.print(f"[yellow]Usando caché: {CACHE_FILE}[/yellow]")
        results = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    else:
        results = run_matching_for_evaluation(GOLDEN_MATCHING)

    rag_results = run_rag_evaluation(results)
    agent_scores = asyncio.run(run_agent_evaluation(results, GOLDEN_MATCHING))
    print_results(results, rag_results, agent_scores)


if __name__ == "__main__":
    main()
