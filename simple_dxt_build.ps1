# Simple DXT Package Builder for database-operations-mcp

# Configuration
$ProjectRoot = $PSScriptRoot
$DistDir = Join-Path $ProjectRoot "dist"
$PackageName = "database-operations-mcp"
$OutputFile = Join-Path $DistDir "$PackageName.dxt"

# Create dist directory if it doesn't exist
if (-not (Test-Path -Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir -Force | Out-Null
}

# Build the DXT package
Write-Host "Building DXT package..."
dxt pack --output $OutputFile

# Verify the package was created
if (Test-Path -Path $OutputFile) {
    $fileSize = (Get-Item $OutputFile).Length / 1MB
    Write-Host "✅ Successfully created DXT package: $OutputFile (${fileSize:N2} MB)"
} else {
    Write-Error "❌ Failed to create DXT package"
}
