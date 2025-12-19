# Database Recovery Check Script
# Checks for recoverable data in SQLite databases

param(
    [string]$DatabasePath = "",
    [switch]$CheckWAL = $true,
    [switch]$CheckBackups = $true
)

Write-Host "=== Database Recovery Check ===" -ForegroundColor Cyan
Write-Host ""

if ($DatabasePath) {
    $dbPath = $DatabasePath
} else {
    Write-Host "Please provide the database path:" -ForegroundColor Yellow
    Write-Host "Usage: .\database-recovery-check.ps1 -DatabasePath 'C:\path\to\database.db'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or let me search for common database locations..." -ForegroundColor Yellow
    Write-Host ""
    
    # Common locations
    $commonPaths = @(
        "$env:USERPROFILE\.advanced-memory\memory.db",
        "$env:APPDATA\*\*.db",
        "C:\Users\$env:USERNAME\Documents\*.db"
    )
    
    Write-Host "Searching common locations..." -ForegroundColor Cyan
    foreach ($pattern in $commonPaths) {
        $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
        if ($files) {
            Write-Host "Found: $($files.FullName)" -ForegroundColor Green
        }
    }
    exit
}

if (-not (Test-Path $dbPath)) {
    Write-Host "ERROR: Database file not found: $dbPath" -ForegroundColor Red
    exit 1
}

Write-Host "Checking database: $dbPath" -ForegroundColor Cyan
Write-Host ""

# Check if database exists
if (Test-Path $dbPath) {
    $dbInfo = Get-Item $dbPath
    Write-Host "Database found:" -ForegroundColor Green
    Write-Host "  Path: $($dbInfo.FullName)"
    Write-Host "  Size: $([math]::Round($dbInfo.Length / 1MB, 2)) MB"
    Write-Host "  Last Modified: $($dbInfo.LastWriteTime)"
    Write-Host ""
}

# Check for WAL file (Write-Ahead Logging - may contain recent data)
if ($CheckWAL) {
    $walPath = "$dbPath-wal"
    if (Test-Path $walPath) {
        $walInfo = Get-Item $walPath
        Write-Host "WAL file found (may contain recent data):" -ForegroundColor Yellow
        Write-Host "  Path: $($walInfo.FullName)"
        Write-Host "  Size: $([math]::Round($walInfo.Length / 1MB, 2)) MB"
        Write-Host "  Last Modified: $($walInfo.LastWriteTime)"
        Write-Host ""
        Write-Host "  NOTE: WAL files can contain uncommitted transactions!" -ForegroundColor Yellow
        Write-Host "  You may be able to recover data by checking the WAL file." -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host "No WAL file found." -ForegroundColor Gray
        Write-Host ""
    }
    
    # Check for SHM file
    $shmPath = "$dbPath-shm"
    if (Test-Path $shmPath) {
        Write-Host "SHM file found: $shmPath" -ForegroundColor Yellow
        Write-Host ""
    }
}

# Check for backup files
if ($CheckBackups) {
    $backupDir = Split-Path $dbPath -Parent
    $backupPatterns = @(
        "$dbPath.backup",
        "$dbPath.bak",
        "$backupDir\*.db.backup",
        "$backupDir\*.db.bak",
        "$backupDir\backup\*.db"
    )
    
    Write-Host "Checking for backup files..." -ForegroundColor Cyan
    $foundBackups = $false
    foreach ($pattern in $backupPatterns) {
        $backups = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
        if ($backups) {
            $foundBackups = $true
            foreach ($backup in $backups) {
                Write-Host "  Backup found: $($backup.FullName)" -ForegroundColor Green
                Write-Host "    Size: $([math]::Round($backup.Length / 1MB, 2)) MB"
                Write-Host "    Modified: $($backup.LastWriteTime)"
            }
        }
    }
    
    if (-not $foundBackups) {
        Write-Host "  No backup files found." -ForegroundColor Gray
    }
    Write-Host ""
}

# Try to query database to see what's left
Write-Host "Attempting to query database..." -ForegroundColor Cyan
try {
    Add-Type -Path "System.Data.SQLite.dll" -ErrorAction SilentlyContinue
    $connectionString = "Data Source=$dbPath;Version=3;"
    $connection = New-Object System.Data.SQLite.SQLiteConnection($connectionString)
    $connection.Open()
    
    $command = $connection.CreateCommand()
    $command.CommandText = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    $reader = $command.ExecuteReader()
    
    $tables = @()
    while ($reader.Read()) {
        $tables += $reader["name"]
    }
    
    Write-Host "Tables found: $($tables.Count)" -ForegroundColor $(if ($tables.Count -gt 0) { "Green" } else { "Red" })
    foreach ($table in $tables) {
        $countCmd = $connection.CreateCommand()
        $countCmd.CommandText = "SELECT COUNT(*) as cnt FROM [$table];"
        $count = $countCmd.ExecuteScalar()
        Write-Host "  $table : $count rows" -ForegroundColor $(if ($count -gt 0) { "Green" } else { "Yellow" })
    }
    
    $connection.Close()
} catch {
    Write-Host "  Could not query database (SQLite library may not be available)" -ForegroundColor Yellow
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Recovery Recommendations ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. If WAL file exists, data may be recoverable by merging WAL into database"
Write-Host "2. Check for backup files in the same directory"
Write-Host "3. Check Windows File History or System Restore points"
Write-Host "4. Check if your application has automatic backups enabled"
Write-Host "5. If using version control, check git history for database files"
Write-Host ""
