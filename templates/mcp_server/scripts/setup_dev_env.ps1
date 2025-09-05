<#
.SYNOPSIS
    Sets up the development environment for the MCP Server.
    
.DESCRIPTION
    This script sets up the development environment by:
    1. Creating a virtual environment
    2. Installing development dependencies
    3. Setting up pre-commit hooks
    4. Creating required configuration files
    
.PARAMETER PythonPath
    Path to the Python executable to use for the virtual environment.
    
.PARAMETER NoVenv
    Skip virtual environment creation and use the current Python environment.
    
.EXAMPLE
    .\setup_dev_env.ps1
    .\setup_dev_env.ps1 -PythonPath "C:\Python39\python.exe"
    .\setup_dev_env.ps1 -NoVenv
#>

param (
    [string]$PythonPath = "python",
    [switch]$NoVenv
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir

Write-Host "Setting up MCP Server development environment..." -ForegroundColor Green

# Check if Python is installed
Write-Host "Checking Python installation..." -NoNewline
$pythonVersion = & $PythonPath --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Error "Python is not installed or not in PATH. Please install Python 3.8+ and try again."
    exit 1
}
Write-Host " $pythonVersion" -ForegroundColor Green

# Create virtual environment if not disabled
$venvPath = Join-Path $rootDir ".venv"
if (-not $NoVenv) {
    Write-Host "Creating virtual environment..." -NoNewline
    if (Test-Path $venvPath) {
        Write-Host " already exists" -ForegroundColor Yellow
    } else {
        & $PythonPath -m venv $venvPath
        if ($LASTEXITCODE -ne 0) {
            Write-Host " FAILED" -ForegroundColor Red
            Write-Error "Failed to create virtual environment."
            exit 1
        }
        Write-Host " done" -ForegroundColor Green
    }
    
    # Activate the virtual environment
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    if (-not (Test-Path $activateScript)) {
        Write-Error "Failed to find virtual environment activation script."
        exit 1
    }
    
    # Set the Python path to the virtual environment's Python
    $PythonPath = Join-Path $venvPath "Scripts\python.exe"
}

# Upgrade pip
Write-Host "Upgrading pip..." -NoNewline
& $PythonPath -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Error "Failed to upgrade pip."
    exit 1
}
Write-Host " done" -ForegroundColor Green

# Install development dependencies
Write-Host "Installing development dependencies..."
$requirementsFiles = @(
    "requirements-dev.txt",
    "requirements.txt"
)

foreach ($file in $requirementsFiles) {
    $reqPath = Join-Path $rootDir $file
    if (Test-Path $reqPath) {
        Write-Host "Installing from $file..." -NoNewline
        & $PythonPath -m pip install -r $reqPath
        if ($LASTEXITCODE -ne 0) {
            Write-Host " FAILED" -ForegroundColor Red
            Write-Warning "Failed to install dependencies from $file. Continuing..."
        } else {
            Write-Host " done" -ForegroundColor Green
        }
    }
}

# Install pre-commit hooks if .pre-commit-config.yaml exists
$preCommitConfig = Join-Path $rootDir ".pre-commit-config.yaml"
if (Test-Path $preCommitConfig) {
    Write-Host "Setting up pre-commit hooks..." -NoNewline
    & $PythonPath -m pre_commit install
    if ($LASTEXITCODE -ne 0) {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Warning "Failed to set up pre-commit hooks. Continuing..."
    } else {
        Write-Host " done" -ForegroundColor Green
    }
}

# Create llms.txt if it doesn't exist
$llmsPath = Join-Path $rootDir "llms.txt"
if (-not (Test-Path $llmsPath)) {
    Write-Host "Creating llms.txt..." -NoNewline
    @"
# List of supported LLM models and their configurations
# Format: model_name|api_key_env_var|base_url(optional)

# OpenAI models
gpt-4-turbo|OPENAI_API_KEY
gpt-3.5-turbo|OPENAI_API_KEY

# Anthropic models
claude-3-opus-20240229|ANTHROPIC_API_KEY
claude-3-sonnet-20240229|ANTHROPIC_API_KEY

# Local models (uncomment and configure as needed)
# local/llama2|LOCAL_LLM_API_KEY|http://localhost:8080
# local/mistral|LOCAL_LLM_API_KEY|http://localhost:8081
"@ | Out-File -FilePath $llmsPath -Encoding utf8
    Write-Host " done" -ForegroundColor Green
}

# Create .env file if it doesn't exist
$envPath = Join-Path $rootDir ".env"
if (-not (Test-Path $envPath)) {
    Write-Host "Creating .env file..." -NoNewline
    @"
# MCP Server Configuration

# Server settings
HOST=0.0.0.0
PORT=8000
DEBUG=True
LOG_LEVEL=INFO

# Authentication (uncomment and configure as needed)
# AUTH_ENABLED=False
# AUTH_TOKEN=your-secret-token

# LLM API Keys (uncomment and add your API keys)
# OPENAI_API_KEY=your-openai-api-key
# ANTHROPIC_API_KEY=your-anthropic-api-key
# LOCAL_LLM_API_KEY=your-local-llm-api-key

# Database settings (uncomment and configure as needed)
# DATABASE_URL=sqlite:///./mcp.db
# DATABASE_URL=postgresql://user:password@localhost:5432/mcp

# Caching settings
# CACHE_ENABLED=True
# CACHE_TTL=300  # 5 minutes
"@ | Out-File -FilePath $envPath -Encoding utf8
    Write-Host " done" -ForegroundColor Green
}

Write-Host "`nDevelopment environment setup complete!" -ForegroundColor Green

if (-not $NoVenv) {
    Write-Host "`nTo activate the virtual environment, run:" -ForegroundColor Cyan
    Write-Host "  .\\.venv\\Scripts\Activate.ps1" -ForegroundColor Yellow
}

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Edit the .env file with your configuration" -ForegroundColor Yellow
Write-Host "2. Run the development server: python -m mcp_server.main" -ForegroundColor Yellow
Write-Host "3. Access the API at http://localhost:8000" -ForegroundColor Yellow
Write-Host "4. View API documentation at http://localhost:8000/docs" -ForegroundColor Yellow
