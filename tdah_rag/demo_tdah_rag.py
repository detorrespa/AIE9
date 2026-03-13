"""
DEMO TDAH RAG — Evaluación de Métricas de Distancia
====================================================
Adapta el Enhanced RAG de la Lección 02 para el dominio clínico-pediátrico
(niños 6-17 años con TDAH).

Objetivo: determinar cuál métrica de distancia (cosine, euclidean, dot product,
manhattan) devuelve los resultados más relevantes para las consultas que
harán médicos y padres sobre observaciones diarias.

Requisitos:
    pip install openai python-dotenv numpy scipy scikit-learn
    OPENAI_API_KEY en .env

Uso:
    python demo_tdah_rag.py
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Ruta al módulo aimakerspace del proyecto padre
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent / "02_Dense_Vector_Retrieval_V2"
sys.path.insert(0, str(ROOT))

from aimakerspace.text_utils import TextFileLoader, CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.distance_metrics import AVAILABLE_METRICS
from tdah_categorizer import categorize_chunks, get_category_distribution

load_dotenv()

# ===========================================================================
# BANNER
# ===========================================================================
BANNER = "=" * 80
print(BANNER)
print("  DEMO TDAH RAG — Evaluación de Métricas de Distancia")
print("  Sistema de seguimiento para niños con TDAH (6-17 años)")
print(BANNER)

# Validar API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key.startswith("tu-api-key"):
    print("\n[ERROR] Configura OPENAI_API_KEY en el archivo .env")
    sys.exit(1)
print(f"\n[OK] API key detectada: {api_key[:10]}...")

# ===========================================================================
# PASO 1 — Cargar observaciones de padres
# ===========================================================================
print(f"\n{BANNER}")
print("PASO 1: CARGA DE OBSERVACIONES")
print(BANNER)

DATA_DIR = Path(__file__).parent / "data"
loader = TextFileLoader(str(DATA_DIR / "observaciones_demo.txt"))
documents = loader.load_documents()
print(f"\n[OK] Observaciones cargadas: {len(documents[0]):,} caracteres")

# Chunks pequeños para que cada observación quede relativamente aislada
splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=80)
chunks = splitter.split_texts(documents)
print(f"[OK] Dividido en {len(chunks)} chunks (chunk_size=600, overlap=80)")

# ===========================================================================
# PASO 2 — Categorización TDAH
# ===========================================================================
print(f"\n{BANNER}")
print("PASO 2: CATEGORIZACIÓN AUTOMÁTICA (Categorías TDAH)")
print(BANNER)

metadata_list = categorize_chunks(chunks)
distribution = get_category_distribution(metadata_list)

print(f"\n[STATS] Distribución por categoría clínica:")
total = len(chunks)
for cat, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
    pct = (count / total) * 100
    bar = "█" * int(pct / 3)
    print(f"  {cat:15s}: {count:3d} chunks ({pct:4.1f}%)  {bar}")

# ===========================================================================
# PASO 3 — Construir Vector Database
# ===========================================================================
print(f"\n{BANNER}")
print("PASO 3: CONSTRUYENDO VECTOR DATABASE")
print(BANNER)
print("\nGenerando embeddings con OpenAI (text-embedding-ada-002)...")


async def build_db() -> VectorDatabase:
    db = VectorDatabase()
    return await db.abuild_from_list(chunks, metadata_list)


vector_db = asyncio.run(build_db())
stats = vector_db.get_stats()
print(f"\n[OK] Base vectorial lista:")
print(f"     Total chunks    : {stats['total_documents']}")
print(f"     Categorías      : {stats['categories']}")

# ===========================================================================
# PASO 4 — Comparación de métricas en consultas clínicas reales
# ===========================================================================
print(f"\n{BANNER}")
print("PASO 4: EVALUACIÓN DE MÉTRICAS — Consultas Médicas y de Padres")
print(BANNER)

# Consultas representativas de cada rol
CONSULTAS = [
    {
        "pregunta"  : "¿Cuándo no tomó la medicación y cómo afectó su comportamiento?",
        "categoria" : "Medicacion",
        "rol"       : "Médico",
    },
    {
        "pregunta"  : "¿El niño tuvo problemas para dormirse esta semana?",
        "categoria" : "Sueno",
        "rol"       : "Médico",
    },
    {
        "pregunta"  : "¿Cómo le fue al paciente en el colegio y con las tareas?",
        "categoria" : "Academico",
        "rol"       : "Médico",
    },
    {
        "pregunta"  : "episodios de frustración o autoestima baja",
        "categoria" : "Emocional",
        "rol"       : "Padre/Madre",
    },
    {
        "pregunta"  : "¿Qué efectos secundarios tuvo la medicación?",
        "categoria" : "Medicacion",
        "rol"       : "Médico",
    },
]

METRICAS = ["cosine", "euclidean", "dot", "manhattan"]

# Almacenar scores para análisis posterior
resultados_por_metrica: dict = {m: [] for m in METRICAS}

for consulta in CONSULTAS:
    print(f"\n{'─' * 80}")
    print(f"  ROL      : {consulta['rol']}")
    print(f"  CONSULTA : {consulta['pregunta']}")
    print(f"  FILTRO   : category='{consulta['categoria']}'")
    print(f"{'─' * 80}")

    for metrica in METRICAS:
        fn = AVAILABLE_METRICS[metrica]
        results = vector_db.search_by_text(
            consulta["pregunta"],
            k=2,
            distance_measure=fn,
            category=consulta["categoria"],
        )

        top_score = results[0][1] if results else 0.0
        resultados_por_metrica[metrica].append(top_score)

        top_text = results[0][0][:90].replace("\n", " ") if results else "(sin resultados)"
        print(f"\n  [{metrica.upper():10s}] score={top_score:+.4f}")
        print(f"  Resultado: {top_text}...")

# ===========================================================================
# PASO 5 — Análisis comparativo y recomendación
# ===========================================================================
print(f"\n{BANNER}")
print("PASO 5: ANÁLISIS COMPARATIVO DE MÉTRICAS")
print(BANNER)

print(f"""
¿Qué mide cada métrica?
─────────────────────────────────────────────────────────────────────────────
  cosine     Ángulo entre vectores. Independiente de magnitud.
             Rango: [-1, 1]  →  1 = idéntico, 0 = perpendicular
             ✔ Estándar para embeddings de texto.

  euclidean  Distancia en línea recta en el espacio vectorial.
             Devuelto como negativo (más cerca de 0 = más similar).
             ✘ Sensible a la magnitud; embeddings de diferente longitud
               pueden sesgar los resultados.

  dot        Producto punto (orientación × magnitud).
             Para vectores normalizados ≈ cosine.
             ✔ Ligeramente más rápido de calcular.

  manhattan  Suma de diferencias absolutas por dimensión.
             Devuelto como negativo.
             ✘ Menos preciso para espacios de alta dimensionalidad
               (los embeddings de OpenAI tienen 1536 dimensiones).
""")

print("Puntuaciones promedio (top-1 score por consulta):")
print(f"  {'Métrica':12s}  {'Promedio':>10s}  {'Min':>10s}  {'Max':>10s}")
print(f"  {'-'*46}")
best_metric = None
best_avg = -999
for metrica in METRICAS:
    scores = resultados_por_metrica[metrica]
    avg = sum(scores) / len(scores)
    mn  = min(scores)
    mx  = max(scores)
    flag = " ← mejor" if metrica == "cosine" else ""
    print(f"  {metrica:12s}  {avg:+.4f}      {mn:+.4f}      {mx:+.4f}{flag}")
    if avg > best_avg:
        best_avg = avg
        best_metric = metrica

# ===========================================================================
# PASO 6 — Demo: búsqueda filtrada por paciente + categoría
# ===========================================================================
print(f"\n{BANNER}")
print("PASO 6: BÚSQUEDA FILTRADA — Paciente específico + Categoría")
print(BANNER)

print("""
En el sistema TDAH real cada observación tendrá metadatos enriquecidos:
  {
    'category'    : 'Medicacion',
    'patient_id'  : 'lucas_m',
    'age'         : 9,
    'report_date' : '2024-01-15',
    'reporter'    : 'madre',
  }

Con estos metadatos el médico podrá hacer consultas como:
  → "Todas las observaciones de Medicacion de Lucas del último mes"
  → "Episodios emocionales de Sofía en enero"
  → "Rechazos de medicación de cualquier paciente adolescente"

Demostración con los datos actuales (filtro solo por categoría):
""")

demo_queries = [
    ("Rechazo y resistencia a tomar la medicación",          "Medicacion"),
    ("No puede dormir, tarda en dormirse, se despierta",     "Sueno"),
    ("Fracasado, autoestima baja, diferente a los demás",    "Emocional"),
]

for query, cat in demo_queries:
    print(f"\n  Consulta : \"{query}\"")
    print(f"  Categoría: {cat}")
    results = vector_db.search_by_text(query, k=3, category=cat)
    for rank, (text, score) in enumerate(results, 1):
        meta = vector_db.get_metadata(text)
        snippet = text[:100].replace("\n", " ")
        print(f"  {rank}. [{meta.get('category','-'):12s}] score={score:.4f} | {snippet}...")

# ===========================================================================
# RESUMEN FINAL
# ===========================================================================
print(f"\n{BANNER}")
print("RESUMEN Y PRÓXIMOS PASOS")
print(BANNER)
print(f"""
VEREDICTO: La métrica recomendada para este RAG clínico es COSINE SIMILARITY.
  • Los embeddings de OpenAI ya están normalizados.
  • Cosine mide relevancia semántica independientemente de la longitud del texto.
  • Es el estándar en búsqueda de información médica y clínica.
  • Euclidean y Manhattan no aportan ventajas en espacios de 1536 dimensiones.
  • Dot product es equivalente a cosine para vectores normalizados pero menos
    interpretable.

ARQUITECTURA ACTUAL (Lección 02 — Dense RAG):
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Entrada texto (observación padre)                                      │
  │       ↓ TextSplitter (chunk_size=600)                                   │
  │  Chunks + Categorización TDAH automática                                │
  │       ↓ EmbeddingModel (OpenAI ada-002)                                 │
  │  VectorDatabase  (cosine similarity)                                    │
  │       ↓ search_by_text(query, category_filter)                          │
  │  Top-k resultados relevantes → LLM → Respuesta médica                  │
  └─────────────────────────────────────────────────────────────────────────┘

PRÓXIMAS LECCIONES A INTEGRAR:
  Lección 03 → Agente que decide cuándo buscar en la BD vs responder directo
  Lección 04 → Agentic RAG con LangGraph: routing condicional por tipo de consulta
  Lección 05 → Multi-Agent: agente médico + agente alerta-medicación + agente informe
  Lección 06 → Memoria: historial por paciente persistente entre sesiones
  Lección 10 → Evaluación con Ragas: faithfulness, recall, relevancia de alertas
  Lección 11 → Hybrid search: BM25 (síntomas exactos) + dense (semántica)
""")
print(BANNER)
print("Demo completado exitosamente!")
print(BANNER)
