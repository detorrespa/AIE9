# ARIA — Agentic RAG for the Cosmetics Sector

Multi-agent RAG system with a conversational interface for querying 31 documents from the water sector and European environmental regulation.

## Architecture

```
User → Chainlit UI → Orchestrator (LangGraph)
├─→ retrieve_documents (RAG: Qdrant + nomic-embed-text)
└─→ search_web (DuckDuckGo)
Ollama (RunPod RTX 4080) ← Gemma 3:27B + nomic-embed-text
Docling ← Processing of PDFs, PPTXs, images
```

## Stack

| Component | Technology |
|---|---|
| LLM | Gemma 3:27B via Ollama |
| Embeddings | nomic-embed-text via Ollama |
| Orchestration | LangGraph (multi-agent) |
| Vector Store | Qdrant |
| Doc Processing | Docling |
| Web Search | DuckDuckGo |
| UI | Chainlit |
| GPU | RunPod RTX 5080 |

## Quick Setup

### 1. Local Environment

```bash
# Clone and create virtual environment
cd c:\Dev\ARIA
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -e ".[dev]"

# Configure environment variables
copy .env.example .env
# Edit .env with your RunPod details
```

### 2. Setup RunPod

```bash
# Inside the RunPod pod (via SSH):
bash scripts/setup_runpod.sh

# From your local machine — open tunnel and verify:
python scripts/setup_runpod.py
```

### 3. Ingest Documents

```bash
# Place the 31 documents in ./documents/
python scripts/ingest.py

### 4. Run ARIA

```bash
# Web Interface (Chainlit)
chainlit run aria/ui/app.py

# Terminal Chat (testing)
python scripts/chat.py

```

## Project Structure

```
ARIA/
├── aria/
│   ├── config.py              # Centralized configuration
│   ├── runpod/
│   │   ├── tunnel.py          # SSH tunnel to RunPod
│   │   └── setup.py           # Health checks and model pull
│   ├── ingestion/
│   │   ├── processor.py       # Document conversion (Docling)
│   │   └── chunker.py         # Chunking strategy
│   ├── vectorstore/
│   │   └── store.py           # Qdrant + Ollama embeddings
│   ├── tools/
│   │   ├── retriever.py       # RAG tool
│   │   └── web_search.py      # Web search tool
│   ├── agents/
│   │   ├── orchestrator.py    # Main LangGraph graph
│   │   ├── prompts.py         # System prompts
│   │   └── state.py           # Shared state
│   └── ui/
│       └── app.py             # Chainlit interface
├── scripts/
│   ├── setup_runpod.py        # Local setup (tunnel + models)
│   ├── setup_runpod.sh        # Setup inside the pod
│   ├── ingest.py              # Document ingestion
│   └── chat.py                # Terminal test chat
├── documents/                 # The 31 sector documents
├── pyproject.toml
└── .env.example

```

## Agent Flow

1. The user writes a question in natural language.
2. The orchestrator analyzes the question and decides:
  - **RAG Only**: query answerable with the corpus → `retrieve_documents`
  - **Search Only**: needs updated information →  `search_web`
  - **Both**: complex cross-domain query → executes both in sequence
3. It generates a structured response including:
  - Main answer with citations `[Documento, p.XX]`
  - Optional artifacts: checklists, provider shortlists, risk flags

