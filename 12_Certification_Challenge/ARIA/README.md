# ARIA — Agentic RAG para el Sector del Agua

Sistema multi-agente RAG con interfaz conversacional para consultar 31 documentos del sector del agua y regulación medioambiental europea.

## Arquitectura

```
Usuario → Chainlit UI → Orquestador (LangGraph)
                              ├─→ retrieve_documents (RAG: Qdrant + nomic-embed-text)
                              └─→ search_web (DuckDuckGo)
                              
Ollama (RunPod RTX 5080) ← Gemma 3:27B + nomic-embed-text
Docling ← Procesamiento de PDFs, PPTXs, imágenes
```

## Stack

| Componente | Tecnología |
|---|---|
| LLM | Gemma 3:27B via Ollama |
| Embeddings | nomic-embed-text via Ollama |
| Orquestación | LangGraph (multi-agente) |
| Vector Store | Qdrant |
| Procesamiento docs | Docling |
| Búsqueda web | DuckDuckGo |
| UI | Chainlit |
| GPU | RunPod RTX 5080 |

## Setup rápido

### 1. Entorno local

```bash
# Clonar y crear entorno virtual
cd c:\Dev\ARIA
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -e ".[dev]"

# Configurar variables de entorno
copy .env.example .env
# Editar .env con tus datos de RunPod
```

### 2. Setup RunPod

```bash
# Dentro del pod de RunPod (vía SSH):
bash scripts/setup_runpod.sh

# Desde tu máquina local — abrir tunnel y verificar:
python scripts/setup_runpod.py
```

### 3. Ingestar documentos

```bash
# Colocar los 31 documentos en ./documents/
python scripts/ingest.py
```

### 4. Ejecutar ARIA

```bash
# Interfaz web (Chainlit)
chainlit run aria/ui/app.py

# Chat por terminal (testing)
python scripts/chat.py
```

## Estructura del proyecto

```
ARIA/
├── aria/
│   ├── config.py              # Configuración centralizada
│   ├── runpod/
│   │   ├── tunnel.py          # SSH tunnel a RunPod
│   │   └── setup.py           # Health checks y pull de modelos
│   ├── ingestion/
│   │   ├── processor.py       # Conversión de documentos (Docling)
│   │   └── chunker.py         # Estrategia de chunking
│   ├── vectorstore/
│   │   └── store.py           # Qdrant + Ollama embeddings
│   ├── tools/
│   │   ├── retriever.py       # Herramienta RAG
│   │   └── web_search.py      # Herramienta de búsqueda web
│   ├── agents/
│   │   ├── orchestrator.py    # Grafo LangGraph principal
│   │   ├── prompts.py         # System prompts
│   │   └── state.py           # Estado compartido
│   └── ui/
│       └── app.py             # Interfaz Chainlit
├── scripts/
│   ├── setup_runpod.py        # Setup local (tunnel + modelos)
│   ├── setup_runpod.sh        # Setup dentro del pod
│   ├── ingest.py              # Ingesta de documentos
│   └── chat.py                # Chat terminal de prueba
├── documents/                 # Los 31 documentos del sector
├── pyproject.toml
└── .env.example
```

## Flujo del agente

1. El usuario escribe una pregunta en lenguaje natural
2. El orquestador analiza la pregunta y decide:
   - **Solo RAG**: pregunta respondible con el corpus → `retrieve_documents`
   - **Solo Search**: necesita info actualizada → `search_web`
   - **Ambas**: pregunta compleja cross-domain → ejecuta ambas en secuencia
3. Genera respuesta estructurada con:
   - Respuesta principal con citas `[Documento, p.XX]`
   - Artefactos opcionales: checklist, shortlist de proveedores, risk flags
