#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Install and configure PSScriptAnalyzer for PowerShell linting.

.DESCRIPTION
    Installs PSScriptAnalyzer (the "ruff for PowerShell") and optionally
    creates a configuration file for project-specific rules.

.PARAMETER Install
    Install PSScriptAnalyzer module (default: true)

.PARAMETER Test
    Run linting on all PowerShell scripts in the repo

.EXAMPLE
    .\scripts\setup-powershell-linting.ps1
    # Install PSScriptAnalyzer

.EXAMPLE
    .\scripts\setup-powershell-linting.ps1 -Test
    # Install and test all scripts
#>

param(
    [switch]$Install = $true,
    [switch]$Test = $false
)

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      PowerShell Linting Setup (PSScriptAnalyzer)      ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($Install) {
    Write-Host "📦 Checking PSScriptAnalyzer installation..." -ForegroundColor Yellow

    $module = Get-Module -ListAvailable PSScriptAnalyzer | Select-Object -First 1

    if (-not $module) {
        Write-Host "  Installing PSScriptAnalyzer..." -ForegroundColor Gray
        try {
            Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser -ErrorAction Stop
            Write-Host "  ✅ PSScriptAnalyzer installed successfully" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ Failed to install: $_" -ForegroundColor Red
            Write-Host "  💡 Try running: Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "  ✅ PSScriptAnalyzer already installed (v$($module.Version))" -ForegroundColor Green
    }

    # Import module
    Import-Module PSScriptAnalyzer -Force
    Write-Host ""
}

if ($Test) {
    Write-Host "🔍 Linting PowerShell scripts..." -ForegroundColor Yellow

    $scripts = Get-ChildItem -Path . -Filter "*.ps1" -Recurse | Where-Object {
        $_.FullName -notmatch '\.venv|node_modules|__pycache__'
    }

    if ($scripts.Count -eq 0) {
        Write-Host "  ℹ️  No PowerShell scripts found" -ForegroundColor Gray
        exit 0
    }

    Write-Host "  Found $($scripts.Count) PowerShell script(s)" -ForegroundColor Gray
    Write-Host ""

    $totalIssues = 0
    foreach ($script in $scripts) {
        Write-Host "  📄 $($script.Name)" -ForegroundColor White
        $results = Invoke-ScriptAnalyzer -Path $script.FullName

        if ($results.Count -eq 0) {
            Write-Host "    ✅ No issues found" -ForegroundColor Green
        } else {
            $totalIssues += $results.Count
            foreach ($issue in $results) {
                $severity = switch ($issue.Severity) {
                    "Error" { "🔴" }
                    "Warning" { "🟡" }
                    "Information" { "🔵" }
                    default { "⚪" }
                }
                Write-Host "    $severity $($issue.RuleName): $($issue.Message)" -ForegroundColor Gray
                Write-Host "      Line $($issue.Line): $($issue.ScriptLine)" -ForegroundColor DarkGray
            }
        }
        Write-Host ""
    }

    if ($totalIssues -gt 0) {
        Write-Host "⚠️  Total issues found: $totalIssues" -ForegroundColor Yellow
        Write-Host "💡 Run with -Fix parameter to auto-fix some issues" -ForegroundColor Cyan
        Write-Host ""
        exit 1
    } else {
        Write-Host "✅ All scripts passed linting!" -ForegroundColor Green
        Write-Host ""
    }
} else {
    Write-Host "💡 Usage examples:" -ForegroundColor Cyan
    Write-Host "  Invoke-ScriptAnalyzer -Path scripts\backup-repo.ps1" -ForegroundColor Gray
    Write-Host "  Invoke-ScriptAnalyzer -Path scripts\*.ps1 -Recurse" -ForegroundColor Gray
    Write-Host "  Invoke-ScriptAnalyzer -Path scripts\backup-repo.ps1 -Fix  # Auto-fix" -ForegroundColor Gray
    Write-Host ""
}







