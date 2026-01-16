[![Version](https://img.shields.io/badge/version-1.4.0-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.14.3-orange.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
# Database Operations MCP

FastMCP 2.14.3 MCP server for database operations on Windows, with bookmark management tools.

## Scope
- Primary: Database tools (inspection, backup/restore, analysis, Windows application databases)
- Secondary: Bookmark tools (Firefox + Chromium browsers) including cross-browser synchronization

## Tools Overview

This server provides 24 portmanteau tools consolidating 124+ individual operations into unified interfaces.
Individual tools have been deprecated in favor of portmanteau tools for maintainability and consistency.

### Database Tools (Primary)
- `db_connection` - Database connection management portmanteau (consolidates connection_tools, init_tools)
  - Operations: list_supported, register, init, list, test, test_all, close, get_info, restore, set_active, get_active, get_preferences, set_preferences
- `db_operations` - Query execution, transactions, batch operations, data export portmanteau (consolidates query_tools, data_tools)
  - Operations: execute_query, execute_transaction, execute_write, batch_insert, quick_data_sample, export_query_results
- `db_schema` - Schema inspection, table/column/index analysis portmanteau (consolidates schema_tools)
  - Operations: list_databases, list_tables, describe_table, get_schema_diff
- `db_management` - Database health checks, optimization, backup/restore portmanteau (consolidates management_tools)
- `db_fts` - Full-text search with ranking and highlighting portmanteau (consolidates fts_tools)
- `db_analyzer` - Comprehensive database analysis and diagnostics portmanteau
- `db_sampling_workflow` - FastMCP 2.14.3 sampling-enabled agentic workflows for complex database operations
- `windows_system` - Windows Registry, service status, system info portmanteau (consolidates registry_tools, windows_tools)

### Bookmark Tools (Secondary)
- `browser_bookmarks` - Universal browser bookmark portmanteau (Firefox/Chrome/Edge/Brave)
  - Operations: list_bookmarks, add_bookmark, edit_bookmark, delete_bookmark, search_bookmarks, get_bookmark, and 20+ more
  - Supports all browsers through single interface
- `firefox_bookmarks` - Firefox-specific bookmark operations (SQLite-based)
  - Operations: list_bookmarks, add_bookmark, search, find_duplicates, find_old_bookmarks, find_forgotten_bookmarks, refresh_bookmarks, get_bookmark_stats, find_broken_links
  - Tag management: list_tags, find_similar_tags, batch_update_tags, merge_tags, clean_up_tags
  - **Note:** Write operations require Firefox to be closed (SQLite lock)
- `firefox_profiles` - Firefox profile management portmanteau
- `firefox_backup` - Firefox backup/restore operations
- `firefox_tagging` - Automated tagging (by folder, by year)
- `sync_bookmarks` - Cross-browser bookmark synchronization (Firefox ↔ Chromium family)
- `chrome_profiles` - Chrome profile management portmanteau

### Media & Other Tools
- `media_library` - Calibre & Plex library management portmanteau (consolidates calibre_tools, plex_tools, media_tools)
- `help_system` - Interactive help and documentation portmanteau (consolidates help_tools)
- `system_init` - System initialization and setup portmanteau

### Deprecated Tools (Use Portmanteau Equivalents)
Individual tools are deprecated but kept for backwards compatibility. Migration paths:
- `connection_tools.*` → `db_connection(operation='...')`
- `init_tools.*` → `db_connection(operation='...')`
- `query_tools.*` → `db_operations(operation='...')`
- `data_tools.*` → `db_operations(operation='...')`
- `schema_tools.*` → `db_schema(operation='...')`
- `management_tools.*` → `db_management(operation='...')`
- `fts_tools.*` → `db_fts(operation='...')`
- `calibre_tools.*` → `media_library(operation='...')`
- `plex_tools.*` → `media_library(operation='...')`
- `registry_tools.*` → `windows_system(operation='...')`
- `windows_tools.*` → `windows_system(operation='...')`

*See individual tool files in `src/database_operations_mcp/tools/` for complete API documentation.*

## Core Database Features (Primary)
- SQLite utilities: open/read, schema introspection, queries, export
- Backup and restore helpers for common Windows application databases
- Windows paths helpers (Chrome/Edge/Brave/Firefox history, Outlook, etc.)
- Safety helpers (file locks, status checks) with clear error messages
- MCP tools organized under `src/database_operations_mcp/tools/`

### Representative Tools
- Windows DB helpers: `windows_tools.py`
- Firefox DB safety/status: `tools/firefox/status.py`
- Backup/maintenance helpers across known app DBs

## Bookmark Tools (Secondary)
Cross-browser bookmark utilities packaged with this server.

### Firefox Bookmarks (SQLite-based)

**Important:** Write operations require Firefox to be closed (SQLite database lock).
Read operations work while Firefox is running using `force_access=True`.

#### Core Operations
```python
# List bookmarks
await firefox_bookmarks(operation="list_bookmarks", profile_name="default")

# Add bookmark (Firefox must be closed!)
await firefox_bookmarks(operation="add_bookmark", url="https://example.com", title="Example")

# Search bookmarks
await firefox_bookmarks(operation="search", search_query="python")
```

#### Bookmark Age Analysis
```python
# Find OLD bookmarks (by CREATION date) - e.g. bookmarks from 2005
await firefox_bookmarks(operation="find_old_bookmarks", age_days=7000)
# Returns: bookmarks with age_years, age_days, created timestamp

# Find FORGOTTEN bookmarks (not VISITED in N days) - archive candidates
await firefox_bookmarks(operation="find_forgotten_bookmarks", age_days=365)
# Returns: suggestion to archive/delete these unused bookmarks

# Refresh bookmarks - check for 404s, attempt URL fixes
await firefox_bookmarks(operation="refresh_bookmarks", batch_size=100)
# Returns: working/broken counts, fixable URLs with simplified alternatives
```

#### Tag Management
```python
await firefox_bookmarks(operation="list_tags")
await firefox_bookmarks(operation="find_similar_tags")  # Find typos like "pythn" vs "python"
await firefox_bookmarks(operation="merge_tags", tags=["python", "pythn"])  # Requires Firefox closed
```

#### Statistics & Maintenance
```python
await firefox_bookmarks(operation="get_bookmark_stats")
await firefox_bookmarks(operation="find_duplicates")
await firefox_bookmarks(operation="find_broken_links")
```

### Chrome / Edge / Brave (JSON)
- `list_chrome_bookmarks(bookmarks_path=None)`
- `list_edge_bookmarks(bookmarks_path=None)`

### Chromium Portmanteau (Chrome/Edge/Brave)
- `chromium_bookmarks(operation, browser, ...)` unified tool
  - **list**: `operation="list"`, `browser="chrome|edge|brave"`, `limit?`, `bookmarks_path?`
  - **add**: `operation="add"`, `title`, `url`, `folder?`, `allow_duplicates?`, `bookmarks_path?`
  - **edit**: `operation="edit"`, `id?` or `url?`, `new_title?`, `new_folder?`, `create_folders?`, `allow_duplicates?`, `dry_run?`, `bookmarks_path?`
  - **delete**: `operation="delete"`, `id?` or `url?`, `dry_run?`, `bookmarks_path?`

```python
# List first 50 Edge bookmarks via portmanteau
await chromium_bookmarks(operation="list", browser="edge", limit=50)

# Add to Brave in folder "Reading/Tech"
await chromium_bookmarks(operation="add", browser="brave", title="Docs", url="https://example.com/docs", folder="Reading/Tech")

# Rename and move a Chrome bookmark by URL (dry run)
await chromium_bookmarks(operation="edit", browser="chrome", url="https://example.com/docs", new_title="Docs Home", new_folder="Reading/Docs", dry_run=True)

# Delete by id in Edge
await chromium_bookmarks(operation="delete", browser="edge", id="12345")
```
- `list_brave_bookmarks(bookmarks_path=None)`
- `add_chrome_bookmark(title, url, folder=None, bookmarks_path=None)`
- `add_edge_bookmark(title, url, folder=None, bookmarks_path=None)`
- `add_brave_bookmark(title, url, folder=None, bookmarks_path=None)`

### Cross-Browser Sync
- `sync_bookmarks(source_browser, target_browser, dry_run=True, limit=1000)`
  - Set `dry_run=False` to write to target.
  - If writing to Firefox while it's open, the result will include: "error. firefox must be closed".

### Examples
```python
# List Chrome bookmarks
await list_chrome_bookmarks()

# Add to Edge
await add_edge_bookmark(title="Example", url="https://example.com")

# Sync from Firefox to Chrome (write)
await sync_bookmarks("firefox", "chrome", dry_run=False, limit=100)
```

## Project Layout
```
database-operations-mcp/
├── src/
│   └── database_operations_mcp/
│       ├── main.py                      # MCP server entry
│       ├── config/
│       │   └── mcp_config.py            # shared MCP instance
│       └── tools/
│           ├── firefox/                 # Firefox bookmark + DB helpers
│           ├── chrome/                  # Chrome bookmark tools
│           ├── edge/                    # Edge bookmark tools
│           ├── brave/                   # Brave bookmark tools
│           ├── chromium_common.py       # Shared Chromium JSON helpers
│           └── sync_tools.py            # Cross-browser sync tool
├── tests/
└── README.md
```

## Install via MCPB Package (Claude Desktop)
- Download or build the `.mcpb` package.
- In Claude Desktop, open Extensions and drag-and-drop the `.mcpb` file.
- Restart Claude Desktop if prompted.

## Install Zed Extension
This repository includes a Zed extension for native integration with the Zed editor.

### Build the Extension
```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Build the Zed extension
cd zed-extension
cargo build --release --target wasm32-wasip1
```

### Install in Zed
1. Open Zed
2. Go to `Extensions` → `Install Dev Extension`
3. Select the `zed-extension/extension.json` file from the repository root
4. The extension will be loaded and available for use

**Alternative:** If Zed doesn't recognize the extension.json, you can also select the built WASM file directly at `zed-extension/target/wasm32-wasip1/release/database_operations_mcp_zed_extension.wasm`

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

## Installation

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

1. Download the latest `.mcpb` file from [Releases](https://github.com/sandraschi/database-operations-mcp/releases)
2. Open Claude Desktop → Settings → Extensions
3. Drag and drop the `.mcpb` file
4. Restart Claude Desktop

## FastMCP 2.14.3 Features

This server uses FastMCP 2.14.3 capabilities:

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
- FastMCP 2.14.3
- Supported browsers installed (for bookmark tools)

## License
MIT License - see LICENSE file.
