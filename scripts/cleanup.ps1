# Clean up any remaining duplicates or incorrect directories
$directoriesToRemove = @(
    "src\database-operations-mcp",
    "database_operations_mcp",
    "fastmcp_database_operations"
)

foreach ($dir in $directoriesToRemove) {
    if (Test-Path $dir) {
        Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue
        Write-Host "Removed duplicate directory: $dir"
    }
}

# Verify the correct structure exists
$requiredDirs = @(
    "src\database_operations\config",
    "src\database_operations\handlers",
    "src\database_operations\models",
    "src\database_operations\services\database\connectors",
    "src\database_operations\static",
    "src\database_operations\templates",
    "tests\unit",
    "tests\integration"
)

foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir"
    }
}

Write-Host "Project structure has been cleaned and verified!"
