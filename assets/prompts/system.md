# database-operations-mcp — MCP Server Capabilities

## Server Overview

Database Operations MCP is a comprehensive FastMCP 3.3 server for database operations across 8 database types (SQLite, PostgreSQL, MySQL/MariaDB, MongoDB, ChromaDB, Redis, DuckDB, LanceDB), plus system tools, Firefox bookmark management, Calibre library integration, an activity log ring buffer, and an agentic workflow engine. It supports three transport modes (stdio, HTTP, SSE) and runs as a dual FastAPI + FastMCP server on port 10709 (backend) with a Vite React frontend on port 10708.

The server implements a portmanteau tool architecture — most database operations are consolidated into domain-specific tools with an "operation" enum discriminator. It maintains centralized connection management via a DatabaseManager singleton, exposes an in-memory ring-buffer activity log (max 50,000 entries, default 2,000) with CSV/JSON export, logging query/filter/sort/clear, and supports graceful shutdown with signal handlers.

The server exposes ~40 tools organized by domain: db_connection, db_operations, db_schema, db_management, db_fts (full-text search), db_analyzer, db_operations_extended, media_library, windows_system, calibre_integration, help_system, agentic_tools, and system_init. It also registers FastMCP 3.1+ native prompts for common workflows.

## Tools

### db_connection
**Purpose**: Manage database connections across supported types. Portmanteau with operations for registering, testing, listing, connecting, and configuring database connections.
**Parameters**:
- connection_name (str): Unique identifier for the connection.
- connection_string (str): Database connection string/URL.
- database_type (str): Type: sqlite, postgresql, mongodb, mysql, redis, duckdb, lancedb, chromadb.
**Operations**: list_supported, register, init, list, test, test_all, close, get_info, restore, set_active, get_active, get_preferences, set_preferences.

### db_operations
**Purpose**: Execute database operations (queries, writes, transactions, bulk inserts).
**Operations**: execute_transaction, execute_write, batch_insert, execute_query, quick_data_sample, export_query_results.
**Parameters**:
- connection_name (str): Target registered connection.
- query (str): SQL or query string for execute_query/execute_write.
- parameters (dict): Query parameters for parameterized queries.
- table_name (str): Table name for quick_data_sample.

### db_schema
**Purpose**: Inspect database schemas, list tables, describe columns, compute schema diffs.
**Operations**: list_databases, list_tables, describe_table, get_schema_diff.

### db_management
**Purpose**: Server-level database management tasks.
**Operations**: init_database, list_connections, close_connection, test_connection, get_connection_info, database_health_check, get_database_metrics, vacuum_database, disconnect_database.

### db_fts (Full-Text Search)
**Purpose**: Full-text search across registered databases.
**Operations**: fts_search, fts_tables, fts_suggest.

### db_analyzer
**Purpose**: Analyze database structure, content, health, and performance.
**Operations**: structure, analyze, content, health, errors, report.

### db_operations_extended
**Purpose**: Extended operations including Redis key-value, table structure, and additional query types.
**Operations**: execute_query, execute_non_query, get_tables, get_table_structure, health_check, get_keys, get_value, set_value.

### media_library
**Purpose**: Calibre library integration — search books, get metadata, search full text, optimize Plex databases.
**Operations**: search_calibre_library, get_calibre_book_metadata, search_calibre_fts, search_calibre_fts_db, find_plex_database, optimize_plex_database, export_database_schema, get_plex_library_stats, manage_plex_metadata, get_plex_library_sections.

### windows_system
**Purpose**: Windows-specific database operations including registry access and Windows database management.
**Operations**: list_windows_databases, query_windows_database, clean_windows_database, read_registry_value, write_registry_value, list_registry_keys, list_registry_values, monitor_registry, delete_registry_value, delete_registry_key, registry_key_exists.

### help_system
**Purpose**: Discover tools, get parameter info, search help, get examples.
**Operations**: help, tool_help, list_categories, search_help, get_tool_examples, get_parameter_info, format_help_output.

### agentic_workflow_tool
**Purpose**: Multi-step agentic workflow using FastMCP 3.1 sampling (ctx.sample). The LLM plans and orchestrates complex multi-tool workflows from a natural language goal.

### safety_guard_status
**Purpose**: Check whether the safety guard (MUTATING/DESTRUCTIVE tool filter) is active.

### system_init
**Purpose**: Initialize the database operations system — load saved connections, configure defaults.

## Database Types Supported

1. **SQLite**: Lightweight file-based SQL database. Connection string: file path.
2. **PostgreSQL**: Advanced open-source relational database. Connection string: postgresql://user:pass@host:port/db.
3. **MySQL/MariaDB**: Popular open-source relational database. Connection string: mysql://user:pass@host:port/db.
4. **MongoDB**: Document-oriented NoSQL database. Connection string: mongodb://host:port/db.
5. **ChromaDB**: Vector database for embeddings and AI applications. Connection string: http://host:port.
6. **Redis**: In-memory data structure store. Connection string: redis://host:port.
7. **DuckDB**: In-process analytical SQL database. Connection string: file path.
8. **LanceDB**: Embedding store and vector search. Connection string: directory path.

## Activity Log System

In-memory ring buffer (default 2,000 entries, configurable up to 50,000 via DBOPS_LOG_MAX_ENTRIES). Each entry has: id (float timestamp), timestamp (ISO 8601), level (DEBUG/INFO/WARNING/ERROR/CRITICAL), kind (category), detail (message), meta (dict). Supports querying with filters (level, kind, search text), sorting (asc/desc), pagination (limit/offset), after_id cursor, and export to JSON or CSV with filename stamp. A Python logging handler (ActivityLogHandler) captures all Python logging records into the ring buffer automatically.

## Configuration

### Environment Variables
- MCP_TRANSPORT (str, default="stdio"): Transport mode: stdio, http, sse, dual.
- MCP_HOST (str, default="127.0.0.1"): HTTP server bind address.
- MCP_PORT (int, default=10708 for MCP, 10709 for web bridge): HTTP server port.
- MCP_PATH (str, default="/mcp"): HTTP endpoint path.
- ENABLE_ATOMIC_DB_TOOLS (bool, default=true): Enable per-database-type atomic tools.
- DBOPS_LOG_MAX_ENTRIES (int, default=2000, max 50000): Activity log ring buffer capacity.

### CLI Arguments
- --stdio: Run in STDIO mode (Claude Desktop).
- --http: Run in HTTP Streamable mode.
- --sse: Run in SSE mode (deprecated).
- --dual: Run both stdio and HTTP concurrently.
- --port: Override port.
- --host: Override bind address.
- --debug: Enable debug logging.

## REST API Endpoints

- GET /health: Server health status.
- GET /api/capabilities: Full capability matrix (tools, prompts, resources, skills, sampling).
- GET /api/tools: List all registered MCP tools with schemas.
- POST /api/tools/call: Call an MCP tool by name with arguments.
- GET /api/activity: Activity feed (recent events).
- DELETE /api/activity: Clear activity log.
- GET /api/logs: Query logs with filters.
- GET /api/logs/stats: Log statistics.
- GET /api/logs/export: Export logs as JSON or CSV.
- DELETE /api/logs: Clear logs.

## Prompts (FastMCP 3.1 Native)
- **database_expert**: Guides the model through best practices for database queries.
- **schema_inspector**: "Show me the schema, tables, columns, and indexes for a database."
- **performance_tuning**: "Analyze queries for performance improvements."
- **data_export**: "Export query results to CSV."

## Integration Points
- **Claude Desktop / Cursor**: STDIO transport for direct tool access.
- **Web Dashboard**: Vite React frontend on port 10708.
- **Fleet docsops**: Cross-reference mcp-central-docs for standards.
- **Calibre**: Library database integration for book metadata.
- **Firefox**: Browser bookmark database access (places.sqlite).

## Error Handling
All portmanteau tools return structured dicts with success bool. On failure: error string, error_type (fatal/retryable/user_fixable/invalid_input), recovery_options list, retryable bool. Standard helper functions: mcp_error(), unknown_operation_response(), connection_not_found().

## Database Connector Architecture
Each database type is implemented as a connector class extending BaseDatabaseConnector[T] with an abstract interface:

1. **connect() -> bool**: Establishes the connection using the provided config. Connection pooling is handled at the connector level.
2. **disconnect() -> bool**: Gracefully closes the connection and releases resources.
3. **execute_query(query, parameters, **kwargs) -> QueryResult**: Executes a query and returns structured results with success, data (list of dicts), columns, rowcount, message, execution_time, and timestamp.
4. **get_schema(**kwargs) -> dict**: Returns the database schema structure.
5. **get_tables(**kwargs) -> list[str]**: Returns available table names.
6. **get_table_schema(table_name, **kwargs) -> dict**: Returns column-level schema for a specific table.
7. **health_check() -> dict**: Performs a connectivity and performance health check.

Connectors are registered with the DatabaseManager singleton via register_connector(name, connector). The manager maintains a dictionary of named connectors with status tracking (DISCONNECTED, CONNECTING, CONNECTED, ERROR). The create_connector() factory function looks up connector classes from AVAILABLE_CONNECTORS by database_type string and instantiates with the provided config.

## Activity Log Architecture
The in-memory activity log is implemented as a thread-safe deque with configurable maxlen (2,000 default, 50,000 max via DBOPS_LOG_MAX_ENTRIES). Each entry has:

1. **id**: Float timestamp based on time.time() with microsecond precision, used for cursor-based pagination.
2. **timestamp**: ISO 8601 UTC string for human-readable sorting.
3. **level**: One of DEBUG, INFO, WARNING, ERROR, CRITICAL with rank-based filtering (e.g., querying WARNING returns WARNING+ERROR+CRITICAL).
4. **kind**: Category string (system, tool_call, server) for filtering by event type.
5. **detail**: Human-readable message describing the event.
6. **meta**: Optional dict for structured metadata (tool names, arguments, HTTP status codes).

The query interface supports: level filtering (rank-based), kind filtering (exact match), search filtering (substring match across kind+detail+meta JSON), sorting (asc/desc by timestamp), pagination (limit/offset), and cursor-based pagination (after_id). The export interface supports JSON and CSV formats with Content-Disposition headers for file download. The ActivityLogHandler Python logging handler automatically captures all Python logging records into the ring buffer, ensuring that server-internal events are also tracked.

## Tool Surface Architecture
The server distinguishes between portmanteau tools and atomic tools for the web dashboard capability browser:

- **Portmanteau tools** (12 tools): db_connection, db_operations, db_schema, db_management, db_analyzer, db_fts, db_operations_extended, help_system, media_library, windows_system, calibre_integration, system_init. Each uses the operation enum pattern.
- **Atomic tools** (30+ tools): Individual tools like health, _shutdown, activity_feed, logs_query, logs_stats, logs_export, logs_clear, agentic_workflow_tool, safety_guard_status, calibre_list_books, calibre_get_book_details, calibre_query, postgresql, plus per-database-type atomic tools when ENABLE_ATOMIC_DB_TOOLS is true.

The capability endpoint (/api/capabilities) returns the full tool surface breakdown with counts, prompt names, resource URIs, skill URIs, sampling availability, and agentic workflow tool names.

## Transport Configuration
The server supports three transport modes with automatic detection:

1. **STDIO (default)**: JSON-RPC over stdin/stdout. Used by Claude Desktop, Cursor, and CLI-based MCP clients. Invoked with `--stdio` or default.
2. **HTTP Streamable**: FastMCP 2.14.4+ HTTP transport at configurable host:port/path. Invoked with `--http --port 10708 --path /mcp`.
3. **SSE (deprecated)**: Legacy Server-Sent Events transport. Invoked with `--sse`. Use HTTP instead.

Dual mode runs both stdio and HTTP concurrently using asyncio.gather for maximum compatibility. The transport is detected in priority order: CLI arguments, then MCP_TRANSPORT env var, then default (stdio for CLI, http for web_sota).

## Deployment Topology
The server can be deployed in several configurations:
- **Standalone stdio**: Single process for Claude Desktop. No network binding needed.
- **HTTP bridge + web_sota frontend**: The HTTP bridge (main.py with --http) serves REST API on port 10709 and mounts MCP at /mcp. The Vite React frontend runs on port 10708 and proxies /api calls to the backend.
- **Full stack with web dashboard**: Both services running, providing the complete admin interface with activity log, capabilities browser, and tool testing console.
- **Containerized**: Both services can be containerized with Docker for consistent deployment across environments. The web_sota/frontend serves static files through the backend in production mode.

## Connector Implementation Details
Each database connector must implement seven abstract methods from BaseDatabaseConnector. The connect() method should handle authentication, connection pooling configuration, and initial handshake. The disconnect() method should gracefully close all pooled connections and release resources. The execute_query() method should support parameterized queries via the parameters dict, handle type conversion between Python types and database types, and return results as a list of dicts with column names as keys. The get_schema() method should return database-level schema information including tables, views, indexes, and foreign keys. The get_tables() method should return table names with optional schema filtering. The get_table_schema() method should return column-level information (name, type, nullable, default, primary key, foreign key). The health_check() method should verify connectivity, check server version, and measure query latency. Connectors should handle network timeouts, authentication failures, and query errors gracefully, transitioning to ERROR status when appropriate. Each connector is responsible for its own connection pooling configuration — see individual connector source files for defaults.

## Agentic Workflow Architecture
The agentic_workflow_tool uses FastMCP 3.1 sampling (ctx.sample) to enable autonomous multi-step database operations. The tool receives a natural language goal and uses the connected MCP client's LLM to plan and execute a sequence of tool calls. The agentic workflow is useful for: complex data analysis tasks that require multiple queries, cross-database data migration with schema inspection and transformation, database health assessment with comprehensive diagnostics, schema documentation generation from table structures, and automated data cleanup with verification steps. The agentic workflow requires a sampling-capable MCP client (Claude Desktop, Cursor with sampling support). If sampling is not available, the tool returns a clear error message. The agentic tools are identified by "agentic" or "assist" in their names in the capabilities endpoint, enabling UI discovery.

## Transport Configuration Examples
The server supports multiple transport configurations for different deployment scenarios. For Claude Desktop integration, use stdio mode: just run the server without arguments and configure Claude Desktop's MCP server settings with the command and args. For web dashboard integration with HTTP transport: MCP_TRANSPORT=http MCP_PORT=10709 MCP_HOST=127.0.0.1 uv run python -m database_operations_mcp.main. For dual transport (stdio + HTTP simultaneously): use --dual flag or set MCP_TRANSPORT=dual. For SSE transport (legacy, not recommended): MCP_TRANSPORT=sse uv run python -m database_operations_mcp.main. The HTTP transport serves the MCP surface at /mcp by default (configurable via MCP_PATH). The web_sota FastAPI bridge listens on port 10709 and mounts both the REST API and the MCP HTTP transport. The Vite frontend dev server on port 10708 proxies API calls to the backend. For production, serve the frontend as static files from the backend.

## Quick Reference
Summary of all available database types and their connection string formats: SQLite (file path), PostgreSQL (postgresql://user:pass@host:port/db), MySQL (mysql://user:pass@host:port/db), MongoDB (mongodb://host:port/db), Redis (redis://host:port/db), DuckDB (file path or :memory:), ChromaDB (http://host:port), LanceDB (directory path). Default MCP transport is stdio for Claude Desktop. Default web bridge port is 10709. Default log buffer size is 2000 entries. All portmanteau tools use the operation enum parameter pattern.

## Environment Variable Summary
Quick reference for all configuration variables: MCP_TRANSPORT (stdio|http|sse|dual, default stdio), MCP_HOST (bind address, default 127.0.0.1), MCP_PORT (HTTP port, default 10708), MCP_PATH (HTTP endpoint path, default /mcp), ENABLE_ATOMIC_DB_TOOLS (true|false, default true), DBOPS_LOG_MAX_ENTRIES (100-50000, default 2000). All variables are optional with sensible defaults. Configuration is read at startup — changes require a restart.

## Uninstallation and Cleanup
To remove the server, delete the repository directory. The server creates no system-wide files. The activity log and connection configuration are in-memory and lost on shutdown. No persistent data is created outside the repository.

## Known Limitations
The database-operations-mcp server has some known limitations. Connection strings containing credentials are stored in memory only — they are not persisted across restarts unless explicitly saved. The restore_saved_database_connections mechanism stores connection configs but not passwords — credentials must be re-entered after restart. Very large result sets (>100,000 rows) may cause memory pressure — use LIMIT/OFFSET pagination or export to CSV/JSON for large datasets. The activity log ring buffer has a configurable capacity (default 2,000, max 50,000) — old entries are automatically evicted when the buffer is full. Not all database connectors support all operations — for example, Redis does not support schema inspection or full-text search. Some database operations require specific client libraries that may not be installed — the connector will report missing dependencies on connection attempt. The agentic workflow tool requires a sampling-capable MCP client.

## Web Dashboard Integration
The web_sota backend (port 10709) builds a FastAPI application that wraps the MCP tools with REST endpoints and adds a capability discovery API. The build_web_app function imports all tools, configures CORS, sets up the web router with /api/health, /api/capabilities, /api/tools, /api/tools/call, /api/activity, /api/logs endpoints, and installs the logging handler. The web router calls the MCP app's list_tools and call_tool methods to bridge REST calls to MCP tools. The /api/capabilities endpoint returns the full capability matrix for dynamic UI generation. The /api/tools endpoint lists all tools with their input schemas. The /api/tools/call endpoint invokes a tool by name with arguments and returns the result. The web_sota frontend (port 10708) is a Vite React app that consumes these REST endpoints.

## Prompt Templates Reference
The server registers FastMCP 3.1+ native prompts for common database workflows. The database_expert prompt provides query optimization tips, schema design patterns, and best practices for the selected database type. The schema_inspector prompt guides the user through listing tables, columns, indexes, and foreign keys for a connection. The performance_tuning prompt helps analyze slow queries and suggests indexes, query rewrites, and configuration changes. The data_export prompt generates a data export workflow with format selection (CSV or JSON), column filtering, and row limiting. These prompts are registered in the prompts module and loaded during server initialization. They are available via the MCP prompts/list and prompts/get protocol methods. Prompts are designed to be injected as system messages in the conversation context, providing structured guidance for common tasks.

## Database Management Operations
The db_management tool provides server-level database administration operations. The init_database operation creates a new database or initializes an existing connection. The list_connections operation returns all registered connections with their status, type, and error information. The close_connection operation gracefully shuts down a connection and releases resources. The test_connection operation performs a connectivity test against the database server. The get_connection_info operation returns the connection configuration including type, host, port, and database name. The database_health_check operation returns comprehensive health metrics: uptime, active connections, database size, cache hit ratio, query throughput, and replication lag. The get_database_metrics operation returns detailed performance metrics: query execution time percentiles, index usage statistics, table size rankings, and vacuum/analyze recommendations. The vacuum_database operation reclaims storage space and updates query statistics. The disconnect_database operation force-disconnects without graceful shutdown.

## Capability Discovery
The /api/capabilities endpoint provides a complete inventory of the server's capabilities for dynamic UI generation. The response includes: tool_surface with total tool count, portmanteau count, atomic count, and lists of each, prompts section with availability flag, count, and names, resources section with URIs (limit 50), skills section with URIs (limit 50), sampling section with availability flag and indicator tools, and agentic_workflows section with tools list. The capability endpoint is used by the web_sota dashboard to dynamically render the tools hub page with portmanteau-aware drill-downs and tool documentation. It also enables MCP clients to discover available features without static configuration. The endpoint response is cached for 30 seconds to reduce overhead on frequent requests.

## Activity Log Integration
The activity log is automatically populated by both the Python logging handler and explicit log_activity() calls in REST API endpoints. The ActivityLogHandler captures all log records at INFO level and above from the Python logging system, routing them to the ring buffer with kind="server" and the logger name in meta. Explicit log_activity() calls are used for business events: tool calls (kind="tool_call" with tool name and arguments in meta), system events (kind="system" for startup, shutdown, configuration changes), and errors (kind="error" for connection failures, query errors). The log is thread-safe using a Lock. Querying and exporting are non-destructive — entries remain in the buffer after reading. Clearing the log resets the buffer completely. The max_entries is configurable via DBOPS_LOG_MAX_ENTRIES environment variable and cannot exceed 50,000 to prevent memory exhaustion. The ring buffer automatically evicts the oldest entries when the capacity is reached.

## Development and Testing
The database-operations-mcp server is developed following fleet SOTA standards. The codebase is organized as a standard Python package under src/database_operations_mcp/ with tools/ subdirectory for portmanteau tools, services/ for database connectors, and config/ for configuration. To add support for a new database type, create a new connector class extending BaseDatabaseConnector in services/database/connectors/, implement all abstract methods, register it in AVAILABLE_CONNECTORS, and add the type to the DatabaseType enum. To add a new tool, create a new module in tools/ with @mcp.tool() decorated functions and import it in _import_all_tools(). Tests use pytest with async support and are located in tests/. Run `uv run pytest` for the full test suite. The justfile provides recipes for serve, test, lint, and mcpb-pack. The project uses ruff for linting and formatting with fleet-standard configuration. Type checking with mypy is recommended for new connector implementations. The package is distributed as a uv-managed project with pyproject.toml and committed uv.lock.

## Web Dashboard SOTA Integration
The web_sota frontend (port 10708) is a Vite React application following the fleet SOTA WebApp standards. It uses the Slate/Amber dark theme with Tailwind CSS, Framer Motion animations, Lucide React icons, and Zustand state management. The dashboard includes: a sidebar with navigation to Dashboard, Tools, Logs, and API Docs pages, a topbar with connection status and dark mode toggle, a tools hub page that dynamically discovers all registered MCP tools with their input schemas, a logs page with filtering and export to CSV/JSON, an API docs page embedding Swagger UI and ReDoc, and a status page with the activity log and server health. The frontend proxies /api calls to the backend on port 10709 via Vite's proxy configuration. The backend CORS middleware allows cross-origin requests from the frontend dev server.

## Use Cases and Applications
The database-operations-mcp server is designed for: database administrators managing multiple database types through a unified interface, developers who need to query databases during development without switching between multiple database clients, data analysts extracting and exporting data for reporting, MCP-powered automated database maintenance and optimization, Calibre library management and full-text search, Plex database optimization and statistics, Firefox bookmark access and management, Redux cache inspection and manipulation, and cross-database data migration workflows. The server replaces the need for multiple specialized database clients (pgAdmin, SQLite Browser, MongoDB Compass, RedisInsight) with a single MCP interface accessible from any MCP-compatible client.

## Security Considerations
The server stores database connection strings in memory during the session. Connection strings may contain credentials (passwords, API keys). These are not persisted to disk unless explicitly saved via restore_saved_database_connections. The HTTP API does not implement authentication — use in trusted networks only. The CORS middleware allows all origins by default — restrict in production deployments. SQL injection is prevented by using parameterized queries via the parameters dict in execute_query calls. The safety_guard tool provides visibility into MUTATING/DESTRUCTIVE tool filtering. The activity log captures all tool calls with parameters for auditability. For production deployments, run behind a reverse proxy with TLS and authentication.

## Prompts Reference
The server registers FastMCP 3.1+ native prompts for common database workflows:

1. **database_expert**: Guides the model through best practices for specific database types. Provides query optimization tips, schema design patterns, and performance considerations.
2. **schema_inspector**: Creates a prompt that lists tables, columns, indexes, and foreign keys for a selected connection.
3. **performance_tuning**: Analyzes slow queries and suggests indexes, query rewrites, and configuration changes.
4. **data_export**: Generates a data export workflow with format selection (CSV, JSON), column filtering, and row limiting.
