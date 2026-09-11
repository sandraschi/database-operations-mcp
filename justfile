set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

REPO := justfile_directory()
NAME := "database-operations-mcp"

# --- Dashboard ---

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# --- Install ---

install sync:
    uv sync --extra dev

bootstrap:
    uv sync --extra dev
    uv run pre-commit install
    Set-Location web_sota; npm ci; if ($LASTEXITCODE -ne 0) { npm install }
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green

# --- Runtime ---

mcp:
    uv run database-operations-mcp --stdio

backend:
    uv run database-operations-mcp --http --port 10709

webapp:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{REPO}}/web_sota/start.ps1"

# --- Quality ---

# Execute Ruff SOTA v13.1 linting
lint:
    uv run ruff check src/ tests/
    cd web_sota; npx @biomejs/biome ci --config-path=biome.json .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    uv run ruff check src/ tests/ --fix
    uv run ruff format src/ tests/
    cd web_sota; npx @biomejs/biome check --write --config-path=biome.json .

test:
    uv run pytest tests/unit/ -q

# Serve backend (fleet standard alias; canonical target is `backend` on 10709)
serve:
    uv run database-operations-mcp --http --port 10709

# Format alias (fleet standard name; canonical recipe is `fix`)
fmt:
    uv run ruff check src/ tests/ --fix
    uv run ruff format src/ tests/

# Five-gate local CI (ruff + format-check + pyright + pytest)
ci:
    uv run ruff check src/ tests/
    uv run ruff format src/ tests/ --check
    uv run pyright src/
    uv run pytest tests/ -q

# --- Hardening ---

# Execute Bandit security audit
check-sec:
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    uv run safety check

# --- MCPB ---

MCPB_IGNORE := "{{REPO}}/.mcpbignore"

# Build .mcpb bundle for Claude Desktop
pack mcpb-pack:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\Dev\repos\mcp-central-docs\scripts\make-mcpb.ps1" -RepoPath "{{REPO}}"

# --- Native  Tauri ---

# Build the PyInstaller backend .exe and copy to Tauri resources
build-sidecar:
    powershell.exe -NoProfile -File "{{REPO}}/native/build.ps1"

# Build the Tauri NSIS desktop installer (full pipeline)
build-native:
    powershell.exe -NoProfile -File "{{REPO}}/native/build.ps1"
# --- Playwright E2E ---

# Install Playwright browsers (one-time)
e2e-install:
    Set-Location '{{REPO}}/web_sota'
    npx playwright install chromium

# Run Playwright E2E smoke tests (start backend first: just serve)
e2e:
    Set-Location '{{REPO}}/web_sota'
    npx playwright test

# Bootstrap: install dev deps + pre-commit hook

# Run CUA-NSIS smoke test (install -> launch -> nav walk -> uninstall)
cua-nsis-test:
    powershell.exe -NoProfile -File "{{justfile_directory()}}\scripts\just\cua-nsis-test.ps1"

# Run CUA webapp test (pre-Tauri: start.ps1 stack + nav walk in browser)
cua-webapp-test:
    powershell.exe -NoProfile -File "{{justfile_directory()}}\scripts\just\cua-webapp-test.ps1"
