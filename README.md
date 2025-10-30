[![Version](https://img.shields.io/badge/version-1.4.0-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.13-orange.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
# Database Operations MCP

FastMCP 2.13 MCP server for database-centric operations on Windows, with powerful bookmark tooling as an add-on (because large bookmark collections are a kind of database).

## What this repo is
- Primary: Database tools (inspection, backup/restore, analysis, Windows app databases)
- Secondary: Bookmark tools (Firefox + Chromium family) including cross-browser sync

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

### Firefox (existing, SQLite)
- `list_bookmarks(profile_name=None, folder_id=None)`
- `add_bookmark(url, title, profile_name=None)`
- Search, tags, analysis, bulk ops (see `src/database_operations_mcp/tools/firefox/`)

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
  - If writing to Firefox while it’s open, the result will include: "error. firefox must be closed".

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

## Development (optional)
```powershell
uv run pytest -q
uv run ruff check .
uv run ruff format .
uv run mypy src/
```

## Requirements
- Python 3.10+
- FastMCP 2.13
- Supported browsers installed (for bookmark tools)

## License
MIT License - see LICENSE file.
