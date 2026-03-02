"""Ingesta solo el documento L'Oréal para evitar duplicados."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from aria.ingestion.chunker import chunk_all_documents
from aria.ingestion.processor import convert_documents
from aria.vectorstore.store import ingest_chunks

console = Console()

def main():
    md_path = Path(__file__).resolve().parent.parent / "documents" / "Caso_exito_Loreal_agua.md"
    if not md_path.exists():
        console.print("[red]No existe documents/Caso_exito_Loreal_agua.md[/red]")
        return
    console.print("[cyan]Ingestando solo Caso_exito_Loreal_agua.md[/cyan]")
    docs = convert_documents([md_path])
    if not docs:
        console.print("[red]Error en conversión[/red]")
        return
    chunks = chunk_all_documents(docs, chunk_size=1000, chunk_overlap=200)
    console.print(f"Chunks generados: {len(chunks)}")
    count = ingest_chunks(chunks)
    console.print(f"[green]OK — {count} chunks añadidos a Qdrant[/green]")

if __name__ == "__main__":
    main()
