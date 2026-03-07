"""
ARIA — Script de ingesta de documentos.

Uso:
    python scripts/ingest.py [--docs-dir ./documents] [--chunk-size 1000] [--chunk-overlap 200]

Procesa todos los documentos del directorio, los convierte con Docling,
los divide en chunks y los ingesta en el vector store.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console

from aria.ingestion.chunker import chunk_all_documents
from aria.ingestion.processor import convert_documents, get_document_paths
from aria.vectorstore.store import ingest_chunks

console = Console()


def main():
    parser = argparse.ArgumentParser(description="ARIA Document Ingestion")
    parser.add_argument("--docs-dir", type=Path, default=Path("./documents"),
                        help="Directorio con los documentos")
    parser.add_argument("--chunk-size", type=int, default=1000,
                        help="Tamaño máximo de cada chunk (caracteres)")
    parser.add_argument("--chunk-overlap", type=int, default=200,
                        help="Solapamiento entre chunks (caracteres)")
    args = parser.parse_args()

    console.rule("[bold cyan]ARIA — Ingesta de Documentos[/bold cyan]")

    # 1. Discover documents
    doc_paths = get_document_paths(args.docs_dir)
    if not doc_paths:
        console.print("[red]No se encontraron documentos. Coloca tus archivos en el directorio.[/red]")
        return

    # 2. Convert with Docling
    console.rule("Fase 1: Conversión con Docling")
    docs = convert_documents(doc_paths)

    # 3. Chunk
    console.rule("Fase 2: Chunking")
    chunks = chunk_all_documents(docs, args.chunk_size, args.chunk_overlap)
    console.print(f"[cyan]Total chunks generados: {len(chunks)}[/cyan]")

    # 4. Ingest into vector store
    console.rule("Fase 3: Ingesta en Vector Store")
    count = ingest_chunks(chunks)

    console.rule("[bold green]✓ Ingesta completada[/bold green]")
    console.print(f"  Documentos procesados: {len(docs)}")
    console.print(f"  Chunks ingestados: {count}")


if __name__ == "__main__":
    main()
