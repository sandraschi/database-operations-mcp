[![FastMCP Version](https://img.shields.io/badge/FastMCP-3.1.0-blue?style=flat-square&logo=python&logoColor=white)](https://github.com/sandraschi/fastmcp) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Linted with Biome](https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white)](https://biomejs.dev/) [![Built with Just](https://img.shields.io/badge/Built_with-Just-000000?style=flat-square&logo=gnu-bash&logoColor=white)](https://github.com/casey/just)

[![Version](https://img.shields.io/badge/version-1.4.1-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.1-orange.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
# Database Operations MCP

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>


> 📖 **[Installation Guide](INSTALL.md)** — quick start, manual setup, and troubleshooting

FastMCP 3.3 MCP server for database operations on Windows. Includes MCP prompts and a bundled database-expert skill. Browser bookmark management lives in [bookmarks-mcp](https://github.com/sandraschi/bookmarks-mcp).

## Scope
- Database tools (inspection, backup/restore, analysis, Windows application databases)
- Media library tools (Calibre, Plex)
- Windows Registry and system utilities

## Tools Overview

Portmanteau tools consolidate individual operations into unified interfaces.

### Database Tools
- `db_connection` - Database connection management portmanteau (consolidates connection_tools, init_tools)
  - Operations: list_supported, register, init, list, test, test_all, close, get_info, restore, set_active, get_active, get_preferences, set_preferences
- `db_operations` - Query execution, transactions, batch operations, data export portmanteau (consolidates query_tools, data_tools)
  - Operations: execute_query, execute_transaction, execute_write, batch_insert, quick_data_sample, export_query_results
- `db_schema` - Schema inspection, table/column/index analysis portmanteau (consolidates schema_tools)
  - Operations: list_databases, list_tables, describe_table, get_schema_diff
- `db_management` - Database health checks, optimization, backup/restore portmanteau (consolidates management_tools)
- `db_fts` - Full-text search with ranking and highlighting portmanteau (consolidates fts_tools)
- `db_analyzer` - Comprehensive database analysis and diagnostics portmanteau
- `agentic_workflow_tool` - FastMCP sampling-enabled agentic workflows for complex database operations
- `windows_system` - Windows Registry, service status, system info portmanteau (consolidates registry_tools, windows_tools)

### Media & Other Tools
- `media_library` - Calibre & Plex library management portmanteau (consolidates calibre_tools, plex_tools, media_tools)
- `help_system` - Interactive help and documentation portmanteau (consolidates help_tools)
- `system_init` - System initialization and setup portmanteau

### Deprecated Tools (Use Portmanteau Equivalents)
Individual tools are deprecated but kept for backwards compatibility. Migration paths:
- `connection_tools.*`  `db_connection(operation='...')`
- `init_tools.*`  `db_connection(operation='...')`
- `query_tools.*`  `db_operations(operation='...')`
- `data_tools.*`  `db_operations(operation='...')`
- `schema_tools.*`  `db_schema(operation='...')`
- `management_tools.*`  `db_management(operation='...')`
- `fts_tools.*`  `db_fts(operation='...')`
- `calibre_tools.*`  `media_library(operation='...')`
- `plex_tools.*`  `media_library(operation='...')`
- `registry_tools.*`  `windows_system(operation='...')`
- `windows_tools.*`  `windows_system(operation='...')`

*See individual tool files in `src/database_operations_mcp/tools/` for complete API documentation.*

## Core Database Features
- SQLite utilities: open/read, schema introspection, queries, export
- Backup and restore helpers for common Windows application databases
- Windows paths helpers (browser history DBs, Outlook, etc.)
- Safety helpers (file locks, status checks) with clear error messages
- MCP tools organized under `src/database_operations_mcp/tools/`

## Project Layout
```
database-operations-mcp/
 src/
    database_operations_mcp/
        main.py                      # MCP server entry
        config/
           mcp_config.py            # shared MCP instance
        tools/                     # portmanteau + atomic DB tools
        services/database/         # DB connectors
 tests/
 web_sota/                        # React dashboard (optional)
 README.md
```

##  Packaging & Distribution

This repository is SOTA 2026 compliant and uses the officially validated `@anthropic-ai/mcpb` workflow for distribution.

### Pack Extension
To generate a `.mcpb` distribution bundle with complete source code and automated build exclusions:
```bash
# SOTA 2026 standard pack command
mcpb pack . dist/database-operations-mcp.mcpb
```

## Quick Start

```powershell
git clone https://github.com/sandraschi/database-operations-mcp
cd database-operations-mcp
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:


## Install Zed Extension
This repository includes a Zed extension for native integration with the Zed editor.

### Prerequisites
- Rust toolchain installed (`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`)

### Build the Extension
```bash
cd zed-extension
cargo build --release --target wasm32-wasip1
```

### Install in Zed
1. Open Zed
2. Go to `Extensions`  `Install Dev Extension`
3. Navigate to the repository and select: `zed-extension/extension.toml`
4. The Database Operations MCP extension will be installed and loaded

**Note:** The extension runs the MCP server from the parent directory, so make sure you're in the correct repository location.

### Zed Extension Features
- MCP server integration within Zed
- Database operations accessible from Zed's AI assistant
- Context server management
- Integration with Zed's codebase understanding

## Configure in Cursor / Claude (recommended)
## Transports: stdio and HTTP
- Default: dual (both stdio and HTTP) unless overridden
- Override via env: set `MCP_TRANSPORT=stdio|http|dual`
- HTTP host/port via `MCP_HOST` (default `0.0.0.0`) and `MCP_PORT` (default `8000`)
- CLI flags: `--stdio`, `--http`, `--dual`

```powershell
# HTTP only on port 3210
$env:MCP_TRANSPORT = "http"
$env:MCP_PORT = "3210"
uv run python -m database_operations_mcp.main --http

# Dual mode (stdio + HTTP) with custom host/port
$env:MCP_TRANSPORT = "dual"
$env:MCP_HOST = "127.0.0.1"
$env:MCP_PORT = "9000"
uv run python -m database_operations_mcp.main --dual
```
Add the server to your MCP config (`%USERPROFILE%\AppData\Roaming\Cursor\.cursor\mcp.json` or equivalent):

```json
{
  "mcpServers": {
    "database-operations-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "database_operations_mcp.main"],
      "env": { "LOG_LEVEL": "INFO" }
    }
  }
}
```

## Development
For Python development setup, testing, and contribution guidelines, see [README-python.md](README-python.md).

##  Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

###  Quick Start
Run immediately via `uvx`:
```bash
uvx database-operations-mcp
```

###  Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "database-operations": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/database-operations-mcp", "run", "database-operations-mcp"]
  }
}
```
### From PyPI (Recommended)

```bash
pip install database-operations-mcp
```

### From GitHub Releases

```bash
# Direct wheel download
pip install https://github.com/sandraschi/database-operations-mcp/releases/download/v1.4.0/database_operations_mcp-1.4.0-py3-none-any.whl

# Or from git
pip install git+https://github.com/sandraschi/database-operations-mcp.git
```

### For Claude Desktop (MCPB Package)

1. Download or build the latest `.mcpb` file.
2. Open Claude Desktop  Settings  Extensions
3. Drag and drop the `.mcpb` file
4. Restart Claude Desktop

## FastMCP 3.1.0 Features

This server uses FastMCP 3.1.0 capabilities:

### Conversational Tool Returns
All tools return structured responses with natural language summaries alongside technical data.

**Example Response:**
```json
{
  "success": true,
  "operation": "list_supported",
  "message": "I found 15 supported database types across 4 categories. You can connect to SQL databases (PostgreSQL, MySQL, SQLite), NoSQL databases (MongoDB), vector databases (ChromaDB), and more.",
  "databases_by_category": {...},
  "total_supported": 15,
  "categories": ["sql", "nosql", "vector", "graph"]
}
```

### Sampling Capabilities
Supports agentic workflows where the LLM can orchestrate multi-step database operations without client round-trips.

**Example Workflow:**
```python
result = await db_sampling_workflow(
    workflow_prompt="Analyze database performance, optimize slow queries, and generate a comprehensive report",
    available_operations=["analyze_performance", "optimize_queries", "generate_report"],
    max_iterations=10
)
```

### Enhanced Error Handling
Error responses include recovery suggestions and context-aware guidance.

**Example Error Response:**
```json
{
  "success": false,
  "operation": "execute_query",
  "message": "I encountered an error while executing your query. The connection to the database might have been lost.",
  "error": "Connection timeout after 30 seconds",
  "error_code": "CONNECTION_TIMEOUT",
  "suggestions": [
    "Check if the database server is running",
    "Verify network connectivity",
    "Try reconnecting using the 'test' operation"
  ]
}
```

### Agentic Database Workflows
The `db_sampling_workflow` tool enables complex database operations that would previously require multiple round-trips:

- Query optimization: Analyzes and optimizes slow queries
- Schema migration planning: Plans and executes schema changes
- Data quality assessment: Data validation and integrity checks
- Performance analysis: Performance bottleneck detection and resolution

## Requirements
- Python 3.10+
- FastMCP 3.1.0+
- **Persistence**: `py-key-value-aio[disk]` for DiskStore (optional; in-memory fallback if not installed)
- **Database Drivers**: `chromadb`, `pymongo`, `psycopg2-binary`, `duckdb`, `aiomysql`, `redis`
- **Utilities**: `aiohttp`, `rich`, `psutil`



## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.

## Webapp Dashboard

This MCP server includes a web interface (FastMCP 3.1.0 gateway) for monitoring and tool execution.
- **Frontend**: port **10708** (Vite dev server)
- **Backend**: port **10709** (FastAPI + MCP mounted at `/mcp`, REST at `/api/tools`)

To start the webapp:
1. Navigate to the `web_sota` directory.
2. Run `.\start.ps1` (PowerShell; from repo root: `cd web_sota; .\start.ps1`).
3. Open `http://localhost:10708` in your browser.

## Prompts and skills (FastMCP 3.1.0)

- **MCP prompt `database_expert`**: Clients can call `get_prompt("database_expert", arguments={"focus": "general"|"sql"|"connections"|"export"})` to receive instruction text to inject so the LLM acts as a database expert using this server's tools. Use when you want the assistant to follow connection/schema/query/export  practices without reading this README.
- **Bundled skill `database-expert`**: Exposed as MCP resources under the `skill://` scheme. Clients that support MCP resources can read `skill://database-expert/SKILL.md` (and manifest/supporting files) for the same expert guidance. The skill lives in `src/database_operations_mcp/skills/database-expert/` and is registered via the FastMCP Skills provider.

See [FastMCP Prompts](https://goFastMCP 3.1.0com/servers/prompts) and [Skills Provider](https://goFastMCP 3.1.0com/servers/providers/skills) for the framework docs.

## Persistence

Connection state and preferences are persisted across restarts using `py-key-value-aio[disk]` (DiskStore).

- **Storage location**: `%APPDATA%\database-operations-mcp` (Windows), `~/Library/Application Support/database-operations-mcp` (macOS), `~/.local/share/database-operations-mcp` (Linux).
- **Persisted data**: Saved database connections, active connection id, user preferences (e.g. default page size), restore state, and schema cache.
- **Initialization**: Storage is initialized in server lifespan; if the optional `[disk]` extra is not installed, the server falls back to in-memory storage and logs a warning.
- **Development**: Set `ENABLE_PASSWORD_STORAGE=1` only in dev; it allows storing connection passwords (insecure, not for production).
