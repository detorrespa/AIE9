"""Application package bootstrap and public API.

Responsibilities:
- Load environment variables from a local .env at import time for local development.
- Provide organized modules for graphs, models, state, tools, and a simple RAG utility.
- Expose key submodules via __all__ for convenient imports.
"""
from __future__ import annotations

# Load environment variables from a .env file at import time so local servers pick them up
try:
    from pathlib import Path

    from dotenv import load_dotenv

    # Use absolute path so .env is found regardless of worker CWD
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(_env_path, override=False)
except Exception:
    # dotenv not installed or .env not found; continue silently
    pass

__all__ = ["graphs", "models", "state", "tools", "rag"]

