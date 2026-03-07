# ARIA — Arranque completo: RunPod (túnel) + Qdrant local + Chainlit
# Persistencia: Qdrant en ./qdrant_data (embedded) o ./qdrant_storage (Docker)
# Ejecutar desde la raíz: .\scripts\start_aria_full.ps1

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

# Cargar .env
$envFile = Join-Path $PSScriptRoot "..\.env"
$runpodHost = "213.173.102.237"
$runpodPort = "14002"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "RUNPOD_SSH_HOST=(.+)") { $runpodHost = $matches[1].Trim() }
        if ($_ -match "RUNPOD_SSH_PORT=(.+)") { $runpodPort = $matches[1].Trim() }
    }
}

Write-Host "=== ARIA — Arranque completo (RunPod + Qdrant local) ===" -ForegroundColor Cyan
Write-Host "  RunPod: $runpodHost`:$runpodPort | Qdrant: disco local (qdrant_data/)" -ForegroundColor Gray
Write-Host ""

# 0. Qdrant: la app usa modo embedded (qdrant_data/) — no requiere Docker
Write-Host "[0] Qdrant: modo local (qdrant_data/) — persistencia en disco local OK" -ForegroundColor Green
$qdrantData = Join-Path $PSScriptRoot "..\qdrant_data"
if (-not (Test-Path $qdrantData)) {
    New-Item -ItemType Directory -Path $qdrantData -Force | Out-Null
    Write-Host "    Directorio qdrant_data creado." -ForegroundColor Gray
}

# 1. Túnel RunPod + Ollama
Write-Host "`n[1] RunPod + Ollama..." -ForegroundColor Yellow
& $PSScriptRoot\run_aria_with_tunnel.ps1
