# Create dist directory if it doesn't exist
$distDir = "dist"
if (-not (Test-Path -Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir | Out-Null
}

# Get the current directory name to use in the output filename
$currentDir = Split-Path -Leaf (Get-Location)
$outputFile = "$distDir\$currentDir.dxt"

# First validate the manifest
Write-Host "Validating manifest..."
dxt validate manifest.json
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Manifest validation failed. Please fix the issues and try again."
    exit 1
}

# Build the DXT package
Write-Host "Building DXT package..."
Set-Location -Path "$PSScriptRoot"
$env:PYTHONPATH = "."
dxt pack . --output $outputFile

# Verify the file was created
if (Test-Path -Path $outputFile) {
    Write-Host "✅ Successfully created DXT package at $outputFile"
    
    # Sign the package
    Write-Host "Signing DXT package..."
    dxt sign $outputFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Successfully signed DXT package"
    } else {
        Write-Host "⚠️ Failed to sign DXT package. Continuing with unsigned package."
    }
} else {
    Write-Host "❌ Failed to create DXT package"
    exit 1
}
