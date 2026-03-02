"""Chunking strategies for processed documents."""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_document(doc: dict, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    """
    Split a processed document into chunks suitable for embedding.

    Each chunk retains metadata about its source document and page.
    """
    # Priorizar splits por secciones markdown para mantener "## Casos de éxito" con su contenido
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n## ", "\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    full_text = doc.get("full_markdown", "")

    if not full_text.strip():
        return chunks

    splits = splitter.split_text(full_text)

    for i, text in enumerate(splits):
        page_num = _estimate_page(text, doc.get("items", []))
        chunks.append({
            "text": text,
            "metadata": {
                "source": doc["source"],
                "source_name": doc["source_name"],
                "chunk_index": i,
                "page_num": page_num,
                **doc.get("metadata", {}),
            },
        })

    return chunks


def chunk_all_documents(
    docs: list[dict], chunk_size: int = 1000, chunk_overlap: int = 200
) -> list[dict]:
    """Chunk all processed documents."""
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc, chunk_size, chunk_overlap))
    return all_chunks


def _estimate_page(chunk_text: str, items: list[dict]) -> int:
    """Estimate which page a chunk belongs to by matching content to items."""
    best_page = 0
    best_overlap = 0
    for item in items:
        content = item.get("content", "")
        overlap = len(set(chunk_text.split()) & set(content.split()))
        if overlap > best_overlap:
            best_overlap = overlap
            best_page = item.get("page_num", 0)
    return best_page
