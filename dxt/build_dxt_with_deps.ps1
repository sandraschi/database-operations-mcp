# Build a self-contained DXT package with all dependencies

# Configuration
$projectRoot = $PSScriptRoot
$distDir = Join-Path $projectRoot "dist"
$packageName = "database-operations-mcp"
$outputFile = Join-Path $distDir "${packageName}_with_deps.dxt"

# Create dist directory if it doesn't exist
if (-not (Test-Path -Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir -Force | Out-Null
}

# Create a temporary directory
$tempDir = Join-Path $env:TEMP "dxt_pkg_$(Get-Random)"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

try {
    Write-Host "🚀 Creating self-contained DXT package..."
    
    # Copy only necessary files
    $excludePatterns = @(
        '.git',
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.pytest_cache',
        '.mypy_cache',
        '.vscode',
        '.idea',
        '*.swp',
        '*.swo',
        '*~',
        '*.bak',
        '*.tmp',
        '*.temp',
        '*.db',
        '*.sqlite',
        '*.sqlite3',
        '*.log',
        'dist',
        'build',
        '*.egg-info',
        '.eggs',
        'htmlcov',
        '.coverage',
        '*.dxt',
        'package_env',
        '.venv',
        'venv',
        'env',
        'test_*',
        'tests',
        '.github'
    )

    # Copy files
    Get-ChildItem -Path $projectRoot -Recurse | ForEach-Object {
        $relativePath = $_.FullName.Substring($projectRoot.Length + 1)
        $exclude = $false
        
        foreach ($pattern in $excludePatterns) {
            if ($relativePath -like $pattern -or $relativePath -like "*\$pattern") {
                $exclude = $true
                break
            }
        }
        
        if (-not $exclude) {
            $targetPath = Join-Path $tempDir $relativePath
            if ($_.PSIsContainer) {
                New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
            } else {
                $targetDir = Split-Path -Parent $targetPath
                if (-not (Test-Path $targetDir)) {
                    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
                }
                Copy-Item -Path $_.FullName -Destination $targetPath -Force
            }
        }
    }

    # Create a virtual environment and install dependencies
    Write-Host "🔧 Setting up virtual environment..."
    $venvPath = Join-Path $tempDir ".venv"
    python -m venv $venvPath

    # Install package in development mode to include all dependencies
    Write-Host "📦 Installing package and dependencies..."
    & "$venvPath\Scripts\pip.exe" install -e "$tempDir"

    # Package everything
    Write-Host "📦 Creating DXT package..."
    Push-Location $tempDir
    try {
        dxt pack . $outputFile
        if (Test-Path $outputFile) {
            $fileSize = (Get-Item $outputFile).Length / 1MB
            Write-Host "✅ Successfully created self-contained DXT package: $outputFile (${fileSize:N2} MB)" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to create DXT package" -ForegroundColor Red
        }
    } finally {
        Pop-Location
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
} finally {
    # Clean up
    Write-Host "🧹 Cleaning up temporary files..."
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "✨ Done!"
