<#
.SYNOPSIS
    Builds, signs, and verifies MCP server packages using DXT.

.DESCRIPTION
    This script automates the process of building DXT packages for MCP servers.
    It handles building, signing, and verifying the package in a single command.
    The script is designed to be used across all MCP server repositories.

.PARAMETER NoSign
    Skip the package signing step. Useful for development or testing.

.PARAMETER OutputDir
    Specify a custom output directory for the built package. Defaults to './dist'.

.PARAMETER Help
    Show this help message and exit.

.EXAMPLE
    # Build and sign a package (default behavior)
    .\scripts\build-mcp-package.ps1

    # Build without signing
    .\scripts\build-mcp-package.ps1 -NoSign

    # Specify custom output directory
    .\scripts\build-mcp-package.ps1 -OutputDir "C:\builds"

.NOTES
    - Requires DXT CLI to be installed and available in PATH
    - The package name is derived from the project directory name
    - The script will create the output directory if it doesn't exist
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [switch]$NoSign = $false,
    
    [Parameter(Mandatory = $false)]
    [string]$OutputDir = "$PSScriptRoot\..\dist",
    
    [Parameter(Mandatory = $false)]
    [switch]$Help
)

# Show help if requested
if ($Help) {
    Get-Help $PSCommandPath -Detailed
    exit 0
}

# Set error action preference
$ErrorActionPreference = "Stop"

# Configuration
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PackageName = Split-Path -Leaf $ProjectRoot
$OutputFile = Join-Path $OutputDir "$PackageName.dxt"

function Write-Header($message) {
    Write-Host "`n=== $message ===`n" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "⚠️ $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
    exit 1
}

try {
    # Step 1: Validate the manifest
    Write-Header "Validating manifest..."
    Push-Location $ProjectRoot
    
    $manifestPath = Join-Path $ProjectRoot "manifest.json"
    if (-not (Test-Path $manifestPath)) {
        Write-Error "manifest.json not found in project root"
    }
    
    $manifest = Get-Content -Path $manifestPath -Raw | ConvertFrom-Json
    
    # Basic manifest validation
    $requiredFields = @("name", "version", "dxt_version", "server")
    foreach ($field in $requiredFields) {
        if (-not $manifest.PSObject.Properties.Name -contains $field) {
            Write-Error "Missing required field in manifest: $field"
        }
    }
    
    # Validate server configuration
    $server = $manifest.server
    if ($server.type -ne "python") {
        Write-Error "Only 'python' server type is supported"
    }
    
    if (-not $server.mcp_config) {
        Write-Error "mcp_config is required in the server configuration"
    }
    
    Write-Success "Manifest validation passed"
    
    # Step 2: Create output directory if it doesn't exist
    if (-not (Test-Path -Path $OutputDir)) {
        Write-Host "Creating output directory: $OutputDir"
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }
    
    # Step 3: Build the DXT package
    Write-Header "Building DXT package..."
    
    # Clean previous build if exists
    if (Test-Path $OutputFile) {
        Remove-Item $OutputFile -Force
    }
    
    # Set Python path to include the project root
    $env:PYTHONPATH = $ProjectRoot
    
    # Build the package
    $buildResult = dxt pack . $OutputDir 2>&1
    
    # Rename the output file to include the package name
    $defaultOutput = Join-Path $OutputDir "package.dxt"
    if (Test-Path $defaultOutput) {
        Rename-Item -Path $defaultOutput -NewName (Split-Path $OutputFile -Leaf) -Force
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build DXT package: $buildResult"
    }
    
    if (-not (Test-Path $OutputFile)) {
        Write-Error "DXT package was not created successfully"
    }
    
    Write-Success "Successfully created DXT package: $OutputFile"
    
    # Step 4: Sign the package (unless --NoSign is specified)
    if ($NoSign) {
        Write-Warning "Skipping package signing as requested (--NoSign flag was used)"
    } else {
        Write-Header "Signing DXT package..."
        
        $signResult = dxt sign $OutputFile 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to sign DXT package: $signResult"
        }
        
        Write-Success "Package signed successfully"
    }
    
    # Step 5: Verify the package
    Write-Header "Verifying DXT package..."
    $verifyResult = dxt verify $OutputFile 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Package verification failed: $verifyResult"
    }
    
    Write-Success "Package verification passed"
    
    # Final output
    Write-Host "`n🎉 DXT package created successfully!" -ForegroundColor Green
    Write-Host "Package: $OutputFile"
    
} catch {
    Write-Error "Build failed: $_"
    exit 1
} finally {
    Pop-Location
}
