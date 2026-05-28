# database-operations-mcp — Agent Guide

## Overview
Comprehensive FastMCP 3.1.0 server for database operations (SQL, NoSQL, Vector), browser bookmarks, and system tools.

## Entry Points

- `uv run database-operations-mcp` → `database_operations_mcp.main:main`
- `uv run browser-bookmarks` → `browser_bookmarks_tools.mcp_server:main`

## Standards
- FastMCP 3.2+ portmanteau tool pattern — tools use `operation` enum param
- Responses: structured dicts with `success`, `message`, domain-specific fields
- Dual transport: stdio (Claude Desktop) + HTTP (`MCP_TRANSPORT=http`)
- See [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) for fleet-wide coding standards

## Key Files
- `README.md` — full documentation
- `pyproject.toml` — build config and entry points
- `CLAUDE.md` — Claude Code context (if present)

Install docs: follow mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md
