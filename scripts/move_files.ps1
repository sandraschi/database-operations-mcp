# Move database connector files to the correct location
$sourceDir = "database_operations_mcp/connectors"
$destDir = "src/database_operations/services/database/connectors"

# Create destination directory if it doesn't exist
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
}

# Move Python files from old location to new location
Get-ChildItem -Path $sourceDir -Filter "*.py" | ForEach-Object {
    $destination = Join-Path $destDir $_.Name
    if (Test-Path $_.FullName) {
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
        if (Test-Path $_.FullName) {
            Move-Item -Path $_.FullName -Destination $destination -Force
            Write-Host "Moved $($_.Name) to $handlersDir"
        }
    }
}

# Create main.py if it doesn't exist
$mainPyPath = "src/database_operations/main.py"
if (-not (Test-Path $mainPyPath)) {
    @"
"""Main module for Database Operations MCP."""
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP(
    name="database-operations",
    version="0.1.0"
)

# Import and register handlers
from database_operations.handlers import connection_tools, query_tools, schema_tools, management_tools

# Mount MCP app
app.mount("/mcp", mcp.app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"@ | Out-File -FilePath $mainPyPath -Encoding utf8
    Write-Host "Created main.py"
}

Write-Host "File structure has been reorganized successfully!"
