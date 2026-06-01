# database-operations-mcp — Agent Guide

## Overview
Comprehensive FastMCP 3.3 server for database operations (SQL, NoSQL, vector) and system tools.

## Entry Points

- `uv run database-operations-mcp` → stdio MCP or `--http` for web_sota REST bridge (port **10709**)
- `web_sota/start.ps1` → Vite frontend on **10708**

## Standards
- FastMCP 3.2+ portmanteau tool pattern — tools use `operation` enum param
- Responses: structured dicts with `success`, `message`, domain-specific fields
- Webapp: `/logs` page + `/api/logs` per mcp-central-docs `WEBAPP_LOGS_PAGE.md`
- See [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) for fleet-wide coding standards

## Key Files
- `README.md` — full documentation
- `pyproject.toml` — build config and entry points
- `src/database_operations_mcp/http_app.py` — FastAPI web bridge
- `justfile` — dev recipes

Install docs: follow mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md

## Quick Ref

```powershell
uv run pytest tests/unit/test_web_api.py -q
```
