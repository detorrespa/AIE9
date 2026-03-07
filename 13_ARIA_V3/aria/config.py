from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # RunPod
    runpod_ssh_host: str = ""
    runpod_ssh_port: int = 22
    runpod_ssh_user: str = "root"
    runpod_ssh_key_path: str = "~/.ssh/id_ed25519"

    # Ollama
    ollama_base_url: str = "http://localhost:11435"
    ollama_llm_model: str = "gemma3:27b"
    ollama_router_model: str = "gemma3:27b"
    ollama_embed_model: str = "nomic-embed-text"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "aria_documents"

    # Search
    search_max_results: int = 5

    # Documents
    documents_dir: Path = Path("./documents")

    @property
    def local_ollama_port(self) -> int:
        from urllib.parse import urlparse

        parsed = urlparse(self.ollama_base_url)
        return parsed.port or 11435


settings = Settings()
