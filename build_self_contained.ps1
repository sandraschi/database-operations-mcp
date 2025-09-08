# Build a self-contained DXT package with all dependencies

# Configuration
$projectRoot = $PSScriptRoot
$tempDir = Join-Path $env:TEMP "dxt_package_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$distDir = Join-Path $projectRoot "dist"
$packageName = "database-operations-mcp"
$outputFile = Join-Path $distDir "${packageName}_with_deps.dxt"

# Create directories
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
New-Item -ItemType Directory -Path $distDir -Force | Out-Null

Write-Host "🚀 Creating self-contained DXT package..."

# Copy project files (exclude unnecessary files)
$exclude = @(
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
    '*.dxt'
)

Write-Host "📂 Copying project files..."
Get-ChildItem -Path $projectRoot -Recurse | Where-Object {
    $include = $true
    foreach ($pattern in $exclude) {
        if ($_.FullName -like "*\$pattern" -or $_.FullName -like "$pattern") {
            $include = $false
            break
        }
    }
    return $include
} | ForEach-Object {
    $targetPath = $_.FullName.Replace($projectRoot, $tempDir)
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

# Create a virtual environment and install dependencies
Write-Host "🔧 Setting up virtual environment..."
$venvPath = Join-Path $tempDir ".venv"
python -m venv $venvPath

# Activate the virtual environment and install package in development mode
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

# Clean up
Write-Host "🧹 Cleaning up temporary files..."
Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✨ Done!"
