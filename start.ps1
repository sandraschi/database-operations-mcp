Param([switch]$Headless)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$env:FASTMCP_LOG_LEVEL = 'WARNING'
# database-operations-mcp Start - Standards-Compliant SOTA
Write-Host 'Starting database-operations-mcp...' -ForegroundColor Cyan

Set-Location $PSScriptRoot
Write-Host 'Starting Standardized Fullstack Hybrid...' -ForegroundColor Green
# Clear stale occupants on backend/frontend ports before bind
foreach ($port in @(10709, 10708)) {
    try {
        $owners = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($pid in $owners) {
            try { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } catch {}
        }
    } catch {}
}
# Launch backend Hidden by default to prevent console spam
Start-Process pwsh -ArgumentList '-NoProfile', '-Command', 'uv run -m database_operations_mcp' -WindowStyle Hidden
# Backend readiness: TCP poll 10709 (max ~30s) instead of fixed sleep
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $tcp = New-Object Net.Sockets.TcpClient
        $iar = $tcp.BeginConnect('127.0.0.1', 10709, $null, $null)
        if ($iar.AsyncWaitHandle.WaitOne(1000)) { $tcp.EndConnect($iar); $ready = $true; $tcp.Close(); break }
        $tcp.Close()
    } catch {}
    Start-Sleep -Seconds 1
}
if (-not $ready) { Write-Warning 'Backend 10709 not reachable after 30s; starting frontend anyway.' }
Set-Location web_sota
if ($SkipFrontend) { return }
npm run dev
