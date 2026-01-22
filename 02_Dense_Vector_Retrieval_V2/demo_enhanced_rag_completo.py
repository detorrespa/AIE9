"""
DEMO COMPLETO - Enhanced RAG con todas las mejoras
Este script puedes ejecutarlo directamente en Cursor o como script Python
"""

import asyncio
from aimakerspace.text_utils import TextFileLoader, CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.categorizer import categorize_chunks, get_category_distribution
from aimakerspace.distance_metrics import AVAILABLE_METRICS
import os
from dotenv import load_dotenv

# Cargar API key
load_dotenv()

print("=" * 80)
print("DEMO COMPLETO - ENHANCED RAG SYSTEM")
print("=" * 80)

# Verificar API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "tu-api-key-aqui":
    print("\n[ERROR] Necesitas configurar tu API key en .env")
    print("   Ejecuta: notepad .env")
    exit(1)

print(f"\n[OK] API key configurada")
print(f"   Primeros caracteres: {api_key[:10]}...")

# ==========================================================================
# PASO 1: Cargar y procesar documento
# ==========================================================================
print("\n" + "=" * 80)
print("PASO 1: CARGA Y PROCESAMIENTO DE DOCUMENTO")
print("=" * 80)

text_loader = TextFileLoader("data/HealthWellnessGuide.txt")
documents = text_loader.load_documents()
print(f"\n[OK] Documento cargado: {len(documents[0])} caracteres")

text_splitter = CharacterTextSplitter()
chunks = text_splitter.split_texts(documents)
print(f"[OK] Dividido en {len(chunks)} chunks")

# ==========================================================================
# PASO 2: Categorización automática (NUEVA FUNCIONALIDAD)
# ==========================================================================
print("\n" + "=" * 80)
print("PASO 2: CATEGORIZACION AUTOMATICA")
print("=" * 80)

metadata_list = categorize_chunks(chunks)
distribution = get_category_distribution(metadata_list)

print(f"\n[STATS] Distribucion de categorias:")
total = len(chunks)
for cat, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total) * 100
    bar = "#" * int(percentage / 2)
    print(f"   {cat:12s}: {count:3d} chunks ({percentage:5.1f}%) {bar}")

# ==========================================================================
# PASO 3: Construir Vector Database
# ==========================================================================
print("\n" + "=" * 80)
print("PASO 3: CONSTRUYENDO VECTOR DATABASE")
print("=" * 80)
print("\nEsto tomará 1-2 minutos (generando embeddings con OpenAI)...")

async def build_db():
    vector_db = VectorDatabase()
    vector_db = await vector_db.abuild_from_list(chunks, metadata_list)
    return vector_db

vector_db = asyncio.run(build_db())
print("\n[OK] Vector database creada!")

# Ver estadisticas
stats = vector_db.get_stats()
print(f"\n[STATS] Estadisticas:")
print(f"   Total documentos: {stats['total_documents']}")
print(f"   Categorías: {stats['categories']}")

# ==========================================================================
# PASO 4: DEMOSTRACIÓN - Búsqueda SIN filtro vs CON filtro
# ==========================================================================
print("\n" + "=" * 80)
print("PASO 4: BUSQUEDA SIN FILTRO vs CON FILTRO")
print("=" * 80)

query = "What exercises help with back pain?"
print(f"\nQuery: '{query}'")

# SIN filtro
print("\n[SEARCH] BUSQUEDA SIN FILTRO:")
print("-" * 80)
results_sin = vector_db.search_by_text(query, k=3)
for i, (text, score) in enumerate(results_sin, 1):
    meta = vector_db.get_metadata(text)
    print(f"{i}. [{meta['category']:12s}] {score:.4f}")
    print(f"   {text[:100]}...\n")

# CON filtro (solo Exercise)
print("\n[FILTERED] BUSQUEDA CON FILTRO (Solo Exercise):")
print("-" * 80)
results_con = vector_db.search_by_text(query, k=3, category='Exercise')
for i, (text, score) in enumerate(results_con, 1):
    meta = vector_db.get_metadata(text)
    print(f"{i}. [{meta['category']:12s}] {score:.4f}")
    print(f"   {text[:100]}...\n")

# Analisis
print("[ANALYSIS] ANALISIS:")
cats_sin = [vector_db.get_metadata(t)['category'] for t, _ in results_sin]
cats_con = [vector_db.get_metadata(t)['category'] for t, _ in results_con]
print(f"Sin filtro - Categorias: {cats_sin}")
print(f"Con filtro - Categorias: {cats_con}")
print("[INFO] El filtrado garantiza resultados solo de la categoria deseada")

# ==========================================================================
# PASO 5: DEMOSTRACIÓN - Comparación de métricas
# ==========================================================================
print("\n" + "=" * 80)
print("PASO 5: COMPARACION DE METRICAS DE DISTANCIA")
print("=" * 80)

query2 = "natural sleep remedies"
print(f"\nQuery: '{query2}'")
print(f"Filtro: category='Sleep'\n")

for metric_name in ['cosine', 'euclidean', 'dot']:
    print(f"\n--- {metric_name.upper()} ---")
    results = vector_db.search_by_text(
        query2,
        k=2,
        category='Sleep',
        distance_measure=AVAILABLE_METRICS[metric_name]
    )
    
    for i, (text, score) in enumerate(results, 1):
        print(f"{i}. Score: {score:8.4f}")
        print(f"   {text[:80]}...")

# Explicacion
print("\n" + "=" * 80)
print("[INFO] INTERPRETACION DE METRICAS:")
print("=" * 80)
print("""
1. COSINE SIMILARITY (Recomendado para textos)
   - Rango: [-1, 1] donde 1 = identico
   - Mide el angulo entre vectores
   - No afectado por magnitud

2. EUCLIDEAN DISTANCE
   - Valores negativos (mas cerca de 0 = mas similar)
   - Distancia en linea recta
   - Afectado por magnitud

3. DOT PRODUCT
   - Valores mas altos = mas similar
   - Combina orientacion y magnitud
   - Para vectores normalizados ~ cosine

[OK] Para busqueda de textos (embeddings), COSINE es la mejor opcion.
""")

# ==========================================================================
# RESUMEN FINAL
# ==========================================================================
print("\n" + "=" * 80)
print("[SUCCESS] RESUMEN: MEJORAS IMPLEMENTADAS")
print("=" * 80)
print("""
1. [OK] Categorizacion automatica en 5 categorias de salud
2. [OK] 4 metricas de distancia para comparar similitud
3. [OK] Filtrado inteligente por categorias
4. [OK] Estadisticas completas del corpus
5. [OK] Mejor organizacion del codigo (modulos separados)

COMPARATIVA:
- Sin filtro: Resultados mezclados de multiples categorias
- Con filtro: Solo resultados de la categoria deseada (mejor relevancia)
- Cosine similarity: Mejor metrica para embeddings de texto

LISTO PARA TU LOOM!
""")

print("=" * 80)
print("Demo completada exitosamente!")
print("=" * 80)
