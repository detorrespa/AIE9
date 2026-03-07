"""
ARIA — Ingesta al servidor Qdrant (solo para visualizar en el dashboard).

No modifica ARIA. Ingiere los mismos documentos hacia http://localhost:6333
para poder ver los vectores en el dashboard de Qdrant.

Uso:
    python scripts/ingest_to_qdrant_dashboard.py [--docs-dir ./documents] [--clear]

Requiere: Qdrant Docker corriendo en localhost:6333 y túnel Ollama activo (si usas RunPod).
"""

import argparse
import os
import sys
from pathlib import Path

# Forzar conexión al servidor ANTES de cargar settings
os.environ["QDRANT_URL"] = "http://localhost:6333"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="Ingesta documentos al servidor Qdrant (dashboard únicamente)"
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("./documents"),
        help="Directorio con los documentos",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Tamaño máximo de cada chunk",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Solapamiento entre chunks",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Borrar la colección antes de ingestar (empezar desde cero)",
    )
    args = parser.parse_args()

    console.rule("[bold cyan]ARIA — Ingesta al Qdrant Dashboard[/bold cyan]")

    # Verificar que el servidor esté accesible (sin usar fallback local)
    from qdrant_client import QdrantClient

    try:
        client = QdrantClient(url="http://localhost:6333", timeout=5)
        client.get_collections()
        console.print("[green]✓ Servidor Qdrant accesible en localhost:6333[/green]")
    except Exception as e:
        console.print(
            "[red]✗ No se puede conectar a Qdrant en localhost:6333. "
            "¿Está el contenedor Docker activo?[/red]"
        )
        console.print(f"[dim]{e}[/dim]")
        sys.exit(1)

    if args.clear:
        collection = "aria_documents"
        collections = [c.name for c in client.get_collections().collections]
        if collection in collections:
            client.delete_collection(collection)
            console.print(f"[yellow]Colección '{collection}' eliminada.[/yellow]")

    # Pipeline normal (usa QDRANT_URL ya forzado)
    from aria.ingestion.chunker import chunk_all_documents
    from aria.ingestion.processor import convert_documents, get_document_paths
    from aria.vectorstore.store import ingest_chunks

    doc_paths = get_document_paths(args.docs_dir)
    if not doc_paths:
        console.print("[red]No se encontraron documentos.[/red]")
        sys.exit(1)

    console.rule("Fase 1: Conversión con Docling")
    docs = convert_documents(doc_paths)

    console.rule("Fase 2: Chunking")
    chunks = chunk_all_documents(docs, args.chunk_size, args.chunk_overlap)
    console.print(f"[cyan]Total chunks: {len(chunks)}[/cyan]")

    console.rule("Fase 3: Ingesta en Qdrant (localhost:6333)")
    count = ingest_chunks(chunks)

    console.rule("[bold green]✓ Completado[/bold green]")
    console.print(f"  Documentos: {len(docs)} | Chunks: {count}")
    console.print("[dim]Abre http://localhost:6333/dashboard#/collections para ver aria_documents[/dim]")


if __name__ == "__main__":
    main()
