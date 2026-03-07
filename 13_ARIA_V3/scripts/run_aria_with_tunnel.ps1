# ARIA - Arranque con tunel SSH al RunPod y Chainlit
# Ejecutar desde la raiz: .\scripts\run_aria_with_tunnel.ps1

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

# Cargar host/puerto desde .env si existe
$envFile = Join-Path $PSScriptRoot "..\.env"
$runpodHost = "213.173.102.99"
$runpodPort = "33945"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "RUNPOD_SSH_HOST=(.+)") { $runpodHost = $matches[1].Trim() }
        if ($_ -match "RUNPOD_SSH_PORT=(.+)") { $runpodPort = $matches[1].Trim() }
    }
}

Write-Host "=== ARIA Startup (con tunel RunPod) ===" -ForegroundColor Cyan

# 1. Verificar si ya hay túnel/Ollama activo
Write-Host "`n[1] Comprobando Ollama (localhost:11435)..." -ForegroundColor Yellow
try {
    $r = Invoke-RestMethod -Uri "http://localhost:11435/api/tags" -TimeoutSec 5
    Write-Host "   OK - Ollama ya accesible. Modelos: $($r.models.name -join ', ')" -ForegroundColor Green
} catch {
    # 2. Arrancar Ollama en el pod (workspace)
    Write-Host "   No responde. Arrancando Ollama en el pod..." -ForegroundColor Yellow
    $sshKey = Join-Path $env:USERPROFILE ".ssh\id_ed25519"
    if (-not (Test-Path $sshKey)) {
        Write-Host "   ERROR: Clave SSH no encontrada en $sshKey" -ForegroundColor Red
        exit 1
    }
    # Intentar arrancar Ollama. Si no esta instalado, ejecutar setup desde el repo.
    $setupScript = Join-Path $PSScriptRoot "setup_runpod.sh"
    $sshArgs = @("-i", $sshKey, "-p", $runpodPort, "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=30", "-o", "ServerAliveInterval=60", "root@$runpodHost")
    $remoteCmd = "export DEBIAN_FRONTEND=noninteractive; if command -v ollama &>/dev/null; then [ -f /workspace/start_ollama.sh ] && /workspace/start_ollama.sh || (OLLAMA_MODELS=/workspace/.ollama nohup ollama serve & sleep 5); else bash -s; fi"
    Write-Host "   (Ollama en pod: arrancando o instalando si hace falta...)" -ForegroundColor Gray
    Write-Host "   La primera vez puede tardar 10-15 min (descarga de modelos)." -ForegroundColor Gray
    $prevErr = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $scriptContent = Get-Content $setupScript -Raw -ErrorAction SilentlyContinue
        if ($scriptContent) {
            $scriptContent | & ssh @sshArgs $remoteCmd 2>&1 | Out-Null
        } else {
            & ssh @sshArgs "[ -f /workspace/start_ollama.sh ] && /workspace/start_ollama.sh" 2>&1 | Out-Null
        }
    } catch { }
    $ErrorActionPreference = $prevErr
    Start-Sleep -Seconds 8

    # 3. Iniciar túnel SSH al RunPod
    Write-Host "   Iniciando túnel SSH al pod..." -ForegroundColor Yellow
    $tunnelProc = Start-Process ssh -ArgumentList "-N","-L","11435:localhost:11434","-i",$sshKey,"-p",$runpodPort,"root@$runpodHost","-o","StrictHostKeyChecking=no" -PassThru -WindowStyle Hidden
    Write-Host "   Túnel SSH iniciado (PID $($tunnelProc.Id))" -ForegroundColor Green

    # 4. Esperar a que Ollama responda
    Write-Host "`n[2] Esperando a Ollama..." -ForegroundColor Yellow
    $maxRetries = 15
    $ok = $false
    for ($i = 0; $i -lt $maxRetries; $i++) {
        try {
            $r = Invoke-RestMethod -Uri "http://localhost:11435/api/tags" -TimeoutSec 5
            Write-Host "   OK - Ollama accesible." -ForegroundColor Green
            $ok = $true
            break
        } catch {
            Start-Sleep -Seconds 2
            Write-Host "   Reintentando... ($($i+1)/$maxRetries)" -ForegroundColor Gray
        }
    }
    if (-not $ok) {
        Write-Host "   ERROR: Ollama no respondió. Comprueba que Ollama esté corriendo en el pod." -ForegroundColor Red
        $tunnelProc | Stop-Process -Force -ErrorAction SilentlyContinue
        exit 1
    }
}

# 5. Ejecutar run_aria (Chainlit)
Write-Host "`n[3] Iniciando Chainlit..." -ForegroundColor Green
& $PSScriptRoot\run_aria.ps1
