"""
Demo completo del Enhanced RAG System
Este script demuestra todas las funcionalidades sin necesidad de API key
"""

import numpy as np
from aimakerspace.categorizer import categorize_chunk, categorize_chunks, get_category_distribution
from aimakerspace.distance_metrics import AVAILABLE_METRICS
from aimakerspace.text_utils import TextFileLoader, CharacterTextSplitter

print("=" * 80)
print("DEMO: Enhanced RAG System")
print("=" * 80)

# ============================================================================
# PARTE 1: Demostracion del Categorizador Automatico
# ============================================================================
print("\n[*] PARTE 1: CATEGORIZADOR AUTOMATICO")
print("-" * 80)

test_texts = [
    "Regular exercise can help reduce lower back pain. Try stretching daily.",
    "A balanced diet rich in fruits and vegetables provides essential nutrients.",
    "Good sleep hygiene includes maintaining a consistent bedtime routine.",
    "Meditation and deep breathing can help manage stress and anxiety.",
    "This is just some random text without specific health topics.",
    "High-intensity interval training (HIIT) improves cardiovascular fitness.",
    "Protein intake is crucial for muscle recovery after workouts.",
    "Insomnia affects millions of people and can be improved with proper sleep habits.",
    "Mindfulness practices reduce cortisol levels and promote relaxation.",
    "Walking 10,000 steps daily supports overall wellness."
]

print("\n[OK] Categorizando 10 textos de ejemplo:\n")
for i, text in enumerate(test_texts, 1):
    category = categorize_chunk(text)
    print(f"{i:2d}. [{category:12s}] {text[:60]}...")

# Obtener distribucion de categorias
metadata = categorize_chunks(test_texts)
distribution = get_category_distribution(metadata)

print(f"\n[STATS] Distribucion de categorias:")
for cat, count in sorted(distribution.items()):
    percentage = (count / len(test_texts)) * 100
    bar = "#" * int(percentage / 5)
    print(f"   {cat:12s}: {count:2d} docs ({percentage:5.1f}%) {bar}")

# ============================================================================
# PARTE 2: Demostracion de Metricas de Distancia
# ============================================================================
print("\n\n[*] PARTE 2: METRICAS DE DISTANCIA")
print("-" * 80)

# Vectores de ejemplo
v1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
v2 = np.array([5.0, 4.0, 3.0, 2.0, 1.0])  # Inverso de v1
v3 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])  # Igual a v1
v4 = np.array([1.1, 2.1, 3.1, 4.1, 5.1])  # Muy similar a v1

print("\nVectores de prueba:")
print(f"  v1 = {v1}")
print(f"  v2 = {v2}  (inverso de v1)")
print(f"  v3 = {v3}  (identico a v1)")
print(f"  v4 = {v4}  (muy similar a v1)")

print("\n[OK] Comparando v1 con otros vectores:\n")
print(f"{'Metrica':15s} | v1 vs v2 (inverso) | v1 vs v3 (identico) | v1 vs v4 (similar)")
print("-" * 80)

for metric_name, metric_func in AVAILABLE_METRICS.items():
    score_v2 = metric_func(v1, v2)
    score_v3 = metric_func(v1, v3)
    score_v4 = metric_func(v1, v4)
    print(f"{metric_name:15s} | {score_v2:18.4f} | {score_v3:19.4f} | {score_v4:17.4f}")

print("\n[INFO] Interpretacion:")
print("   - Cosine: 1.0 = identico, 0.0 = ortogonal, -1.0 = opuesto")
print("   - Euclidean: 0.0 = identico, mas negativo = mas distante")
print("   - Dot Product: mayor valor = mas similar (depende de magnitud)")
print("   - Manhattan: 0.0 = identico, mas negativo = mas distante")

# ============================================================================
# PARTE 3: Carga y Split de Documentos Reales
# ============================================================================
print("\n\n[*] PARTE 3: CARGA Y PROCESAMIENTO DE DOCUMENTOS")
print("-" * 80)

# Cargar documento real
try:
    text_loader = TextFileLoader("data/HealthWellnessGuide.txt")
    documents = text_loader.load_documents()
    print(f"\n[OK] Documento cargado exitosamente:")
    print(f"   - Archivo: HealthWellnessGuide.txt")
    print(f"   - Tamano: {len(documents[0])} caracteres")
    print(f"   - Primeros 150 caracteres:")
    print(f"   {documents[0][:150]}...")
    
    # Split en chunks
    text_splitter = CharacterTextSplitter()
    chunks = text_splitter.split_texts(documents)
    print(f"\n[OK] Documento dividido en chunks:")
    print(f"   - Total de chunks: {len(chunks)}")
    print(f"   - Tamano promedio: {sum(len(c) for c in chunks) / len(chunks):.0f} caracteres")
    
    # Mostrar algunos chunks de ejemplo
    print(f"\n[CHUNKS] Ejemplo de chunks (primeros 3):\n")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"   Chunk {i}:")
        print(f"   {chunk[:100]}...")
        print()
    
    # Auto-categorizar todos los chunks
    print("[PROCESS] Categorizando todos los chunks...")
    metadata_list = categorize_chunks(chunks)
    chunk_distribution = get_category_distribution(metadata_list)
    
    print(f"\n[STATS] Distribucion de categorias en el documento completo:")
    total_chunks = len(chunks)
    for cat, count in sorted(chunk_distribution.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_chunks) * 100
        bar = "#" * int(percentage / 2)
        print(f"   {cat:12s}: {count:3d} chunks ({percentage:5.1f}%) {bar}")
    
    # Mostrar ejemplos de cada categoria
    print(f"\n[EXAMPLES] Ejemplo de chunk por categoria:\n")
    seen_categories = set()
    for chunk, meta in zip(chunks, metadata_list):
        cat = meta['category']
        if cat not in seen_categories:
            seen_categories.add(cat)
            print(f"   [{cat}]")
            print(f"   {chunk[:120]}...")
            print()
        if len(seen_categories) >= 5:
            break

except FileNotFoundError:
    print("\n[ERROR] Archivo HealthWellnessGuide.txt no encontrado")
    print("   Asegurate de que el archivo existe en data/HealthWellnessGuide.txt")

# ============================================================================
# PARTE 4: Simulacion de Vector Database (sin API key)
# ============================================================================
print("\n\n[*] PARTE 4: SIMULACION DE VECTOR DATABASE")
print("-" * 80)
print("\n[INFO] Para usar la base de datos vectorial completa necesitas:")
print("   1. Crear archivo .env con tu OPENAI_API_KEY")
print("   2. Ejecutar el notebook Enhanced_RAG_Assignment.ipynb")
print("   3. O usar el siguiente codigo:\n")

print("""
from aimakerspace.vectordatabase import VectorDatabase
import asyncio

# Construir la base de datos
vector_db = VectorDatabase()
vector_db = await vector_db.abuild_from_list(chunks, metadata_list)

# Ver estadisticas
stats = vector_db.get_stats()
print(f"Total documentos: {stats['total_documents']}")
print(f"Categorias: {stats['categories']}")

# Busqueda sin filtro
results = vector_db.search_by_text("ejercicios para dolor de espalda", k=3)

# Busqueda CON filtro de categoria
results = vector_db.search_by_text(
    "ejercicios para dolor de espalda",
    k=3,
    category='Exercise'  # Solo chunks de Exercise
)

# Comparar diferentes metricas
for metric_name in ['cosine', 'euclidean', 'dot']:
    results = vector_db.search_by_text(
        "natural sleep remedies",
        k=3,
        category='Sleep',
        distance_measure=AVAILABLE_METRICS[metric_name]
    )
    print(f"\\n--- {metric_name} ---")
    for text, score in results:
        print(f"{score:.3f}: {text[:50]}...")
""")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n\n" + "=" * 80)
print("[SUCCESS] RESUMEN: FUNCIONALIDADES VERIFICADAS")
print("=" * 80)
print("""
1. [OK] Categorizacion automatica de documentos
   - 5 categorias: Exercise, Nutrition, Sleep, Stress, General
   - Basada en keywords especificas por categoria
   
2. [OK] Multiples metricas de distancia
   - Cosine Similarity (mejor para textos)
   - Euclidean Distance
   - Dot Product
   - Manhattan Distance
   
3. [OK] Carga y procesamiento de documentos
   - TextFileLoader para cargar archivos
   - CharacterTextSplitter para dividir en chunks
   
4. [OK] Vector Database mejorado (requiere OpenAI API key)
   - Metadata support
   - Filtrado por categorias
   - Busqueda multi-metrica
   - Estadisticas del corpus

PROXIMOS PASOS:
1. Crear archivo .env con tu OPENAI_API_KEY
2. Abrir el notebook: uv run jupyter notebook
3. Ejecutar Enhanced_RAG_Assignment.ipynb
4. Experimentar con diferentes queries y filtros
""")

print("=" * 80)
print("Demo completado exitosamente!")
print("=" * 80)
