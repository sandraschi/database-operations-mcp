# DXT Package Builder
# This script builds the DXT package from the dxt directory

# Configuration
$projectRoot = Join-Path $PSScriptRoot ".."
$dxtDir = Join-Path $projectRoot "dxt"
$distDir = Join-Path $projectRoot "dist"
$packageName = "database-operations-mcp"
$outputFile = Join-Path $distDir "${packageName}.dxt"

# Create dist directory if it doesn't exist
if (-not (Test-Path -Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir -Force | Out-Null
}

function Write-Header($message) {
    Write-Host "`n=== $message ===`n" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
    exit 1
}

try {
    # Step 1: Validate the manifest
    Write-Header "Validating manifest..."
    Push-Location $projectRoot
    
    $manifestPath = Join-Path $projectRoot "manifest.json"
    if (-not (Test-Path $manifestPath)) {
        Write-Error "manifest.json not found in project root"
    }
    
    # Validate manifest
    dxt validate $manifestPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Manifest validation failed"
    }
    
    # Step 2: Build the DXT package
    Write-Header "Building DXT package..."
    
    # Ensure we're in the project root
    Set-Location $projectRoot
    
    # Build the package
    dxt pack . $outputFile
    
    if (-not (Test-Path $outputFile)) {
        Write-Error "Failed to create DXT package"
    }
    
    $fileSize = (Get-Item $outputFile).Length / 1MB
    Write-Success "Successfully created DXT package: $outputFile (${fileSize:N2} MB)"
    
} catch {
    Write-Error "Build failed: $_"
    exit 1
} finally {
    Pop-Location
}
