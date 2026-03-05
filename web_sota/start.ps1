# Webapp Start - Standardized SOTA (Auto-Repaired V2.5)
$WebPort = 10708
$BackendPort = 10709
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 1. Kill any process squatting on the ports
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Setup
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) { npm install }

# 3. Start the Python backend (Background)
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan

# Backend lives in repo src; run from repo root so browser_bookmarks_tools.server is importable
$backendCmd = "Set-Location '$ProjectRoot'; `$env:PYTHONPATH = '$ProjectRoot\src'; uv run uvicorn browser_bookmarks_tools.server:app --host 127.0.0.1 --port $BackendPort --log-level info"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 4. Wait for backend to be listening (avoid ECONNREFUSED when frontend loads)
$healthUrl = "http://127.0.0.1:$BackendPort/health"
$maxAttempts = 15
$attempt = 0
Write-Host "Waiting for backend at $healthUrl ..." -ForegroundColor Cyan
while ($attempt -lt $maxAttempts) {
    try {
        $null = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        Write-Host "Backend is up." -ForegroundColor Green
        break
    } catch {
        $attempt++
        if ($attempt -ge $maxAttempts) {
            Write-Host "Backend did not respond after ${maxAttempts} attempts. Starting frontend anyway." -ForegroundColor Yellow
            break
        }
        Start-Sleep -Seconds 2
    }
}

# 5. Run server (Vite dev)
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green
npm run dev -- --port $WebPort --host

