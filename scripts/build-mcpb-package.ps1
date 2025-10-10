<#
.SYNOPSIS
    Builds MCPB package for database-operations-mcp

.DESCRIPTION
    Automated build script for creating MCPB (MCP Bundle) packages.
    Validates manifest, builds package, and optionally signs it.

.PARAMETER NoSign
    Skip package signing (for development builds)

.PARAMETER OutputDir
    Custom output directory (default: dist)

.PARAMETER Help
    Show this help message

.EXAMPLE
    .\scripts\build-mcpb-package.ps1 -NoSign
    .\scripts\build-mcpb-package.ps1 -OutputDir "C:\builds"

.NOTES
    Requires: MCPB CLI (@anthropic-ai/mcpb)
    Requires: Python 3.9+
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

# Show help
if ($Help) {
    Get-Help $PSCommandPath -Detailed
    exit 0
}

# Error handling
$ErrorActionPreference = "Stop"

# Configuration
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PackageName = "database-operations-mcp"
$OutputFile = Join-Path $OutputDir "$PackageName.mcpb"

# Colors
function Write-Header($message) {
    Write-Host "`n=== $message ===`n" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "⚠️ $message" -ForegroundColor Yellow
}

function Write-Error-Message($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

try {
    Push-Location $ProjectRoot
    
    # Step 1: Check prerequisites
    Write-Header "Checking Prerequisites"
    
    # Check MCPB CLI
    try {
        $mcpbVersion = mcpb --version 2>&1
        Write-Success "MCPB CLI installed: $mcpbVersion"
    } catch {
        Write-Error-Message "MCPB CLI not found. Install with: npm install -g @anthropic-ai/mcpb"
        exit 1
    }
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python installed: $pythonVersion"
    } catch {
        Write-Error-Message "Python not found. Please install Python 3.9+"
        exit 1
    }
    
    # Check manifest exists
    $manifestPath = Join-Path $ProjectRoot "manifest.json"
    if (-not (Test-Path $manifestPath)) {
        Write-Error-Message "manifest.json not found in project root"
        exit 1
    }
    Write-Success "Found manifest.json"
    
    # Step 2: Validate manifest
    Write-Header "Validating Manifest"
    
    $validateResult = mcpb validate $manifestPath 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Message "Manifest validation failed: $validateResult"
        exit 1
    }
    Write-Success "Manifest validation passed"
    
    # Step 3: Create output directory
    if (-not (Test-Path -Path $OutputDir)) {
        Write-Host "Creating output directory: $OutputDir"
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }
    
    # Clean previous build
    if (Test-Path $OutputFile) {
        Remove-Item $OutputFile -Force
        Write-Host "Removed previous build"
    }
    
    # Step 4: Build MCPB package
    Write-Header "Building MCPB Package"
    
    $env:PYTHONPATH = $ProjectRoot
    
    # mcpb pack expects: mcpb pack <source> <output_file>
    $buildResult = mcpb pack . $OutputFile 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Message "Build failed: $buildResult"
        exit 1
    }
    
    if (-not (Test-Path $OutputFile)) {
        Write-Error-Message "Package not created successfully"
        exit 1
    }
    
    Write-Success "Package built successfully"
    
    # Step 5: Sign package (optional)
    if ($NoSign) {
        Write-Warning "Skipping package signing (-NoSign flag)"
    } else {
        Write-Header "Signing Package"
        
        $signResult = mcpb sign $OutputFile 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Package signing failed (continuing anyway): $signResult"
        } else {
            Write-Success "Package signed successfully"
        }
    }
    
    # Step 6: Verify package
    Write-Header "Verifying Package"
    
    $verifyResult = mcpb verify $OutputFile 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Package verification failed: $verifyResult"
    } else {
        Write-Success "Package verification passed"
    }
    
    # Final output
    Write-Host "`n🎉 MCPB package created successfully!" -ForegroundColor Green
    Write-Host "Package: $OutputFile" -ForegroundColor White
    
    $fileInfo = Get-Item $OutputFile
    $sizeKB = [math]::Round($fileInfo.Length/1KB, 2)
    $sizeMB = [math]::Round($fileInfo.Length/1MB, 2)
    
    if ($sizeMB -ge 1) {
        Write-Host "Size: $sizeMB MB" -ForegroundColor White
    } else {
        Write-Host "Size: $sizeKB KB" -ForegroundColor White
    }
    
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Test: Drag $OutputFile to Claude Desktop" -ForegroundColor White
    Write-Host "2. Verify: Check all tools work correctly" -ForegroundColor White
    Write-Host "3. Release: Create GitHub tag and push" -ForegroundColor White
    
} catch {
    Write-Error-Message "Build failed: $_"
    exit 1
} finally {
    Pop-Location
}

