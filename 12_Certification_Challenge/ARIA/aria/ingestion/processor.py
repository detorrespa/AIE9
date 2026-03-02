"""Document processing with Docling — handles PDFs, PPTXs, images, and more."""

import os
import shutil
import sys
from pathlib import Path

# Monkeypatch huggingface_hub to use file copies instead of symlinks on Windows
# (Windows requires Developer Mode or admin privileges for symlinks)
if sys.platform == "win32":
    import huggingface_hub.file_download as _hf_dl

    _original_create_symlink = _hf_dl._create_symlink

    def _patched_create_symlink(src: str, dst: str, new_blob: bool = False) -> None:
        try:
            _original_create_symlink(src, dst, new_blob=new_blob)
        except OSError:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if new_blob:
                shutil.move(src, dst)
            else:
                shutil.copy2(src, dst)

    _hf_dl._create_symlink = _patched_create_symlink

from docling.document_converter import DocumentConverter
from rich.console import Console
from rich.progress import track

from aria.config import settings

console = Console(force_terminal=True)


def get_document_paths(docs_dir: Path | None = None) -> list[Path]:
    """Discover all supported documents in the documents directory."""
    docs_dir = docs_dir or settings.documents_dir
    supported = {".pdf", ".pptx", ".ppt", ".docx", ".xlsx", ".html", ".png", ".jpg", ".jpeg", ".tiff"}
    paths = sorted(p for p in docs_dir.rglob("*") if p.suffix.lower() in supported)
    console.print(f"[cyan]Encontrados {len(paths)} documentos en {docs_dir}[/cyan]")
    return paths


def convert_documents(doc_paths: list[Path] | None = None) -> list[dict]:
    """
    Convert documents to structured representation using Docling.

    Returns a list of dicts with keys:
        - source: original file path
        - pages: list of page dicts with 'page_num' and 'content'
        - metadata: document-level metadata
    """
    if doc_paths is None:
        doc_paths = get_document_paths()

    if not doc_paths:
        console.print("[yellow]No se encontraron documentos para procesar.[/yellow]")
        return []

    converter = DocumentConverter()
    results = []

    for path in track(doc_paths, description="Procesando documentos..."):
        try:
            doc_result = converter.convert(str(path))
            doc = doc_result.document

            pages = []
            for item in doc.iterate_items():
                page_num = _extract_page_number(item)
                text = item.export_to_markdown() if hasattr(item, "export_to_markdown") else str(item)
                if text.strip():
                    pages.append({
                        "page_num": page_num,
                        "content": text.strip(),
                        "type": type(item).__name__,
                    })

            full_md = doc_result.document.export_to_markdown()

            results.append({
                "source": str(path),
                "source_name": path.stem,
                "full_markdown": full_md,
                "items": pages,
                "metadata": {
                    "filename": path.name,
                    "extension": path.suffix.lower(),
                    "num_items": len(pages),
                },
            })
            console.print(f"  [green]OK[/green] {path.name} -> {len(pages)} elementos")

        except Exception as e:
            console.print(f"  [red]ERROR[/red] {path.name}: {e}")

    console.print(f"[green]Procesados {len(results)}/{len(doc_paths)} documentos.[/green]")
    return results


def _extract_page_number(item) -> int:
    """Try to extract page number from a Docling item."""
    if hasattr(item, "prov") and item.prov:
        for prov in item.prov:
            if hasattr(prov, "page_no"):
                return prov.page_no
    return 0
