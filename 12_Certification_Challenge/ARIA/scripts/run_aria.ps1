# ARIA — Script de arranque con diagnóstico
# Ejecutar desde la raíz del proyecto: .\scripts\run_aria.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

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
    Write-Host "   ssh -N -L 11435:localhost:11434 -i ~/.ssh/id_ed25519 -p 11435 root@213.173.102.206" -ForegroundColor White
    exit 1
}

# 3. Matar procesos Chainlit en puerto 8000
Write-Host "`n[3] Comprobando puerto 8000..." -ForegroundColor Yellow
$proc = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($proc) {
    Write-Host "   Cerrando proceso anterior (PID $proc)..." -ForegroundColor Yellow
    Stop-Process -Id $proc -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}
Write-Host "   OK" -ForegroundColor Green

# 4. Iniciar Chainlit
Write-Host "`n[4] Iniciando Chainlit en http://localhost:8000 ..." -ForegroundColor Green
Write-Host ""
Write-Host "  IMPORTANTE para ver los cambios:" -ForegroundColor Yellow
Write-Host "  - Pulsa Ctrl+Shift+R (o Ctrl+F5) en el navegador para recargar sin cache" -ForegroundColor White
Write-Host "  - Clic en 'New Chat' para ver el mensaje de bienvenida actualizado" -ForegroundColor White
Write-Host ""
Write-Host "  (Ctrl+C para parar)`n" -ForegroundColor Gray
.\.venv\Scripts\chainlit.exe run aria/ui/app.py --port 8000 --watch --no-cache
