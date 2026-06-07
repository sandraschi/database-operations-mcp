set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

REPO := justfile_directory()

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

pack mcpb-pack:
    Set-Location '{{REPO}}'
    New-Item -ItemType Directory -Force -Path dist | Out-Null
    npx --yes @anthropic-ai/mcpb pack "{{REPO}}" "{{REPO}}/dist/database-operations-mcp-v1.4.1.mcpb"
    Write-Host "Bundle: {{REPO}}/dist/database-operations-mcp-v1.4.1.mcpb"

