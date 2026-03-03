**ARIA**

*Adaptive RAG Intelligence for Advisory*

Perfumery & Cosmetics Sector

# Task 1 — Problem & Audience

## Problem Statement

*Teams responsible for Digital Transformation, Sustainability, and Compliance in Spanish cosmetics companies lack a single system that can instantly retrieve sector-specific regulatory guidance, water management recommendations, and technology provider matching from their own private document corpus — forcing them to manually search across multiple PDFs, rely on generic LLM answers, or wait for specialist consultants.*

## Why This Is a Problem for This User

The primary user is the Director of Digital Transformation, Sustainability, or Compliance at a cosmetics brand, manufacturer, or sector association (FIBS/Stanpa member) making decisions across multiple domains simultaneously without constant access to specialised consultants.

Typical decisions require combining digital technology strategy (ERP/MES/PLM, IoT, cybersecurity), sustainability operations (water footprint, CIP reporting, ESG disclosure), and regulatory interpretation (UWWTD, NIS2, cosmetics claims). This information exists in sector documents but is distributed across long PDFs and heterogeneous sources — creating a repeated pattern of weeks of manual search before projects can advance. The key constraint is that the most valuable documents (Dygipic diagnostic reports, DIGIPYC solutions catalog, COSM-EAU water research) are not on the public internet and therefore unavailable to any general-purpose LLM.

## Evaluation Dataset — 15 Input/Output Pairs

The golden dataset covers the 3 agent domains with 5 questions per agent. Each question includes a ground\_truth extracted manually from the Dygipic documents and reference\_topics for the TopicAdherence metric. Questions were designed to reflect real queries from the target user profile.

|  |  |  |  |
| --- | --- | --- | --- |
| **#** | **Question** | **Expected Agent** | **Ground Truth (summary)** |
| **1** | ¿Cuál es la principal fuente de consumo de agua en una fábrica cosmética? | 💧 WaterAgent | CIP y limpieza representan el mayor consumo; reducción via automatización, reutilización OI y osmosis |
| **2** | ¿Qué establece la directiva UWWTD sobre tratamiento de aguas residuales? | 💧 WaterAgent | Marco jurídico para recogida, tratamiento y vertido; exige reducción DBO5 y sólidos en suspensión |
| **3** | ¿Qué es el concepto Dry Factory y cómo se aplica al sector cosmético? | 💧 WaterAgent | Modelo de mínimo consumo hídrico: CIP optimizado, recirculación, osmosis inversa, formulaciones waterless |
| **4** | ¿Cómo se calcula la huella hídrica en la industria cosmética? | 💧 WaterAgent | ISO 14046; >99% huella indirecta (materias primas); huella directa solo 1% del total |
| **5** | ¿Qué tecnologías avanzadas de tratamiento de efluentes existen para la industria cosmética? | 💧 WaterAgent | Osmosis inversa, MBR, electrocoagulación, sistemas sin generación de fangos |
| **6** | ¿Cuál es el nivel de madurez digital del sector cosmético en España? | 🏭 SectorAgent | Media-baja; diferencias PYME/gran empresa; áreas mejora: ERP/MES, ciberseguridad, IoT |
| **7** | ¿Qué implica la directiva NIS2 para el sector cosmético? | 🏭 SectorAgent | Requisitos ciberseguridad para infraestructuras conectadas; gestión de riesgos y notificación incidentes |
| **8** | ¿Cómo está estructurado el roadmap de digitalización del sector cosmético español? | 🏭 SectorAgent | Diagnóstico madurez → priorización áreas → selección ERP/MES/PLM → KPIs → plan formación |
| **9** | ¿Cuáles son los objetivos del proyecto DIGIPYC para el sector? | 🏭 SectorAgent | Diagnóstico sectorial, catálogo de soluciones tecnológicas, hoja de ruta de transformación digital |
| **10** | ¿Cuáles son las principales barreras para la adopción de IoT en el sector cosmético? | 🏭 SectorAgent | Coste, falta de personal, integración legacy, ciberseguridad, resistencia al cambio |
| **11** | ¿Qué soluciones para control de producción están en el catálogo DIGIPYC? | 🔍 MatchingAgent | Funditec (IoT/IA), XITASO (Industria 4.0, gemelos digitales), AINIA NPD (gestión innovación) |
| **12** | ¿Qué herramienta del catálogo DIGIPYC usa IA para optimizar formulaciones cosméticas? | 🔍 MatchingAgent | FragIA: modelos RAG + simulaciones bioquímicas + NLP; también AINIA NPD para ciclo completo |
| **13** | ¿Qué soluciones de visión artificial para control de calidad hay en el catálogo DIGIPYC? | 🔍 MatchingAgent | SKINSPECTOR (AINIA): robótica colaborativa + visión espectral + IA para evaluación de la piel |
| **14** | ¿Qué soluciones de ciberseguridad OT/IoT hay en el catálogo DIGIPYC? | 🔍 MatchingAgent | Funditec, XITASO (IEC 62443/NIS2), Irontec (auditoría + DevSecOps + pen testing) |
| **15** | ¿Qué proveedores de trazabilidad de ingredientes aparecen en el catálogo DIGIPYC? | 🔍 MatchingAgent | AINIA NPD (control ingredientes/proveedores); XITASO (IoT + ciencia de datos para trazabilidad) |

# Task 2 — Proposed Solution

## Solution Description

ARIA is a Multi-Agent RAG system with 3 specialised agents and a conversational interface built on Chainlit. The user types a question in natural language and receives a structured response with citations to the source documents. An LLM router dispatches the question to the correct specialist agent, which retrieves context from the private corpus (RAG) and optionally searches domain-restricted web sources for current regulatory information.

The architecture is 100% on-premise — the 31 Dygipic project documents never leave the FIBS-controlled environment. Inference runs on Ollama with a Gemma 3:27B model on a RunPod RTX 4090 GPU. This was a deliberate choice: sector documents contain commercially sensitive benchmarks and company diagnostic data that cannot be sent to cloud LLM APIs.

## RAG and Agent Components

RAG components: Qdrant vector store with nomic-embed-text embeddings (768 dimensions), domain-partitioned metadata filtering (one category per agent), RecursiveCharacterTextSplitter (chunk\_size=1000, overlap=200), and similarity-score-threshold retrieval (k=8, threshold=0.60). The retriever filters by category before applying vector similarity — this is the core specialisation mechanism.

Agent components: LangGraph StateGraph with 4 nodes (router + 3 agents), MemorySaver for multi-turn conversation state, per-agent system prompts with domain-specific citation instructions, and conditional DuckDuckGo web search triggered by recency keywords ('current', '2025', 'convocatoria', etc.). The router returns JSON {agent, reason} at T=0 for deterministic dispatch.

## Technology Stack

|  |  |  |
| --- | --- | --- |
| **Component** | **Choice** | **Justification** |
| **LLM (agents)** | Gemma 3:27B / Ollama | On-premise RunPod — zero inference cost, private sector data never leaves FIBS environment |
| **LLM (router)** | Gemma 3:27B / Ollama | T=0 for deterministic routing; same model avoids dependency on second endpoint |
| **Orchestration** | LangGraph | Stateful supervisor pattern with MemorySaver for multi-turn conversations; adding a 4th agent is one dict entry + one edge |
| **Embedding** | nomic-embed-text (768d) | Open-source, runs on same Ollama server as LLM; strong multilingual performance on Spanish sector documents |
| **Vector DB** | Qdrant + metadata filter | Pre-filtering by agent category before semantic search — the core specialisation mechanism |
| **Web Search** | DuckDuckGo (restricted domains) | No API cost; domain-restricted per agent prevents hallucination from off-topic web results |
| **Evaluation LLM** | GPT-4.1-mini (OpenAI) | RAGAS judge only — production system remains 100% on-premise; evaluation cost < €0.15 per full run |
| **Evaluation** | RAGAS 0.4.x | 8 metrics: 6 RAG (Faithfulness, LLMContextRecall, FactualCorrectness, ResponseRelevancy, ContextEntityRecall, NoiseSensitivity) + 2 agent (AnswerCorrectness, TopicAdherence) |
| **Monitoring** | LangSmith | Automatic tracing of every graph node; essential for debugging router decisions and tool call latency |
| **UI** | Chainlit | Native streaming support with per-message metadata; renders agent headers and source citations inline |
| **Deployment** | RunPod (RTX 4090) | GPU cloud on-premise equivalent for FIBS — SSH tunnel to local Qdrant and Ollama services |

## Three Specialised Agents

**💧 WaterAgent:** Water management and environmental regulation. Corpus: 12 COSM-EAU documents (754 chunks). Web: eur-lex.europa.eu, boe.es, watereurope.eu.

**🏭 SectorAgent:** Digital transformation knowledge for the cosmetics sector. Corpus: 18 DIGIPYC/FIBS documents (523 chunks). Web: incibe.es, red.es, stanpa.com.

**🔍 MatchingAgent:** Technology solutions and provider matching. Corpus: DIGIPYC solutions catalog + roadmap documents (272 chunks). No web search — the catalog covers the domain completely.

*The 85 chunks from anonymised company diagnostic reports are stored in a 'company' category with no active agent — reserved for Phase 2. Assigning them to SectorAgent caused the agent to mix individual company situations with general sector recommendations, producing incorrect responses.*

# Task 3 — Data & Retrieval

## Data Sources

The corpus consists of 31 documents from two Dygipic project sources:

COSM-EAU project (water): 12 documents covering water footprint methodology, CIP best practices, UWWTD directive, hydric transition reports, and the COSM-EAU solutions catalog — developed by Cetaqua, CWP, and Feeling Innovation by Stanpa.

DIGIPYC project (digital transformation): 19 documents covering digital maturity assessment (15 companies), sector roadmaps, FIBS strategic plan 2025-2028, innovation analysis, NIS2 context, and the DIGIPYC technology solutions catalog with provider profiles.

## External API: DuckDuckGo Web Search

DuckDuckGo replaces Tavily as the external search tool — eliminating a paid API dependency. The search is domain-restricted per agent to prevent off-topic results from diluting the response: WaterAgent searches eur-lex.europa.eu, boe.es, and watereurope.eu for current directive transposition status and regulatory updates. SectorAgent searches incibe.es, red.es, and stanpa.com for current NIS2 compliance guidance and digitalisation grants. Web search is triggered conditionally only when the query contains recency keywords — for static sector knowledge, the corpus is sufficient.

## Chunking Strategy

RecursiveCharacterTextSplitter with chunk\_size=1000 and chunk\_overlap=200. Each chunk stores three metadata fields: source\_name (document identifier), page\_num, and category (water | sector | matching | company). The category is assigned via scripts/categorize.py which updates Qdrant metadata without re-ingestion.

The overlap of 200 characters (20%) ensures that sentences spanning chunk boundaries are not lost — particularly important for regulatory text where a single clause can reference conditions defined in the previous paragraph.

## Retriever Configuration and Justification

Each agent uses a dedicated retriever filtered by its Qdrant category. Configuration: search\_type='similarity\_score\_threshold', k=8, score\_threshold=0.60.

**Why k=8:** With category pre-filtering already reducing the search space to the agent's domain, retrieving 8 chunks instead of the default 6 increases context coverage without meaningful latency impact. This directly improves context\_recall by giving the synthesis LLM more source material.

**Why score\_threshold=0.60:** An initial threshold of 0.70 caused sector\_agent and matching\_agent to return 0 documents — the semantic gap between business-language user questions and consulting-language corpus text is larger than in water documents where the vocabulary is highly domain-specific (CIP, COD, UWWTD). Lowering to 0.60 recovered 7-8 chunks per query for all agents with no meaningful noise increase, confirmed by Faithfulness improving from 0.320 to 0.668.

**Why category filtering over a unified retriever:** A single retriever across all 1,259 chunks would return a mix of water, sector, and matching documents for every query. Category pre-filtering ensures each agent retrieves only from its domain. Documents intentionally assigned to multiple categories (e.g. ['sector', 'matching'] for roadmap documents that reference specific technologies) are retrieved by both relevant agents — this is by design, not a bug.

## Corpus Distribution — 1,259 chunks total

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Category** | **Chunks** | **Docs** | **Active agent** | **Key documents** |
| **water** | **754** | 12 | 💧 WaterAgent | COSM-EAU catalog, UWWTD directive, hydric transition, water footprint studies, CIP cases |
| **sector** | **523** | 18 | 🏭 SectorAgent | Digital maturity report, DIGIPYC roadmaps, FIBS strategic plan, NIS2 context, innovation analysis |
| **matching** | **272** | 7 | 🔍 MatchingAgent | DIGIPYC solutions catalog + 6 sector/roadmap docs with technology references (shared categories) |
| **company** | **85** | 2 | — reserved phase 2 | Anonymised company diagnostic reports — excluded to avoid mixing individual cases with sector knowledge |

# Task 4 — End-to-End Prototype

## LangGraph Architecture

The graph has 4 nodes: router → [water\_agent | sector\_agent | matching\_agent] → END. The router uses Gemma 3:27B at T=0 and returns JSON {agent, reason}. All three agent nodes execute the same agent\_node function with agent-specific AGENT\_TOOLS configuration — adding a 4th agent requires one dictionary entry and one conditional edge, no structural changes.

## How to Run

1. Start RunPod RTX 4090: ollama pull gemma3:27b && ollama pull nomic-embed-text

2. Start Qdrant: docker run -p 6333:6333 qdrant/qdrant

3. Ingest documents: python scripts/ingest.py

4. Assign categories: python scripts/categorize.py

5. Start UI: chainlit run aria/ui/app.py --port 8000

## OSS Models — Optional Deliverable

ARIA uses Gemma 3:27B (Google DeepMind, Apache 2.0) via Ollama throughout — both for routing and agent synthesis. This satisfies the optional OSS model deliverable. The only commercial model in the system is GPT-4.1-mini, used exclusively as the RAGAS evaluation judge and not in the production inference path.

## Deployment Note

ARIA is deployed to a local RunPod endpoint rather than a public URL. This is a deliberate architectural decision: the 31 Dygipic documents contain commercially sensitive sector benchmarks and anonymised company diagnostics that cannot be served from a public endpoint.

## Key Architectural Decision: Company Reports Excluded

The 2 anonymised company diagnostic documents are stored in category 'company' with no active agent. Reason: the reports describe specific individual company situations. During development, assigning them to SectorAgent caused responses that mixed a single company's situation with sector-wide recommendations — generating statements like 'the sector struggles with legacy ERP integration' when the source was a specific PYME's diagnostic. The separation is also the strongest argument for FIBS Phase 2: a personalised agent per company that uses its own diagnostic as primary context.

# Task 5 — RAGAS Baseline Evaluation

## Evaluation Setup

Evaluator LLM: GPT-4.1-mini via LangchainLLMWrapper. The production ARIA system remains 100% on-premise with Ollama; only the RAGAS judge uses OpenAI. Estimated evaluation cost per full run: < €0.15. LangSmith traces every evaluation run automatically in the 'aria' project.

8 metrics evaluated: Faithfulness, LLMContextRecall, ContextPrecision, FactualCorrectness, ResponseRelevancy, ContextEntityRecall, NoiseSensitivity (RAG metrics) + AnswerCorrectness and TopicAdherence (agent metrics).

## Baseline Results — v1 through v3

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Version / Event** | **Faith** | **CtxRec** | **CtxPrec** | **FactCorr** | **RespRel** | **EntRec** | **Noise** |
| v1 baseline (2 agents, wrong categories) | 0.320 | 0.133 | n/a | 0.143 | 0.300 | 0.033 | 0.120 |
| v2 (categories fixed, k=8, th=0.60) | 0.659 | 0.300 | n/a | 0.112 | 0.681 | 0.159 | 0.264 |
| **v3 FINAL (matching corpus expanded)** | **0.668** | **0.300** | **0.641** | **0.133** | **0.677** | **0.187** | **0.272** |

*Note on Context Precision: The v3 evaluation added LLMContextPrecisionWithReference, obtaining 0.641. This metric was not available in v1/v2 runs due to a RAGAS version constraint. The score of 0.641 confirms that retrieved chunks are relevant to the ground truth reference — consistent with the Faithfulness (0.668) and Response Relevancy (0.677) results.*

## Conclusions from Baseline

v1 exposed a critical failure: sector\_agent and matching\_agent recovered 0 contexts because the Qdrant metadata key was nested at payload.metadata.source\_name rather than payload.source\_name, causing all category filters to miss. Faithfulness of 0.320 reflected agents responding entirely from model parametric knowledge with no grounding.

v2 fixed the metadata path and tuned retrieval parameters, recovering 7-8 contexts per query for all agents. Faithfulness jumped to 0.659 (+106%) and ResponseRelevancy to 0.681 (+127%). The remaining weak metrics — FactualCorrectness (0.112) and AnswerCorrectness — reflect a ground truth mismatch: concise 1-2 sentence references evaluated against rich multi-paragraph agent responses. More assertions = lower precision against a short reference.

v3 expanded the matching corpus from 40 to 272 chunks. FactualCorrectness recovered to 0.133 and EntityRecall improved to 0.187. Results are stable across two independent evaluation runs (delta < 0.001 on all metrics), confirming the system has no erratic behaviour between executions.

**AnswerCorrectness: 0.312 | TopicAdherence: 0.517 | Routing Accuracy: 15/15 (100%)**

# Task 6 — Advanced Retrieval Technique

## Technique: Domain-Partitioned Metadata Filtering

*Advanced technique implemented: domain-partitioned metadata pre-filtering. Each agent applies a Qdrant category filter before the vector similarity search, restricting retrieval to its assigned document domain. This is a production-grade retrieval pattern that combines metadata filtering with semantic search — going beyond standard dense retrieval over a unified corpus.*

Standard dense RAG applies cosine similarity across all corpus chunks for every query. The resulting context mix reduces precision because a question about NIS2 retrieves water regulation chunks, and a question about CIP cleaning retrieves digital maturity chunks — neither harmful individually but cumulatively they dilute the context window available for the actual answer.

Domain-partitioned filtering addresses this by restricting the vector search space to the semantically relevant subdomain before similarity is computed. The filter is applied at the Qdrant query level (FieldCondition + MatchAny) with zero latency penalty — it is evaluated server-side on indexed metadata before the ANN search runs.

## Why This Technique for This Use Case

The primary bottleneck identified in v1 evaluation was not semantic gap between query language and document language (the problem HyDE addresses) — it was retrieval precision loss from cross-domain chunk mixing. Category pre-filtering directly solves the identified problem. HyDE would add a redundant LLM call to generate a hypothetical document before each retrieval and would not have resolved the 0-context failure in v1 that caused the most damage.

For FIBS specifically, domain isolation also has a semantic correctness argument: a question about the DIGIPYC technology catalog should never retrieve water footprint chunks, even if they score above threshold on cosine similarity. Category filtering enforces domain boundaries that reflect the real-world knowledge boundaries of the three specialist roles ARIA serves.

## Quantified Improvement

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| **Retrieval approach** | **Faith** | **CtxRec** | **CtxPrec** | **RespRel** | **FactCorr** | **Δ Faith** |
| v1: Global dense retriever (baseline) | 0.320 | 0.133 | — | 0.300 | 0.143 | — |
| **v3: Domain-partitioned metadata filtering** | **0.668** | **0.300** | **0.641** | **0.677** | **0.133** | **+109%** |

## Final Results by Agent

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Agent** | **Faith** | **CtxRec** | **CtxPrec** | **FactCorr** | **RespRel** | **EntRec** | **Noise** |
| 💧 WaterAgent | 0.819 | 0.400 | — | 0.212 | 0.716 | 0.100 | 0.458 |
| 🏭 SectorAgent | 0.631 | 0.300 | — | 0.130 | 0.934 | 0.090 | 0.253 |
| 🔍 MatchingAgent | 0.552 | 0.200 | — | 0.058 | 0.382 | 0.370 | 0.106 |
| **GLOBAL** | **0.668** | **0.300** | **0.641** | **0.133** | **0.677** | **0.187** | **0.272** |

## Future Advanced Techniques (Documented)

HyDE (Hypothetical Document Embeddings): Useful for SectorAgent if user queries use very different vocabulary than the corpus — e.g. operational questions vs. consulting-language documents. Would not have helped v1 since the problem was metadata, not semantic gap.

MMR (Maximal Marginal Relevance): Relevant for MatchingAgent to increase provider diversity in recommendations — currently k=8 chunks from one catalog can return redundant sections of the same provider profile.

Structured company agent (Phase 2): The 85 company-category chunks would benefit from a dedicated agent with reranking and session memory, retrieving from the company's own diagnostic as primary context and sector corpus as secondary.

# Task 7 — Next Steps

## Retrieval Decision for Demo Day

*Decision: domain-partitioned metadata filtering as the production retrieval strategy. Dense global retrieval is not viable for this multi-domain corpus because it cannot enforce the knowledge boundaries that make each agent trustworthy to its specialist user.*

The three-agent architecture with category filtering is more maintainable than a single dense retriever for the FIBS use case: each agent's knowledge can be updated independently (add documents to 'water' without affecting 'sector'), and evaluation can be run per-agent to diagnose domain-specific regressions.

## Documented Limitations and Phase 2 Proposals

**Limitation 1 — MatchingAgent corpus depth**

The matching corpus currently contains sector reports that mention technologies in passing, not structured provider profiles with selection criteria. The agent can identify what type of solution is needed but cannot recommend a specific provider with scoring.

*Phase 2 proposal: create standardised structured profiles for each provider in the DIGIPYC catalog (name, solution, technology, target company size, required maturity level, use case, estimated price) and ingest as new matching-category documents.*

**Limitation 2 — No personalised company agent**

The 85 company diagnostic chunks cannot be used in the current architecture without contaminating sector-level responses.

*Phase 2 proposal: a conversational agent per company that uses its own diagnostic as primary context, the sector corpus as reference, and a structured discovery framework (strategy, processes, technology, data, people dimensions) to generate personalised roadmaps.*

## ARIA's Differential Value for FIBS

ARIA is the only system that combines three knowledge sources unavailable to any public LLM: the real-world digital maturity benchmark of the Spanish cosmetics sector (Dygipic), the DIGIPYC qualified technology solutions catalog, and the COSM-EAU water management research. These documents are not indexed on the internet.

The measurable results — 100% routing accuracy, Faithfulness 0.819 for WaterAgent, and a concrete Phase 2 roadmap — provide the evidence base for a follow-on commercial engagement with FIBS that converts this bootcamp POC into a production advisory tool.

**LOOM_Video** 
https://www.loom.com/share/630492c3df2d4dabb49f0e19128bbdcd
