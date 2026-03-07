"""Qdrant vector store with Ollama embeddings — singleton pattern."""

from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from rich.console import Console

from aria.config import settings

console = Console(force_terminal=True)

EMBEDDING_DIM = 768  # nomic-embed-text dimension

_qdrant_client: QdrantClient | None = None
_vector_store: QdrantVectorStore | None = None
_embeddings: OllamaEmbeddings | None = None


def get_embeddings() -> OllamaEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OllamaEmbeddings(
            model=settings.ollama_embed_model,
            base_url=settings.ollama_base_url,
        )
    return _embeddings


def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is not None:
        return _qdrant_client

    from pathlib import Path
    local_path = Path(__file__).resolve().parent.parent.parent / "qdrant_data"
    # aria_v2: siempre modo local (qdrant_data) para no chocar con Docker de aria_v3
    console.print(f"[dim]Qdrant local: {local_path}[/dim]")
    _qdrant_client = QdrantClient(path=str(local_path))
    return _qdrant_client


def ensure_collection(client: QdrantClient) -> None:
    collections = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in collections:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )


def get_vector_store() -> QdrantVectorStore:
    global _vector_store
    if _vector_store is not None:
        return _vector_store

    client = get_qdrant_client()
    ensure_collection(client)
    embeddings = get_embeddings()
    _vector_store = QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection,
        embedding=embeddings,
    )
    return _vector_store


def ingest_chunks(chunks: list[dict]) -> int:
    if not chunks:
        return 0

    store = get_vector_store()
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    store.add_texts(texts=texts, metadatas=metadatas)
    console.print(f"[green]OK {len(chunks)} chunks ingestados en Qdrant.[/green]")
    return len(chunks)
