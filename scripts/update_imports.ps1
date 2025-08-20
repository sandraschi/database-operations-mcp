# Update imports in Python files to match the new structure
$pythonFiles = Get-ChildItem -Path src -Include *.py -Recurse

foreach ($file in $pythonFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # Update imports
    $content = $content -replace 'from database_operations_mcp', 'from database_operations'
    $content = $content -replace 'from \.\.', 'from database_operations'
    $content = $content -replace 'from \.', 'from database_operations'
    
    # Update relative imports
    $content = $content -replace 'from \.connectors', 'from database_operations.services.database.connectors'
    $content = $content -replace 'from \.tools', 'from database_operations.handlers'
    $content = $content -replace 'from \.utils', 'from database_operations.utils'
    
    # Save the updated content
    $content | Set-Content -Path $file.FullName -Encoding utf8
    
    Write-Host "Updated imports in $($file.FullName)"
}

Write-Host "All imports have been updated to match the new structure!"
