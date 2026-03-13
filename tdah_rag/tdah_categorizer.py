"""
Categorización automática para observaciones clínicas de niños con TDAH.

Categorías adaptadas al dominio clínico-pediátrico:
  - Comportamiento : hiperactividad, impulsividad, atención
  - Medicacion     : adherencia, efectos, dosis, efectos secundarios
  - Academico      : rendimiento escolar, tareas, colegio
  - Emocional      : estado de ánimo, ansiedad, autoestima, regulación
  - Social         : pares, familia, habilidades sociales
  - Sueno          : calidad del sueño, rutinas nocturnas
  - Alimentacion   : apetito, peso, hábitos alimenticios
  - General        : observaciones que no encajan en otras categorías
"""

from typing import List, Dict


# ---------------------------------------------------------------------------
# Palabras clave por categoría (en español, con variantes comunes)
# ---------------------------------------------------------------------------
_KEYWORDS: Dict[str, List[str]] = {
    "Comportamiento": [
        "hiperactividad", "hiperactivo", "inquieto", "impulsividad", "impulsivo",
        "atención", "concentración", "distracción", "distraído", "concentrar",
        "sentado", "quieto", "interrumpir", "interrupción", "interrumpió",
        "organización", "olvidó", "perdió", "terminar", "completar",
        "rabieta", "explosión", "berrinche", "conducta", "comportamiento",
        "agitado", "agitación", "moverse", "levantarse", "silla",
    ],
    "Medicacion": [
        "medicación", "medicamento", "metilfenidato", "atomoxetina", "ritalin",
        "dosis", "tomó", "tomar", "pastilla", "píldora", "tratamiento",
        "efecto", "wearing-off", "adherencia", "resistencia", "rechazo",
        "náuseas", "dolor de cabeza", "efectos secundarios", "side effect",
        "horario", "olvidó tomar", "no quiso tomar", "zombie",
    ],
    "Academico": [
        "colegio", "escuela", "clase", "profesor", "maestra", "tarea",
        "examen", "prueba", "nota", "calificación", "trabajo", "entregar",
        "rendimiento", "académico", "leer", "escribir", "lectura", "escritura",
        "matemáticas", "ciencias", "historia", "lengua", "materia",
        "estudio", "estudiar", "aprendizaje", "libro", "mochila",
    ],
    "Emocional": [
        "emoción", "emocional", "humor", "ánimo", "frustración", "frustrado",
        "llorar", "lloro", "ansiedad", "ansioso", "miedo", "preocupación",
        "autoestima", "autoconfianza", "fracasado", "lento", "diferente",
        "feliz", "triste", "enojado", "irritable", "irritabilidad",
        "regulación", "autorregulación", "calmarse", "explosión emocional",
        "orgullo", "motivación", "desmotivación",
    ],
    "Social": [
        "amigo", "amistad", "compañero", "compañera", "grupo", "jugar",
        "pelea", "conflicto", "excluido", "incluido", "interacción",
        "hermano", "familia", "familiar", "social", "habilidades sociales",
        "turno", "empatía", "límites", "respeto",
        "recreo", "parque", "deporte", "actividad grupal",
    ],
    "Sueno": [
        "sueño", "dormir", "durmió", "despertó", "despertarse", "insomnio",
        "noche", "cama", "dormirse", "amaneció", "descanso", "descansado",
        "cansado", "cansancio", "somnolencia", "pantalla antes de dormir",
        "rutina nocturna", "pesadilla", "levantarse de noche",
    ],
    "Alimentacion": [
        "comer", "comió", "apetito", "hambre", "desayuno", "almuerzo",
        "cena", "alimentación", "alimento", "nutrición", "peso",
        "delgado", "engordó", "agua", "hidratación", "dulces",
        "chatarra", "verdura", "fruta", "comida",
    ],
}


def categorize_chunk(text: str) -> str:
    """
    Categoriza un fragmento de texto en una de las 8 categorías TDAH.

    Returns:
        Nombre de la categoría con mayor puntuación, o 'General' si no hay match.
    """
    text_lower = text.lower()

    scores = {
        category: sum(1 for kw in keywords if kw in text_lower)
        for category, keywords in _KEYWORDS.items()
    }

    best_category, best_score = max(scores.items(), key=lambda x: x[1])
    return best_category if best_score > 0 else "General"


def categorize_chunks(chunks: List[str]) -> List[Dict[str, str]]:
    """
    Categoriza una lista de chunks y devuelve una lista de metadatos.

    Returns:
        Lista de dicts con al menos {'category': <str>}.
    """
    return [{"category": categorize_chunk(chunk)} for chunk in chunks]


def get_category_distribution(metadata_list: List[Dict[str, str]]) -> Dict[str, int]:
    """
    Calcula la distribución de categorías en una lista de metadatos.
    """
    distribution: Dict[str, int] = {}
    for meta in metadata_list:
        cat = meta.get("category", "Unknown")
        distribution[cat] = distribution.get(cat, 0) + 1
    return distribution


# ---------------------------------------------------------------------------
# Demo autoejecutable
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_texts = [
        "Lucas estuvo muy inquieto e interrumpió la clase tres veces hoy.",
        "Tomó el metilfenidato a las 7:30 pero el efecto pareció pasar a las 13:00.",
        "No entregó el trabajo de historia aunque lo tenía hecho en casa.",
        "Lloró diciendo que se siente un fracasado y que nunca será normal.",
        "Se peleó con su hermano en el almuerzo y no quiso hablar después.",
        "Tardó una hora en dormirse a pesar de estar en cama a las 21:00.",
        "Solo comió la mitad del desayuno y casi nada en el almuerzo.",
        "Hoy jugó en el parque con dos amigos del vecindario sin conflictos.",
    ]

    print("Categorización TDAH Demo:\n")
    for text in test_texts:
        cat = categorize_chunk(text)
        print(f"  [{cat:15s}] {text[:75]}")

    metadata = categorize_chunks(test_texts)
    dist = get_category_distribution(metadata)
    print("\nDistribución:", dist)
