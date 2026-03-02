"""SSH tunnel management for connecting to Ollama on RunPod."""

import subprocess
import sys
import time
from pathlib import Path

import httpx
from rich.console import Console

from aria.config import settings

console = Console()


class OllamaTunnel:
    """Manages an SSH tunnel to a RunPod pod running Ollama."""

    def __init__(self):
        self._process: subprocess.Popen | None = None

    @property
    def is_active(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def open(self, timeout: int = 15) -> bool:
        """Open SSH tunnel to RunPod. Returns True if tunnel + Ollama are reachable."""
        if self.is_active:
            console.print("[yellow]Tunnel ya está activo.[/yellow]")
            return True

        if not settings.runpod_ssh_host:
            console.print(
                "[red]RUNPOD_SSH_HOST no configurado. Revisa tu archivo .env[/red]"
            )
            return False

        key_path = Path(settings.runpod_ssh_key_path).expanduser()
        if not key_path.exists():
            console.print(f"[red]SSH key no encontrada: {key_path}[/red]")
            return False

        local_port = settings.local_ollama_port
        cmd = [
            "ssh",
            "-N",
            "-L", f"{local_port}:localhost:11434",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=30",
            "-o", "ServerAliveCountMax=3",
            "-i", str(key_path),
            "-p", str(settings.runpod_ssh_port),
            f"{settings.runpod_ssh_user}@{settings.runpod_ssh_host}",
        ]

        console.print(f"[cyan]Abriendo tunnel SSH → {settings.runpod_ssh_host}:{settings.runpod_ssh_port} "
                       f"(local :{local_port} → remote :11434)...[/cyan]")

        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

        return self._wait_for_ollama(timeout)

    def _wait_for_ollama(self, timeout: int) -> bool:
        """Poll Ollama endpoint until it responds or timeout."""
        url = settings.ollama_base_url
        console.print(f"[cyan]Esperando a que Ollama responda en {url}...[/cyan]")

        for i in range(timeout):
            try:
                resp = httpx.get(url, timeout=2.0)
                if resp.status_code == 200:
                    console.print("[green]✓ Ollama accesible via tunnel SSH.[/green]")
                    return True
            except httpx.ConnectError:
                pass

            if not self.is_active:
                stderr = self._process.stderr.read().decode() if self._process.stderr else ""
                console.print(f"[red]Tunnel SSH cerrado inesperadamente: {stderr}[/red]")
                return False

            time.sleep(1)
            console.print(f"  Reintentando... ({i + 1}/{timeout})")

        console.print("[red]Timeout: Ollama no respondió.[/red]")
        return False

    def close(self):
        """Terminate the SSH tunnel."""
        if self._process and self._process.poll() is None:
            self._process.terminate()
            self._process.wait(timeout=5)
            console.print("[yellow]Tunnel SSH cerrado.[/yellow]")
        self._process = None


tunnel = OllamaTunnel()
