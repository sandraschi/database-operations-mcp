set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

REPO := justfile_directory()
NAME := "database-operations-mcp"

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# ── Install ───────────────────────────────────────────────────────────────────

install sync:
    Set-Location '{{REPO}}'
    uv sync --extra dev

# ── Runtime ───────────────────────────────────────────────────────────────────

mcp:
    Set-Location '{{REPO}}'
    uv run database-operations-mcp --stdio

backend:
    Set-Location '{{REPO}}'
    uv run database-operations-mcp --http --port 10708

webapp:
    pwsh -NoProfile -ExecutionPolicy Bypass -File "{{REPO}}/web_sota/start.ps1"

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff SOTA v13.1 linting
lint:
    Set-Location '{{REPO}}'
    uv run ruff check src/ tests/
    Set-Location '{{REPO}}/web_sota'
    npx @biomejs/biome ci .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{REPO}}'
    uv run ruff check src/ tests/ --fix
    uv run ruff format src/ tests/
    Set-Location '{{REPO}}/web_sota'
    npx @biomejs/biome check --write .

test:
    Set-Location '{{REPO}}'
    uv run pytest tests/unit/ -q

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    Set-Location '{{REPO}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{REPO}}'
    uv run safety check

# ── MCPB ──────────────────────────────────────────────────────────────────────

MCPB_IGNORE := "{{REPO}}/.mcpbignore"

# Build .mcpb bundle for Claude Desktop
pack mcpb-pack:
    pwsh -NoProfile -File "{{REPO}}/scripts/mcpb-pack.ps1" -RepoRoot "{{REPO}}"

# ── Native / Tauri ─────────────────────────────────────────────────────────────

# Build the PyInstaller backend .exe and copy to Tauri resources
build-sidecar:
    pwsh -NoProfile -File "{{REPO}}/native/build.ps1"

# Build the Tauri NSIS desktop installer (full pipeline)
build-native:
    pwsh -NoProfile -File "{{REPO}}/native/build.ps1"
# ── Playwright E2E ─────────────────────────────────────────────────────

# Install Playwright browsers (one-time)
e2e-install:
    cd {{REPO}}\web_sota
    npx playwright install chromium

# Run Playwright E2E smoke tests (start backend first: just serve)
e2e:
    cd {{REPO}}\web_sota
    npx playwright test

