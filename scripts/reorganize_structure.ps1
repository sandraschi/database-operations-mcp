# Script to reorganize the directory structure to match FastMCP standards
# This will:
# 1. Move all tools from handlers/tools/ to the root handlers/ directory
# 2. Move the firefox directory to be under tools/
# 3. Clean up any empty directories

$rootDir = "d:\Dev\repos\database-operations-mcp\src\database_operations_mcp"
$handlersDir = Join-Path $rootDir "handlers"
$toolsDir = Join-Path $handlersDir "tools"

# 1. Move all files from tools/ to handlers/
Write-Host "Moving tool files from tools/ to handlers/..."
Get-ChildItem -Path $toolsDir -File | ForEach-Object {
    $destination = Join-Path $handlersDir $_.Name
    if (Test-Path $destination) {
        Write-Host "  Removing existing file: $($_.Name)"
        Remove-Item -Path $destination -Force
    }
    Move-Item -Path $_.FullName -Destination $handlersDir -Force
    Write-Host "  Moved: $($_.Name)"
}

# 2. Move firefox directory to tools/
$firefoxDir = Join-Path $handlersDir "firefox"
$newFirefoxDir = Join-Path $toolsDir "firefox"

if (Test-Path $firefoxDir) {
    Write-Host "Moving firefox/ to tools/firefox/..."
    if (Test-Path $newFirefoxDir) {
        Write-Host "  Removing existing firefox directory in tools/"
        Remove-Item -Path $newFirefoxDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
    Move-Item -Path $firefoxDir -Destination $toolsDir -Force
    Write-Host "  Moved firefox/ to tools/firefox/"
}

# 3. Clean up empty directories
Write-Host "Cleaning up empty directories..."
Get-ChildItem -Path $handlersDir -Directory -Recurse | Where-Object { 
    $_.GetFiles().Count -eq 0 -and $_.GetDirectories().Count -eq 0 
} | ForEach-Object {
    Write-Host "  Removing empty directory: $($_.FullName)"
    Remove-Item -Path $_.FullName -Force
}

# 4. Remove the tools directory if empty
if ((Get-ChildItem -Path $toolsDir -Force | Measure-Object).Count -eq 0) {
    Write-Host "Removing empty tools/ directory..."
    Remove-Item -Path $toolsDir -Force
}

Write-Host "Reorganization complete!"
