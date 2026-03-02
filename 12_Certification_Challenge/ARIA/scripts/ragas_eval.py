"""
ARIA — RAGAS Evaluation (OpenAI GPT-4.1-mini as judge)
11 synthetic questions (5 agua + 4 sector + 2 matching).

Includes:
  - 6 RAG metrics  (Faithfulness, LLMContextRecall, FactualCorrectness,
                     ResponseRelevancy, ContextEntityRecall, NoiseSensitivity)
  - 2 Agent metrics (AgentGoalAccuracy, TopicAdherence)

Usage:
    python scripts/ragas_eval.py              # Full run (Phase 1 + 2)
    python scripts/ragas_eval.py --phase2     # RAGAS only (uses cached Phase 1)
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
        ContextEntityRecall,
        FactualCorrectness,
        Faithfulness,
        LLMContextRecall,
        NoiseSensitivity,
        ResponseRelevancy,
    )
    from ragas.metrics import AgentGoalAccuracyWithReference, TopicAdherenceScore
    from ragas.run_config import RunConfig
    import ragas.messages as r

from rich.console import Console
from rich.table import Table

from aria.config import settings
from aria.tools.retriever import _make_retriever

load_dotenv()

console = Console(force_terminal=True)

CACHE_FILE = Path("./ragas_phase1_cache.json")
EVALUATOR_MODEL = "gpt-4.1-mini"


# ── Response cleaning ────────────────────────────────────────────────────────

def clean_response(answer: str) -> str:
    """Strip ARIA headers, routing info, and warnings from responses
    so RAGAS only evaluates the substantive answer content."""
    # Remove emoji header line (e.g. "💧 **Optimizacion del Agua** | _reason_")
    answer = re.sub(r'^[^\n]*\*\*Optimizaci[oó]n del Agua\*\*[^\n]*\n', '', answer)
    answer = re.sub(r'^[^\n]*\*\*Sector Cosm[eé]tico\*\*[^\n]*\n', '', answer)
    answer = re.sub(r'^[^\n]*\*\*Matching de Soluciones\*\*[^\n]*\n', '', answer)
    # Remove "> Fuentes: ..." line
    answer = re.sub(r'^>\s*Fuentes:[^\n]*\n', '', answer, flags=re.MULTILINE)
    # Remove leading "---" separator
    answer = re.sub(r'^---\s*\n', '', answer, flags=re.MULTILINE)
    # Remove WARNING blocks at the end
    answer = re.sub(r'\*\*WARNING:\*\*[^\n]*(?:\n\[Web:[^\]]*\])?\s*$', '', answer)
    # Remove leading/trailing whitespace
    return answer.strip()


def deduplicate_contexts(contexts: list[str]) -> list[str]:
    """Remove duplicate contexts."""
    seen = set()
    unique = []
    for ctx in contexts:
        normalized = ctx.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(ctx)
    return unique


# ── 10 Synthetic Questions (5 agua + 5 td) ──────────────────────────────────

GOLDEN_DATASET = [
    # ── agua_agent (5) ──
    {
        "question": "Cual es la principal fuente de consumo de agua en una fabrica cosmetica y como se puede reducir?",
        "ground_truth": "La principal fuente de consumo de agua son los procesos de limpieza CIP. Se puede reducir mediante automatizacion de lavados, reutilizacion del agua de rechazo de osmosis inversa, y estandarizacion de protocolos de limpieza.",
        "expected_agent": "agua_agent",
        "reference_topics": ["agua", "cosmetica", "CIP", "eficiencia hidrica"],
        "reference_tool_calls": ["agua_corpus_search"],
    },
    {
        "question": "Que establece la directiva UWWTD sobre el tratamiento de aguas residuales urbanas?",
        "ground_truth": "La UWWTD establece normas para la recogida, tratamiento y vertido de aguas residuales urbanas, exigiendo tratamiento primario con reduccion de al menos 20% DBO5 y 50% de solidos en suspension.",
        "expected_agent": "agua_agent",
        "reference_topics": ["agua", "UWWTD", "normativa", "aguas residuales"],
        "reference_tool_calls": ["agua_corpus_search"],
    },
    {
        "question": "Que es el concepto Dry Factory y como se aplica al sector cosmetico?",
        "ground_truth": "Dry Factory es un modelo de fabrica que minimiza o elimina el consumo de agua en los procesos productivos, aplicando tecnologias como CIP optimizado, recirculacion, osmosis inversa y formulaciones waterless.",
        "expected_agent": "agua_agent",
        "reference_topics": ["agua", "Dry Factory", "cosmetica", "sostenibilidad"],
        "reference_tool_calls": ["agua_corpus_search"],
    },
    {
        "question": "Como se calcula la huella hidrica en la industria cosmetica?",
        "ground_truth": "La huella hidrica se calcula siguiendo la norma ISO 14046, considerando el agua directa consumida en produccion, limpieza y refrigeracion, y el agua indirecta en la cadena de suministro de materias primas.",
        "expected_agent": "agua_agent",
        "reference_topics": ["agua", "huella hidrica", "ISO 14046", "cosmetica"],
        "reference_tool_calls": ["agua_corpus_search"],
    },
    {
        "question": "Que tecnologias avanzadas de tratamiento de efluentes existen para la industria cosmetica?",
        "ground_truth": "Existen tecnologias como osmosis inversa, tratamiento biologico avanzado, electrocoagulacion, y sistemas de tratamiento de aguas con alto contenido en COD sin generacion de fangos.",
        "expected_agent": "agua_agent",
        "reference_topics": ["agua", "efluentes", "tratamiento", "cosmetica"],
        "reference_tool_calls": ["agua_corpus_search"],
    },
    # ── sector_agent (4) ──
    {
        "question": "Cual es el nivel de madurez digital del sector cosmetico en Espana?",
        "ground_truth": "El sector cosmetico en Espana presenta un nivel de madurez digital medio-bajo, con diferencias significativas entre grandes empresas y PYMEs. Las areas de mejora incluyen integracion de sistemas ERP/MES, ciberseguridad y adopcion de IoT.",
        "expected_agent": "sector_agent",
        "reference_topics": ["transformacion digital", "madurez digital", "cosmetica", "Espana"],
        "reference_tool_calls": ["sector_corpus_search"],
    },
    {
        "question": "Que implica la directiva NIS2 para una fabrica cosmetica conectada?",
        "ground_truth": "La NIS2 establece requisitos de ciberseguridad para infraestructuras criticas, afectando a fabricas cosmeticas con sistemas IoT y SCADA conectados, requiriendo gestion de riesgos, notificacion de incidentes y auditorias periodicas.",
        "expected_agent": "sector_agent",
        "reference_topics": ["transformacion digital", "NIS2", "ciberseguridad", "cosmetica"],
        "reference_tool_calls": ["sector_corpus_search"],
    },
    {
        "question": "Como definir un roadmap de transformacion digital para una empresa cosmetica?",
        "ground_truth": "Un roadmap de transformacion digital debe incluir: diagnostico de madurez digital, identificacion de areas prioritarias, seleccion de tecnologias (ERP/MES/PLM), definicion de KPIs, plan de formacion y cronograma de implementacion.",
        "expected_agent": "sector_agent",
        "reference_topics": ["transformacion digital", "roadmap", "cosmetica", "ERP", "MES"],
        "reference_tool_calls": ["sector_corpus_search"],
    },
    {
        "question": "Cuales son las principales barreras para la adopcion de IoT en el sector cosmetico?",
        "ground_truth": "Las principales barreras son: coste de implementacion, falta de personal cualificado, integracion con sistemas legacy, preocupaciones de ciberseguridad (NIS2), y resistencia al cambio organizacional.",
        "expected_agent": "sector_agent",
        "reference_topics": ["transformacion digital", "IoT", "barreras", "cosmetica"],
        "reference_tool_calls": ["sector_corpus_search"],
    },
    # ── matching_agent (2) ──
    {
        "question": "Que soluciones tecnologicas y digitales estan disponibles en el catalogo DIGIPYC?",
        "ground_truth": "El catalogo DIGIPYC incluye soluciones de IA para formulacion, sistemas MES para control de produccion, plataformas IoT para monitorizacion, herramientas de vision artificial para calidad, y soluciones ERP integradas.",
        "expected_agent": "matching_agent",
        "reference_topics": ["DIGIPYC", "soluciones tecnologicas", "catalogo", "cosmetica"],
        "reference_tool_calls": ["matching_corpus_search"],
    },
    {
        "question": "Que proveedores de MES o ERP recomienda el catalogo DIGIPYC para una PYME cosmética?",
        "ground_truth": "El catalogo DIGIPYC incluye proveedores de MES/ERP adaptados a PYMEs del sector cosmetico, con soluciones para control de produccion, trazabilidad y gestion integrada.",
        "expected_agent": "matching_agent",
        "reference_topics": ["DIGIPYC", "MES", "ERP", "PYME", "proveedores"],
        "reference_tool_calls": ["matching_corpus_search"],
    },
]


# ── Phase 1: Run questions through ARIA ──────────────────────────────────────

def run_aria_for_evaluation(questions: list[dict]) -> list[dict]:
    """Run each question through ARIA and collect results + raw messages."""
    from aria.agents.orchestrator import graph

    results = []

    for i, item in enumerate(questions):
        question = item["question"]
        expected = item["expected_agent"]

        console.print(f"[cyan][{i+1}/{len(questions)}][/cyan] {question[:70]}...")

        config = {"configurable": {"thread_id": f"ragas-eval-v2-{i}"}}
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

        # Map agent to Qdrant category: agua->agua, sector->sector, matching->matching
        category = actual_agent.replace("_agent", "")
        retriever = _make_retriever(categories=[category], k=12)
        retrieved_docs = retriever.invoke(question)
        contexts = deduplicate_contexts([doc.page_content for doc in retrieved_docs])

        raw_messages = []
        for msg in result["messages"]:
            raw_messages.append({
                "type": msg.type,
                "content": msg.content,
            })

        routing_ok = actual_agent == expected
        console.print(
            f"  Agente: {actual_agent} "
            f"{'[green]OK[/green]' if routing_ok else '[red]MISS[/red]'} "
            f"| Contextos: {len(contexts)}"
        )

        results.append({
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "ground_truth": item["ground_truth"],
            "expected_agent": expected,
            "actual_agent": actual_agent,
            "routing_correct": routing_ok,
            "raw_messages": raw_messages,
        })

    CACHE_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f"[green]Fase 1 cacheada en {CACHE_FILE}[/green]")

    return results


# ── Phase 2A: RAG metrics evaluation ─────────────────────────────────────────

def _make_evaluator_llm():
    """Create evaluator LLM wrapped for RAGAS."""
    llm = ChatOpenAI(model=EVALUATOR_MODEL, max_tokens=8192)
    return LangchainLLMWrapper(llm)


def _make_evaluator_embeddings():
    """Create evaluator embeddings wrapped for RAGAS."""
    return LangchainEmbeddingsWrapper(OpenAIEmbeddings())


def run_rag_evaluation(results: list[dict]):
    """Evaluate with 6 RAG metrics using GPT-4.1-mini as judge."""
    console.rule("[bold cyan]RAGAS — RAG Metrics (GPT-4.1-mini)[/bold cyan]")

    evaluator_llm = _make_evaluator_llm()
    evaluator_embeddings = _make_evaluator_embeddings()

    samples = []
    for res in results:
        cleaned_answer = clean_response(res["answer"])
        cleaned_contexts = deduplicate_contexts(res["contexts"]) if res["contexts"] else ["No context"]

        samples.append(
            SingleTurnSample(
                user_input=res["question"],
                response=cleaned_answer,
                retrieved_contexts=cleaned_contexts,
                reference=res["ground_truth"],
            )
        )

    eval_dataset = EvaluationDataset(samples=samples)

    metrics = [
        Faithfulness(),
        LLMContextRecall(),
        FactualCorrectness(),
        ResponseRelevancy(),
        ContextEntityRecall(),
        NoiseSensitivity(),
    ]

    run_config = RunConfig(timeout=600, max_retries=5, max_workers=4)

    console.print("[cyan]Ejecutando 6 metricas RAG (timeout=600s, workers=4)...[/cyan]")
    ragas_results = evaluate(
        dataset=eval_dataset,
        metrics=metrics,
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
        run_config=run_config,
    )

    return ragas_results


# ── Phase 2B: Agent metrics evaluation ────────────────────────────────────────

async def run_agent_evaluation(results: list[dict], golden: list[dict]):
    """Evaluate with 2 Agent metrics (GoalAccuracy + TopicAdherence)."""
    console.rule("[bold cyan]RAGAS — Agent Metrics (GPT-4.1-mini)[/bold cyan]")

    evaluator_llm = _make_evaluator_llm()

    goal_scorer = AgentGoalAccuracyWithReference()
    goal_scorer.llm = evaluator_llm

    topic_scorer = TopicAdherenceScore(llm=evaluator_llm, mode="precision")

    agent_scores = []

    for i, (res, gold) in enumerate(zip(results, golden)):
        console.print(f"[cyan][{i+1}/{len(results)}][/cyan] Agent metrics: {res['question'][:50]}...")

        cleaned_answer = clean_response(res.get("answer", ""))
        ragas_trace = [
            r.HumanMessage(content=res["question"]),
            r.AIMessage(content=cleaned_answer, tool_calls=[]),
        ]

        # AgentGoalAccuracy
        goal_sample = MultiTurnSample(
            user_input=ragas_trace,
            reference=gold["ground_truth"],
        )
        try:
            goal_score = await goal_scorer.multi_turn_ascore(goal_sample)
        except Exception as e:
            console.print(f"  [yellow]AgentGoalAccuracy error: {e}[/yellow]")
            goal_score = None

        # TopicAdherence
        topic_sample = MultiTurnSample(
            user_input=ragas_trace,
            reference_topics=gold["reference_topics"],
        )
        try:
            topic_score = await topic_scorer.multi_turn_ascore(topic_sample)
        except Exception as e:
            console.print(f"  [yellow]TopicAdherence error: {e}[/yellow]")
            topic_score = None

        agent_scores.append({
            "question": res["question"],
            "actual_agent": res["actual_agent"],
            "agent_goal_accuracy": float(goal_score) if goal_score is not None else None,
            "topic_adherence": float(topic_score) if topic_score is not None else None,
        })

        console.print(f"  Goal={goal_score}  Topic={topic_score}")

    return agent_scores


# ── Results display ──────────────────────────────────────────────────────────

RAG_METRIC_COLS = [
    ("faithfulness",                       "Faith"),
    ("context_recall",                     "CtxRec"),
    ("factual_correctness(mode=f1)",       "FactCorr"),
    ("answer_relevancy",                   "RespRel"),
    ("context_entity_recall",              "EntRec"),
    ("noise_sensitivity(mode=relevant)",   "Noise"),
]

def print_results(results: list[dict], rag_results, agent_scores: list[dict]):
    """Print combined results tables."""
    correct = sum(1 for r_ in results if r_["routing_correct"])
    total = len(results)
    console.rule("[bold]Routing Accuracy[/bold]")
    console.print(f"  {correct}/{total} ({correct/total*100:.0f}%)")

    # ── RAG Metrics Table ──
    console.rule("[bold]RAG Metrics (6 metricas)[/bold]")
    df = rag_results.to_pandas()

    console.print(f"[dim]Columnas del DataFrame: {list(df.columns)}[/dim]")

    table = Table(title="RAGAS RAG — Resultados por pregunta")
    table.add_column("Pregunta", max_width=40)
    table.add_column("Agente", width=5)
    for _, label in RAG_METRIC_COLS:
        table.add_column(label, justify="right")

    for i, row in df.iterrows():
        q = row.get("user_input", results[i]["question"])[:38]
        agent = results[i]["actual_agent"].replace("_agent", "")
        vals = []
        for col, _ in RAG_METRIC_COLS:
            v = row.get(col, None)
            vals.append(f"{v:.3f}" if v is not None and pd.notna(v) else "N/A")
        table.add_row(q, agent, *vals)

    console.print(table)

    # RAG Global averages
    console.rule("[bold]RAG — Promedios Globales[/bold]")
    for col, label in RAG_METRIC_COLS:
        if col in df.columns and not df[col].dropna().empty:
            mean = df[col].dropna().mean()
            console.print(f"  {label:<30} {mean:.3f}")

    # RAG Per-agent averages
    console.rule("[bold]RAG — Promedios por Agente[/bold]")
    for agent_name in ["agua_agent", "sector_agent", "matching_agent"]:
        indices = [i for i, r_ in enumerate(results) if r_["actual_agent"] == agent_name]
        if indices:
            console.print(f"\n  [bold]{agent_name}[/bold]")
            for col, label in RAG_METRIC_COLS:
                if col in df.columns:
                    vals = [df.iloc[j][col] for j in indices if pd.notna(df.iloc[j].get(col))]
                    if vals:
                        console.print(f"    {label:<30} {sum(vals)/len(vals):.3f}")

    # ── Agent Metrics Table ──
    console.rule("[bold]Agent Metrics (2 metricas)[/bold]")
    agent_table = Table(title="RAGAS Agent — Resultados por pregunta")
    agent_table.add_column("Pregunta", max_width=40)
    agent_table.add_column("Agente", width=5)
    agent_table.add_column("GoalAcc", justify="right")
    agent_table.add_column("TopicAdh", justify="right")

    for s in agent_scores:
        q = s["question"][:38]
        agent = s["actual_agent"].replace("_agent", "")
        ga = f"{s['agent_goal_accuracy']:.3f}" if s["agent_goal_accuracy"] is not None else "N/A"
        ta = f"{s['topic_adherence']:.3f}" if s["topic_adherence"] is not None else "N/A"
        agent_table.add_row(q, agent, ga, ta)

    console.print(agent_table)

    # Agent Global averages
    console.rule("[bold]Agent — Promedios Globales[/bold]")
    for metric in ["agent_goal_accuracy", "topic_adherence"]:
        vals = [s[metric] for s in agent_scores if s[metric] is not None]
        if vals:
            console.print(f"  {metric:<30} {sum(vals)/len(vals):.3f}")

    # ── Save full report ──
    output_path = Path("./ragas_evaluation_results.json")
    export = {
        "routing_accuracy": correct / total,
        "rag_scores_global": {
            label: round(float(df[col].dropna().mean()), 4)
            for col, label in RAG_METRIC_COLS if col in df.columns and not df[col].dropna().empty
        },
        "agent_scores_global": {
            metric: round(sum(s[metric] for s in agent_scores if s[metric] is not None) /
                         max(1, sum(1 for s in agent_scores if s[metric] is not None)), 4)
            for metric in ["agent_goal_accuracy", "topic_adherence"]
        },
        "rag_scores_per_question": [
            {
                "question": results[i]["question"][:60],
                "agent": results[i]["actual_agent"],
                **{label: round(float(row[col]), 4) if pd.notna(row.get(col)) else None for col, label in RAG_METRIC_COLS},
            }
            for i, row in df.iterrows()
        ],
        "agent_scores_per_question": agent_scores,
    }
    output_path.write_text(json.dumps(export, ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f"\n[green]Resultados guardados en {output_path}[/green]")

    csv_path = Path("./ragas_evaluation_results.csv")
    rag_df = pd.DataFrame(export["rag_scores_per_question"])
    agent_df = pd.DataFrame(agent_scores)
    merged = pd.merge(rag_df, agent_df, on="question", how="outer", suffixes=("_rag", "_agent"))
    merged.to_csv(csv_path, index=False, encoding="utf-8")
    console.print(f"[green]CSV guardado en {csv_path}[/green]")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ARIA RAGAS Evaluation")
    parser.add_argument("--phase2", action="store_true", help="Skip Phase 1, use cached results")
    args = parser.parse_args()

    console.rule("[bold cyan]ARIA -- Evaluacion RAGAS completa (11 preguntas)[/bold cyan]")
    console.print(f"[dim]Evaluator LLM: {EVALUATOR_MODEL} (OpenAI)[/dim]")

    if args.phase2 and CACHE_FILE.exists():
        console.print(f"[yellow]Usando cache de Fase 1: {CACHE_FILE}[/yellow]")
        results = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    else:
        console.rule("Fase 1: Ejecutar preguntas en ARIA")
        results = run_aria_for_evaluation(GOLDEN_DATASET)

    # Phase 2A: RAG metrics
    console.rule("Fase 2A: RAG Metrics")
    rag_results = run_rag_evaluation(results)

    # Phase 2B: Agent metrics
    console.rule("Fase 2B: Agent Metrics")
    agent_scores = asyncio.run(run_agent_evaluation(results, GOLDEN_DATASET))

    # Print combined results
    print_results(results, rag_results, agent_scores)


if __name__ == "__main__":
    main()
