# ARIA v3 — Configuración de Producción

ARIA v3 está configurado para **producción**: usa el servidor Qdrant (Docker) y no tiene fallback al modo embebido. Si Qdrant no está disponible, la aplicación falla de forma explícita.

## Diferencias con aria_v2

| Aspecto | aria_v2 (demos) | aria_v3 (producción) |
|---------|-----------------|----------------------|
| Qdrant | Fallback a `qdrant_data` local si el servidor no responde | **Obligatorio** servidor en `localhost:6333` |
| Persistencia | SQLite embebido | Servidor con almacenamiento propio |
| Dashboard | No disponible | http://localhost:6333/dashboard |

## Requisitos previos

1. **Docker** en ejecución
2. **Qdrant** como contenedor
3. **Ollama** (local o RunPod con túnel SSH)
4. **Python** con dependencias instaladas

## Arranque paso a paso

### 1. Qdrant (Docker)

```bash
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v C:\Dev\aria_v3\qdrant_data:/qdrant/storage qdrant/qdrant
```

- Dashboard: http://localhost:6333/dashboard
- La carpeta `qdrant_data` se creará automáticamente si no existe

### 2. Ollama (RunPod con túnel)

Si usas RunPod para Ollama:

```bash
ssh -N -L 11435:localhost:11434 -L 6333:localhost:6333 -p 15188 -i ~/.ssh/id_ed25519 root@213.173.98.22
```

Ajusta host, puerto y clave según tu `.env`.

### 3. Entorno virtual e ingestión

```bash
cd C:\Dev\aria_v3
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
python scripts/ingest.py
```

La ingesta puede tardar 1–2 horas según el corpus.

### 4. Ejecutar ARIA

```bash
chainlit run aria/ui/app.py
```

## Verificación

- **Qdrant**: http://localhost:6333/dashboard → Collections → `aria_documents`
- **Chainlit**: http://localhost:8000

## Solución de problemas

**"Qdrant server no disponible"**

- Comprueba que Docker está en marcha
- Comprueba que el contenedor `qdrant` está activo: `docker ps`
- Si usas RunPod para Qdrant, añade `-L 6333:localhost:6333` al túnel SSH

**Colección vacía en el dashboard**

- Los datos embebidos de aria_v2 no son compatibles
- Ejecuta `python scripts/ingest.py` en aria_v3
