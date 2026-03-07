"""Utilities for setting up Ollama on a RunPod pod."""

import httpx
from rich.console import Console
from rich.table import Table

from aria.config import settings

console = Console()


def check_ollama_health() -> dict:
    """Check Ollama server health and return status info."""
    base = settings.ollama_base_url
    result = {"reachable": False, "models": [], "llm_ready": False, "embed_ready": False}

    try:
        resp = httpx.get(base, timeout=5.0)
        result["reachable"] = resp.status_code == 200
    except httpx.ConnectError:
        return result

    try:
        resp = httpx.get(f"{base}/api/tags", timeout=10.0)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            result["models"] = models
            result["llm_ready"] = any(settings.ollama_llm_model in m for m in models)
            result["embed_ready"] = any(settings.ollama_embed_model in m for m in models)
    except Exception:
        pass

    return result


def pull_required_models():
    """Pull the LLM and embedding models if not already present."""
    base = settings.ollama_base_url
    status = check_ollama_health()

    if not status["reachable"]:
        console.print("[red]Ollama no accesible. Abre el tunnel primero.[/red]")
        return

    for model_name, label, ready_key in [
        (settings.ollama_llm_model, "LLM", "llm_ready"),
        (settings.ollama_embed_model, "Embeddings", "embed_ready"),
    ]:
        if status[ready_key]:
            console.print(f"[green]✓ {label} ({model_name}) ya disponible.[/green]")
        else:
            console.print(f"[cyan]Descargando {label}: {model_name}...[/cyan]")
            try:
                resp = httpx.post(
                    f"{base}/api/pull",
                    json={"name": model_name, "stream": False},
                    timeout=None,
                )
                if resp.status_code == 200:
                    console.print(f"[green]✓ {label} ({model_name}) descargado.[/green]")
                else:
                    console.print(f"[red]Error descargando {model_name}: {resp.text}[/red]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")


def print_status():
    """Print a status dashboard of the ARIA environment."""
    status = check_ollama_health()

    table = Table(title="ARIA — Estado del Entorno")
    table.add_column("Componente", style="bold")
    table.add_column("Estado")
    table.add_column("Detalle")

    # Ollama
    ok = "✓" if status["reachable"] else "✗"
    color = "green" if status["reachable"] else "red"
    table.add_row("Ollama Server", f"[{color}]{ok}[/{color}]", settings.ollama_base_url)

    # LLM
    ok = "✓" if status["llm_ready"] else "✗"
    color = "green" if status["llm_ready"] else "red"
    table.add_row("LLM Model", f"[{color}]{ok}[/{color}]", settings.ollama_llm_model)

    # Embeddings
    ok = "✓" if status["embed_ready"] else "✗"
    color = "green" if status["embed_ready"] else "red"
    table.add_row("Embed Model", f"[{color}]{ok}[/{color}]", settings.ollama_embed_model)

    # Models list
    if status["models"]:
        table.add_row("Modelos cargados", "", ", ".join(status["models"]))

    console.print(table)
