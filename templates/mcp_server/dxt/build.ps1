<#
.SYNOPSIS
    Build script for creating MCP Server DXT package
.DESCRIPTION
    This script builds the MCP Server package into a DXT file for distribution.
    It handles versioning, dependency installation, and package creation.
#>

param(
    [string]$Version = "0.1.0",
    [string]$OutputDir = "dist",
    [switch]$Clean,
    [switch]$Test,
    [switch]$Help
)

if ($Help) {
    Get-Help $PSCommandPath -Detailed
    exit 0
}

# Error handling
$ErrorActionPreference = 'Stop'

# Check for required tools
$requiredTools = @('python', 'pip', 'dxt')
foreach ($tool in $requiredTools) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Error "Required tool not found: $tool"
        exit 1
    }
}

# Clean previous builds
if ($Clean -and (Test-Path $OutputDir)) {
    Write-Host "Cleaning output directory..."
    Remove-Item -Path $OutputDir -Recurse -Force
}

# Create output directory if it doesn't exist
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Install dependencies
Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
pip install -e .[test]

# Run tests if requested
if ($Test) {
    Write-Host "Running tests..."
    python -m pytest tests/ -v --cov=mcp_server --cov-report=term-missing
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Tests failed. Aborting build."
        exit 1
    }
}

# Build the package
Write-Host "Building package..."
$packageName = "mcp-server-template-$Version.dxt"
$outputPath = Join-Path $OutputDir $packageName

# Create package
Write-Host "Creating DXT package: $outputPath"
dxt pack --output $outputPath .

# Verify package
Write-Host "Verifying package..."
dxt info $outputPath

Write-Host "`nBuild completed successfully!"
Write-Host "Package: $outputPath"

# Update version in pyproject.toml
$pyprojectPath = "pyproject.toml"
if (Test-Path $pyprojectPath) {
    $content = Get-Content $pyprojectPath -Raw
    $newContent = $content -replace 'version = ".*?"', "version = `"$Version`""
    Set-Content -Path $pyprojectPath -Value $newContent
    Write-Host "Updated version in pyproject.toml to $Version"
}

exit 0
