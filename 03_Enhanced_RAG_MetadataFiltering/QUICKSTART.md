# 🚀 Quick Start Guide - Enhanced RAG

## ✅ ¿Qué se ha creado?

Has construido una **versión mejorada** del sistema RAG con 3 características principales:

### 1. **Metadata Support** 
- ✅ Categorización automática de documentos (Exercise, Nutrition, Sleep, Stress, General)
- ✅ Filtrado inteligente por categorías
- ✅ Estadísticas del contenido

### 2. **Múltiples Métricas de Distancia**
- ✅ Cosine Similarity (ángulo entre vectores)
- ✅ Euclidean Distance (distancia euclideana)
- ✅ Dot Product (producto punto)
- ✅ Manhattan Distance (distancia manhattan)

### 3. **Mejor Organización**
- ✅ Carpetas organizadas (aimakerspace/, notebooks/, data/)
- ✅ Módulos separados por funcionalidad
- ✅ Documentación completa

---

## 🎯 Ejemplo de Uso Rápido

```python
# 1. Importar componentes mejorados
from aimakerspace import VectorDatabase, AVAILABLE_METRICS
from aimakerspace.text_utils import TextFileLoader, CharacterTextSplitter  
from aimakerspace.categorizer import categorize_chunks
import asyncio

# 2. Cargar documentos
loader = TextFileLoader("data/HealthWellnessGuide.txt")
documents = loader.load_documents()

splitter = CharacterTextSplitter()
chunks = splitter.split_texts(documents)

# 3. Auto-categorizar cada chunk
metadata_list = categorize_chunks(chunks)
print(f"✅ {len(chunks)} chunks categorizados")

# 4. Construir base de datos vectorial con metadata
vector_db = VectorDatabase()
vector_db = await vector_db.abuild_from_list(chunks, metadata_list)

# 5. Ver estadísticas
stats = vector_db.get_stats()
print(f"\n📊 Estadísticas:")
print(f"   Total: {stats['total_documents']} documentos")
print(f"   Categorías: {stats['categories']}")
for cat, count in stats['category_counts'].items():
    print(f"   - {cat}: {count} docs")

# 6. Búsqueda SIN filtro
results = vector_db.search_by_text(
    "What exercises help with back pain?",
    k=3
)
print("\n🔍 Búsqueda SIN filtro:")
for text, score in results:
    meta = vector_db.get_metadata(text)
    print(f"   [{meta['category']}] {score:.3f}: {text[:60]}...")

# 7. Búsqueda CON filtro de categoría
results = vector_db.search_by_text(
    "What exercises help with back pain?",
    k=3,
    category='Exercise'  # ← Filtra solo Exercise
)
print("\n🎯 Búsqueda CON filtro (solo Exercise):")
for text, score in results:
    meta = vector_db.get_metadata(text)
    print(f"   [{meta['category']}] {score:.3f}: {text[:60]}...")

# 8. Comparar diferentes métricas
query = "natural sleep remedies"
print(f"\n📏 Comparando métricas para: '{query}'")

for metric_name in ['cosine', 'euclidean', 'dot']:
    results = vector_db.search_by_text(
        query,
        k=2,
        category='Sleep',
        distance_measure=AVAILABLE_METRICS[metric_name]
    )
    print(f"\n   --- {metric_name.upper()} ---")
    for text, score in results:
        print(f"   {score:.3f}: {text[:50]}...")
```

---

## 🎬 Demo Paso a Paso

### Paso 1: Abrir Jupyter

```bash
cd C:\Dev\AIE9_Enhanced_RAG
uv run jupyter notebook
```

### Paso 2: Abrir el Notebook

`notebooks/Enhanced_RAG_Assignment.ipynb`

### Paso 3: Ejecutar las Celdas

El notebook te guiará por:
1. ✅ Importación de módulos mejorados
2. ✅ Carga y split de documentos
3. ✅ Auto-categorización
4. ✅ Construcción de vector DB con metadata
5. ✅ Búsquedas con y sin filtros
6. ✅ Comparación de métricas
7. ✅ RAG pipeline completo

---

## 📊 Demostración de Mejoras

### Antes (02_Dense_Vector_Retrieval):
```python
# Sin filtros, sin metadata
results = vector_db.search_by_text("ejercicios", k=3)
# → Devuelve cualquier cosa relacionada con "ejercicios"
```

### Después (03_Enhanced_RAG):
```python
# CON filtros y metadata
results = vector_db.search_by_text(
    "ejercicios", 
    k=3, 
    category='Exercise',  # Solo ejercicios
    distance_measure=AVAILABLE_METRICS['cosine']
)
# → Devuelve SOLO chunks de Exercise, más relevantes
```

---

## 🎥 Para tu Video Loom

Muestra estos 3 puntos clave:

### 1. **Categorización Automática**
```python
stats = vector_db.get_stats()
print(stats['category_counts'])
# {'Exercise': 45, 'Nutrition': 32, 'Sleep': 28, ...}
```

### 2. **Filtrado por Categoría**
```python
# Compara resultados CON y SIN filtro
query = "What helps with wellness?"

# Sin filtro (resultados mezclados)
results_unfiltered = vector_db.search_by_text(query, k=3)

# Con filtro (solo Exercise)
results_filtered = vector_db.search_by_text(query, k=3, category='Exercise')
```

### 3. **Comparación de Métricas**
```python
# Muestra cómo diferentes métricas dan resultados diferentes
for metric in ['cosine', 'euclidean', 'dot']:
    results = vector_db.search_by_text(query, k=2, 
                                       distance_measure=AVAILABLE_METRICS[metric])
    print(f"\n{metric}:")
    for text, score in results:
        print(f"  {score:.3f}: {text[:50]}")
```

---

## 📚 Estructura de Archivos

```
C:\Dev\AIE9_Enhanced_RAG\
├── aimakerspace/
│   ├── __init__.py              ← Imports principales
│   ├── categorizer.py           ← 🆕 Auto-categorización
│   ├── distance_metrics.py      ← 🆕 4 métricas
│   ├── vectordatabase.py        ← 🆕 Con metadata support
│   ├── text_utils.py            ← Carga y split
│   └── openai_utils/
│       ├── chatmodel.py
│       ├── embedding.py
│       └── prompts.py
├── data/
│   ├── HealthWellnessGuide.txt
│   └── PMarcaBlogs.txt
├── notebooks/
│   └── Enhanced_RAG_Assignment.ipynb  ← 🆕 Notebook mejorado
├── README.md                    ← Documentación completa
├── SETUP.md                     ← Instrucciones OneDrive
└── QUICKSTART.md                ← Esta guía
```

---

## 🎯 Próximos Pasos

1. ✅ **Ejecuta el notebook** completo
2. ✅ **Experimenta** con diferentes queries y filtros
3. ✅ **Compara métricas** - ¿cuál funciona mejor para salud?
4. ✅ **Graba tu Loom** mostrando las 3 mejoras
5. ✅ **Completa las preguntas** del assignment
6. ✅ **Sube a GitHub** (desde C:\Dev\AIE9_Enhanced_RAG)

---

## 💡 Tips para el Loom

1. **Intro (30 seg)**: "He mejorado el RAG con metadata, múltiples métricas y mejor organización"
2. **Demo Categorización (1 min)**: Muestra `stats['category_counts']`
3. **Demo Filtrado (1.5 min)**: Compara misma query con/sin filtro
4. **Demo Métricas (1.5 min)**: Compara cosine vs euclidean vs dot
5. **Conclusión (30 seg)**: "El filtrado mejora la relevancia, cosine funciona mejor para textos"

---

**¡Todo listo para usar! 🎉**

Si tienes dudas, revisa `README.md` o `SETUP.md`
