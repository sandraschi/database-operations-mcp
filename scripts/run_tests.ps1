<#
.SYNOPSIS
    Run unit tests for the project with proper environment setup.
.DESCRIPTION
    This script ensures all test dependencies are installed and runs the unit tests.
    It's designed to work in both development environments and CI/CD pipelines.
#>

# Stop on first error
$ErrorActionPreference = "Stop"

# Set up environment
$env:PYTHONPATH = "."

# Install test dependencies
Write-Host "Installing test dependencies..." -ForegroundColor Cyan
pip install -r requirements-dev.txt

# Run tests with coverage
Write-Host "Running tests..." -ForegroundColor Cyan
$testResults = python -m pytest tests/unit/ -v --cov=database_operations_mcp --cov-report=term-missing

# Check test results
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "All tests passed!" -ForegroundColor Green
