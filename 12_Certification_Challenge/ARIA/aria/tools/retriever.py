"""RAG retrieval tools — filtradas por categoría por agente."""

from langchain_core.tools import tool
from qdrant_client.models import FieldCondition, Filter, MatchAny

from aria.vectorstore.store import get_vector_store


def _make_retriever(categories: list[str] | None = None, k: int = 12):
    """Build a retriever with optional category filter."""
    store = get_vector_store()
    kwargs = {"k": k, "score_threshold": 0.55}

    if categories:
        kwargs["filter"] = Filter(
            must=[FieldCondition(key="category", match=MatchAny(any=categories))]
        )

    return store.as_retriever(
        search_type="similarity_score_threshold", search_kwargs=kwargs
    )


def _format_docs(docs) -> str:
    if not docs:
        return "No se encontraron documentos relevantes en el corpus."
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source_name", "Desconocido")
        page = doc.metadata.get("page_num", "?")
        formatted.append(
            f"[Fragmento {i}] Fuente: {source} | Página: {page}\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(formatted)


@tool
def agua_corpus_search(query: str) -> str:
    """Busca en documentos sobre agua: CIP, huella hídrica, Dry Factory,
    UWWTD, efluentes, osmosis inversa, normativa ambiental, proveedores de agua."""
    retriever = _make_retriever(categories=["agua"])
    docs = retriever.invoke(query)
    return _format_docs(docs)


@tool
def sector_corpus_search(query: str) -> str:
    """Busca en documentos sectoriales: madurez digital del sector cosmético,
    roadmaps de digitalización, planes estratégicos FIBS/Stanpa/DIGIPYC,
    NIS2, benchmarks, tendencias y estrategia sectorial."""
    retriever = _make_retriever(categories=["sector"])
    docs = retriever.invoke(query)
    return _format_docs(docs)


@tool
def matching_corpus_search(query: str) -> str:
    """Busca en el catálogo DIGIPYC de soluciones tecnológicas y proveedores:
    herramientas de IA, MES, ERP, PLM, IoT, visión artificial, ciberseguridad,
    trazabilidad. Usa esta tool para recomendar proveedores o soluciones concretas."""
    retriever = _make_retriever(categories=["matching"])
    docs = retriever.invoke(query)
    return _format_docs(docs)
