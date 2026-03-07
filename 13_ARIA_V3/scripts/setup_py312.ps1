# ARIA - Crear entorno Python 3.12 (Chainlit no funciona bien con 3.13)
# Requiere: Python 3.12 instalado desde https://www.python.org/downloads/
# Ejecutar: .\scripts\setup_py312.ps1

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

Write-Host "=== ARIA - Setup Python 3.12 ===" -ForegroundColor Cyan

$py312 = Get-Command python3.12 -ErrorAction SilentlyContinue
if (-not $py312) {
    $py312 = Get-Command py -ErrorAction SilentlyContinue
    if ($py312) {
        $ver = & py -3.12 --version 2>$null
        if (-not $ver) { $py312 = $null }
    }
}
if (-not $py312) {
    Write-Host "`nERROR: Python 3.12 no encontrado." -ForegroundColor Red
    Write-Host "Descargalo de: https://www.python.org/downloads/release/python-3120/" -ForegroundColor White
    Write-Host "Durante la instalacion, marca 'Add Python to PATH'" -ForegroundColor White
    exit 1
}

Write-Host "`n[1] Creando .venv con Python 3.12..." -ForegroundColor Yellow
if (Test-Path .venv312) { Remove-Item .venv312 -Recurse -Force }
if ($py312.Source -match "py\.exe") {
    & py -3.12 -m venv .venv312
} else {
    & python3.12 -m venv .venv312
}
if (-not (Test-Path .venv312\Scripts\pip.exe)) {
    Write-Host "   Ejecutando ensurepip..." -ForegroundColor Gray
    & .venv312\Scripts\python.exe -m ensurepip --upgrade
}

Write-Host "`n[2] Instalando dependencias..." -ForegroundColor Yellow
& .venv312\Scripts\pip.exe install -e ".[dev]" --quiet

Write-Host "`n=== Listo ===" -ForegroundColor Green
Write-Host "Ejecuta: .\scripts\run_aria.ps1" -ForegroundColor White
