$ErrorActionPreference = "Stop"

Write-Host "Running fixed test script..."

# Run the Python script
try {
    & ".\.venv\Scripts\python.exe" "tests\test_all_tools_fixed.py"
    Write-Host "Test completed successfully"
} catch {
    Write-Host "Error running test: $_" -ForegroundColor Red
    exit 1
}
