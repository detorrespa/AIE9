# ARIA — Script de arranque con diagnóstico
# Ejecutar desde la raíz del proyecto: .\scripts\run_aria.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

# Reducir bloqueos de Chainlit/LiteralAI en import (Python 3.13)
$env:LANGCHAIN_TRACING_V2 = "false"
$env:TRACELOOP_TRACING_ENABLED = "false"
$env:OTEL_SDK_DISABLED = "true"

Write-Host "=== ARIA Startup ===" -ForegroundColor Cyan

# 1. Limpiar cache de Python (para que los cambios se apliquen)
Write-Host "`n[1] Limpiando __pycache__..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Write-Host "   OK" -ForegroundColor Green

# 2. Comprobar túnel Ollama
Write-Host "`n[2] Comprobando Ollama (localhost:11435)..." -ForegroundColor Yellow
try {
    $r = Invoke-RestMethod -Uri "http://localhost:11435/api/tags" -TimeoutSec 5
    Write-Host "   OK - Modelos: $($r.models.name -join ', ')" -ForegroundColor Green
} catch {
    Write-Host "   FALLO - Ollama no responde. Abre el tunel SSH primero:" -ForegroundColor Red
    $host = "213.173.102.237"
    $port = "14002"
    if (Test-Path ".\.env") {
        Get-Content ".\.env" | ForEach-Object {
            if ($_ -match "RUNPOD_SSH_HOST=(.+)") { $host = $matches[1].Trim() }
            if ($_ -match "RUNPOD_SSH_PORT=(.+)") { $port = $matches[1].Trim() }
        }
    }
    Write-Host "   ssh -N -L 11435:localhost:11434 -i ~/.ssh/id_ed25519 -p $port root@$host" -ForegroundColor White
    exit 1
}

# 3. Liberar puerto 8000
Write-Host "`n[3] Liberando puerto 8000..." -ForegroundColor Yellow
$netstat = netstat -ano 2>$null
$line = $netstat | Select-String ":8000\s" | Select-Object -First 1
if ($line -and $line.Line -match '\s+(\d+)\s*$') {
    $pidToKill = [int]$matches[1]
    if ($pidToKill -gt 4) {
        Write-Host "   Cerrando proceso anterior (PID $pidToKill)..." -ForegroundColor Yellow
        Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}
Write-Host "   OK" -ForegroundColor Green

# 4. Iniciar Chainlit (preferir .venv312 si existe - Python 3.12 evita colgados)
$venv = if (Test-Path ".\.venv312\Scripts\chainlit.exe") { ".venv312" } else { ".venv" }
Write-Host "`n[4] Iniciando Chainlit en http://localhost:8000 ..." -ForegroundColor Green
Write-Host "    (usando $venv)" -ForegroundColor Gray
Write-Host ""
Write-Host "  (Ctrl+C para parar)`n" -ForegroundColor Gray
& ".\$venv\Scripts\chainlit.exe" run aria/ui/app.py --port 8000 --watch --no-cache
