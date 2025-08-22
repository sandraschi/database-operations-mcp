# Simple build script for DXT package

# Set working directory to script location
$scriptPath = $PSScriptRoot
Set-Location -Path $scriptPath

# Create dist directory if it doesn't exist
$distDir = "$scriptPath\dist"
if (-not (Test-Path -Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir -Force | Out-Null
}

# Clean up old package if it exists
$packageName = "database-operations-mcp.dxt"
$packagePath = "$distDir\$packageName"
if (Test-Path -Path $packagePath) {
    Remove-Item -Path $packagePath -Force
}

# Build the DXT package directly in the dist directory
Write-Host "Building DXT package in $distDir..."

# Set PYTHONPATH to include the current directory
$env:PYTHONPATH = "."

# Change to the dxt directory if it exists, otherwise use the current directory
if (Test-Path -Path "$scriptPath\dxt") {
    Set-Location -Path "$scriptPath\dxt"
}

# Run dxt pack with correct syntax
dxt pack . "$packagePath"

# Verify the package was created
if (Test-Path -Path $packagePath) {
    Write-Host "✅ Successfully created DXT package at $packagePath"
    exit 0
} else {
    Write-Host "❌ Failed to create DXT package"
    exit 1
}
