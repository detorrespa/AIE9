"""
Script para comparar diferentes metricas de distancia
Demuestra como diferentes metricas afectan el ranking de resultados
"""

import numpy as np
from aimakerspace.distance_metrics import AVAILABLE_METRICS

print("=" * 80)
print("COMPARACION DE METRICAS DE DISTANCIA")
print("=" * 80)

# Simulamos embeddings de 3 documentos y 1 query
# En realidad estos serian generados por OpenAI embeddings
# Aqui usamos vectores de ejemplo para demostrar el concepto

print("\nSimulando embeddings de documentos (vectores de 5 dimensiones):\n")

# Query: "ejercicios para dolor de espalda"
query_vector = np.array([0.8, 0.6, 0.3, 0.1, 0.2])
print(f"Query vector:  {query_vector}")

# Documento 1: Muy relacionado con ejercicios de espalda
doc1_vector = np.array([0.9, 0.7, 0.4, 0.2, 0.1])
print(f"Doc 1 (alta similitud):  {doc1_vector}")

# Documento 2: Medianamente relacionado
doc2_vector = np.array([0.5, 0.4, 0.5, 0.3, 0.3])
print(f"Doc 2 (media similitud): {doc2_vector}")

# Documento 3: Poco relacionado
doc3_vector = np.array([0.2, 0.1, 0.8, 0.7, 0.6])
print(f"Doc 3 (baja similitud):  {doc3_vector}")

documents = {
    'Doc 1 (alta similitud)': doc1_vector,
    'Doc 2 (media similitud)': doc2_vector,
    'Doc 3 (baja similitud)': doc3_vector
}

print("\n" + "=" * 80)
print("COMPARANDO METRICAS")
print("=" * 80)

# Comparar con cada metrica
for metric_name, metric_func in AVAILABLE_METRICS.items():
    print(f"\n--- {metric_name.upper()} ---")
    
    # Calcular scores para cada documento
    scores = []
    for doc_name, doc_vector in documents.items():
        score = metric_func(query_vector, doc_vector)
        scores.append((doc_name, score))
    
    # Ordenar por score (descendente)
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # Mostrar ranking
    print(f"Ranking segun {metric_name}:")
    for rank, (doc_name, score) in enumerate(scores, 1):
        print(f"  {rank}. {doc_name:25s} | Score: {score:8.4f}")

print("\n" + "=" * 80)
print("ANALISIS DE RESULTADOS")
print("=" * 80)

print("""
OBSERVACIONES:

1. COSINE SIMILARITY:
   - Mide el angulo entre vectores (orientacion)
   - No se ve afectada por la magnitud del vector
   - Mejor para comparar textos de diferentes longitudes
   - Rango: [-1, 1] donde 1 = identico

2. EUCLIDEAN DISTANCE:
   - Mide la distancia en linea recta entre puntos
   - SI se ve afectada por la magnitud
   - Valores mas cercanos a 0 = mas similares
   - Retornamos valores negativos para mantener consistencia (mayor = mejor)

3. DOT PRODUCT:
   - Combina similitud de orientacion Y magnitud
   - Para vectores normalizados, equivale a cosine similarity
   - Valores mas altos = mas similar
   - Util cuando la magnitud importa

4. MANHATTAN DISTANCE:
   - Suma de diferencias absolutas en cada dimension
   - Similar a Euclidean pero usa norma L1
   - Mas robusta a outliers que Euclidean
   - Retornamos valores negativos (mayor = mejor)

CUAL USAR?
- Para textos (embeddings): COSINE SIMILARITY (default)
- Para datos numericos: EUCLIDEAN o MANHATTAN
- Para vectores normalizados: DOT PRODUCT o COSINE
- Para experimentar: PROBAR TODAS y comparar resultados

NOTA: Con embeddings reales de OpenAI, las diferencias pueden ser mas
pronunciadas. Este es solo un ejemplo didactico.
""")

print("=" * 80)
print("Comparacion completada!")
print("=" * 80)
