# Restructure the project to follow FastMCP 2.10.1 standards

# Create necessary directories
$directories = @(
    "src/database_operations/config",
    "src/database_operations/handlers",
    "src/database_operations/models",
    "src/database_operations/services/database/connectors",
    "src/database_operations/static",
    "src/database_operations/templates",
    "tests/unit",
    "tests/integration",
    ".github/workflows"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Write-Host "Created directory: $dir"
}

# Create __init__.py files
$initFiles = @(
    "src/database_operations/__init__.py",
    "src/database_operations/config/__init__.py",
    "src/database_operations/handlers/__init__.py",
    "src/database_operations/models/__init__.py",
    "src/database_operations/services/__init__.py",
    "src/database_operations/services/database/__init__.py",
    "src/database_operations/services/database/connectors/__init__.py",
    "tests/__init__.py",
    "tests/unit/__init__.py",
    "tests/integration/__init__.py"
)

foreach ($file in $initFiles) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
        Write-Host "Created file: $file"
    }
}

# Move database connector files
$sourceDir = "database_operations_mcp/connectors"
$destDir = "src/database_operations/services/database/connectors"

if (Test-Path $sourceDir) {
    Get-ChildItem -Path $sourceDir -Filter "*.py" | ForEach-Object {
        $destination = Join-Path $destDir $_.Name
        Move-Item -Path $_.FullName -Destination $destination -Force
        Write-Host "Moved $($_.Name) to $destDir"
    }
}

# Move tools to handlers
$toolsDir = "database_operations_mcp/tools"
$handlersDir = "src/database_operations/handlers"

if (Test-Path $toolsDir) {
    Get-ChildItem -Path $toolsDir -Filter "*.py" | ForEach-Object {
        $destination = Join-Path $handlersDir $_.Name
        Move-Item -Path $_.FullName -Destination $destination -Force
        Write-Host "Moved $($_.Name) to $handlersDir"
    }
}

# Update imports in moved files
$pythonFiles = Get-ChildItem -Path "src/database_operations" -Filter "*.py" -Recurse

foreach ($file in $pythonFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # Update imports
    $content = $content -replace 'from database_operations_mcp', 'from database_operations'
    $content = $content -replace 'from \.\.', 'from database_operations'
    
    # Write updated content back to file
    $content | Set-Content -Path $file.FullName -NoNewline
    Write-Host "Updated imports in $($file.FullName)"
}

Write-Host "Restructuring complete!"
