# Create dist directory if it doesn't exist
if (-not (Test-Path -Path "dist")) {
    New-Item -ItemType Directory -Path "dist"
}

# Move the DXT file to dist directory
$dxtFile = Get-ChildItem -Path . -Filter "*.dxt" | Select-Object -First 1
if ($dxtFile) {
    Move-Item -Path $dxtFile.FullName -Destination "dist\$($dxtFile.Name)" -Force
    Write-Host "Moved $($dxtFile.Name) to dist directory"
} else {
    Write-Host "No DXT file found in the current directory"
}
