"""Web search tools — domain-restricted per agent."""

from duckduckgo_search import DDGS
from langchain_core.tools import tool

from aria.config import settings


def _search(query: str, domains: list[str] | None = None) -> str:
    """Execute search, optionally restricting to specific domains."""
    if domains:
        domain_query = " ".join(f"site:{d}" for d in domains[:3])
        full_query = f"{query} {domain_query}"
    else:
        full_query = query

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(full_query, max_results=settings.search_max_results))
    except Exception as e:
        return f"Error en busqueda web: {e}"

    if not results:
        return "No se encontraron resultados en la web para esta consulta."

    formatted = []
    for i, r in enumerate(results, 1):
        formatted.append(
            f"[Resultado {i}]\n"
            f"Titulo: {r.get('title', 'N/A')}\n"
            f"URL: {r.get('href', 'N/A')}\n"
            f"Extracto: {r.get('body', 'N/A')}"
        )
    return "\n\n---\n\n".join(formatted)


@tool
def agua_web_search(query: str) -> str:
    """Busca normativa ambiental ACTUALIZADA: UWWTD, CSRD hidrico, ISO 14046,
    convocatorias agua, precios. Solo para info que puede haber cambiado."""
    return _search(
        query,
        domains=["eur-lex.europa.eu", "boe.es", "watereurope.eu"],
    )


@tool
def sector_web_search(query: str) -> str:
    """Busca info ACTUALIZADA sobre digitalización del sector cosmético:
    NIS2, ayudas PYME, directivas UE, convocatorias de digitalización."""
    return _search(
        query,
        domains=["incibe.es", "red.es", "cosmeticseurope.eu", "stanpa.com"],
    )
