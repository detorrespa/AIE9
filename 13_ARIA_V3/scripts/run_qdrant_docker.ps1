# ARIA v3 — Arrancar Qdrant en Docker (localhost:6333)
# Ejecutar desde la raíz: .\scripts\run_qdrant_docker.ps1

$ErrorActionPreference = "Stop"
$projectRoot = (Join-Path $PSScriptRoot "..")
$qdrantData = Join-Path $projectRoot "qdrant_data"

Write-Host "=== ARIA v3 - Qdrant Docker ===" -ForegroundColor Cyan

# 1. Verificar Docker
Write-Host "`n[1] Comprobando Docker..." -ForegroundColor Yellow
try {
    docker info 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Docker no responde" }
    Write-Host "   OK" -ForegroundColor Green
} catch {
    Write-Host "   ERROR: Docker no está en ejecución. Inicia Docker Desktop primero." -ForegroundColor Red
    exit 1
}

# 2. Crear carpeta qdrant_data si no existe
if (-not (Test-Path $qdrantData)) {
    New-Item -ItemType Directory -Path $qdrantData -Force | Out-Null
    Write-Host "`n[2] Carpeta qdrant_data creada" -ForegroundColor Green
} else {
    Write-Host "`n[2] Carpeta qdrant_data OK" -ForegroundColor Green
}

# 3. Iniciar o crear contenedor Qdrant
$existing = docker ps -a --filter "name=qdrant" --format "{{.Names}} {{.Status}}" 2>$null
if ($existing -match "qdrant") {
    Write-Host "`n[3] Contenedor 'qdrant' encontrado. Iniciando..." -ForegroundColor Yellow
    docker start qdrant 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Error al iniciar. Eliminando y recreando..." -ForegroundColor Yellow
        docker rm -f qdrant 2>$null
    }
}
if (-not (docker ps --filter "name=qdrant" -q 2>$null)) {
    Write-Host "`n[3] Creando contenedor Qdrant..." -ForegroundColor Yellow
    docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v "${qdrantData}:/qdrant/storage" qdrant/qdrant
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ERROR al crear el contenedor." -ForegroundColor Red
        exit 1
    }
}
Write-Host "   OK - Qdrant corriendo" -ForegroundColor Green

# 4. Verificar que responde
Write-Host "`n[4] Esperando a que Qdrant responda..." -ForegroundColor Yellow
$maxRetries = 10
for ($i = 0; $i -lt $maxRetries; $i++) {
    try {
        $r = Invoke-RestMethod -Uri "http://localhost:6333/collections" -TimeoutSec 3
        Write-Host "   OK - Qdrant disponible" -ForegroundColor Green
        break
    } catch {
        Start-Sleep -Seconds 2
        if ($i -eq $maxRetries - 1) {
            Write-Host "   Timeout. Comprueba el contenedor con: docker logs qdrant" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "=== Qdrant listo ===" -ForegroundColor Green
Write-Host "  Dashboard: http://localhost:6333/dashboard" -ForegroundColor White
Write-Host "  API: http://localhost:6333" -ForegroundColor White
Write-Host ""
