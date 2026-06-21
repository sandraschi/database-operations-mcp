# database-operations-mcp — User Guide

## Quick Start

### Installation
1. Clone: `git clone https://github.com/sandraschi/database-operations-mcp.git`
2. Create virtual env: `uv venv`
3. Activate: `.venv\Scripts\activate`
4. Install: `uv sync`
5. Start stdio (Claude Desktop): `uv run database-operations-mcp`
6. Start HTTP: `uv run database-operations-mcp --http --port 10709`

### First Use
1. List supported databases: `db_connection(operation="list_supported")`
2. Register a SQLite database: `db_connection(operation="register", connection_name="mydb", connection_string="C:/data/test.db", database_type="sqlite")`
3. Test connection: `db_connection(operation="test", connection_name="mydb")`
4. Query a table: `db_operations(operation="execute_query", connection_name="mydb", query="SELECT * FROM users LIMIT 5")`

## Tutorials

### Tutorial 1: List Supported Database Types
Call `db_connection(operation="list_supported")` to see all 8 supported database types with their descriptions, categories (SQL Server, NoSQL, Vector, File-based, Analytical), and type identifiers.

### Tutorial 2: Register a SQLite Connection
Call `db_connection(operation="register", connection_name="inventory", connection_string="C:/data/inventory.db", database_type="sqlite")` to register a file-based SQLite database. The server validates the path and stores the config for the session.

### Tutorial 3: Register a PostgreSQL Connection
Call `db_connection(operation="register", connection_name="prod_db", connection_string="postgresql://admin:secret@localhost:5432/mydb", database_type="postgresql")` to connect to a PostgreSQL server. Connection strings follow standard URI format.

### Tutorial 4: Initialize a Connection
After registering, call `db_connection(operation="init", connection_name="inventory")` to establish the connection. This opens the database and prepares it for queries.

### Tutorial 5: List All Active Connections
Call `db_connection(operation="list")` to see all registered connections, their status (connected/disconnected/error), database type, and any error messages.

### Tutorial 6: Test a Single Connection
Call `db_connection(operation="test", connection_name="inventory")` to run a quick health check against the specified connection. Returns success, latency, and server version info.

### Tutorial 7: Test All Connections
Call `db_connection(operation="test_all")` to test every registered connection in parallel. Returns a per-connection status report with success, type, and error details.

### Tutorial 8: Execute a SELECT Query
Call `db_operations(operation="execute_query", connection_name="inventory", query="SELECT id, name, price FROM products WHERE category = 'electronics' LIMIT 20")`. Returns rows with column names, row count, and execution time in milliseconds.

### Tutorial 9: Execute a Write Operation
Call `db_operations(operation="execute_write", connection_name="inventory", query="INSERT INTO products (name, price) VALUES ('Widget', 9.99)")`. Returns affected row count and execution time.

### Tutorial 10: Batch Insert Records
Call `db_operations(operation="batch_insert", connection_name="inventory", table_name="products", records=[{"name": "A", "price": 10}, {"name": "B", "price": 20}])`. Efficiently inserts multiple rows in a single transaction.

### Tutorial 11: Execute a Transaction
Call `db_operations(operation="execute_transaction", connection_name="inventory", statements=["UPDATE accounts SET balance = balance - 100 WHERE id = 1", "UPDATE accounts SET balance = balance + 100 WHERE id = 2"])`. Both statements succeed or both roll back atomically.

### Tutorial 12: Quick Data Sample
Call `db_operations(operation="quick_data_sample", connection_name="inventory", table_name="orders")` to get the first 10 rows from a table with column types for quick inspection.

### Tutorial 13: Export Query Results
Call `db_operations(operation="export_query_results", connection_name="inventory", query="SELECT * FROM sales WHERE date > '2026-01-01'", format="csv")` to export results as CSV or JSON.

### Tutorial 14: List Database Schemas
Call `db_schema(operation="list_databases", connection_name="postgres_prod")` to list all databases on the server.

### Tutorial 15: List Tables in a Database
Call `db_schema(operation="list_tables", connection_name="inventory")` to list all tables with row counts and table types.

### Tutorial 16: Describe a Table Schema
Call `db_schema(operation="describe_table", connection_name="inventory", table_name="products")` to see column names, types, nullability, defaults, and primary key info.

### Tutorial 17: Schema Diff Between Databases
Call `db_schema(operation="get_schema_diff", connection_name="staging", params={"target": "production"})` to compare schemas and identify differences.

### Tutorial 18: Database Health Check
Call `db_management(operation="database_health_check", connection_name="prod_db")` to check server uptime, active connections, database size, and cache hit ratio.

### Tutorial 19: Full-Text Search
Call `db_fts(operation="fts_search", connection_name="inventory", query="widget")` to search indexed text columns using FTS5.

### Tutorial 20: Database Analysis
Call `db_analyzer(operation="structure", connection_name="inventory")` to get a comprehensive structural analysis of the database.

### Tutorial 21: Query the Activity Log
Call `logs_query(level="ERROR", search="connection failed")` to find error events. Use `limit=100`, `after_id="..."` for pagination.

### Tutorial 22: Export Logs as CSV
Call `logs_export(format="csv", level="WARNING")` to download all WARNING+ level events as a timestamped CSV file.

### Tutorial 23: Clear the Log Buffer
Call `logs_clear()` to reset the activity log.

### Tutorial 24: Get System Capabilities
Call `api_capabilities()` to see the full tool surface (portmanteau count, atomic count), prompt count, resource URIs, skill URIs, sampling availability, and agentic workflow tools.

### Tutorial 25: Agentic Workflow
Call `agentic_workflow_tool(goal="Find all products with low stock and export the results as CSV", ctx=...)` for multi-step operations using LLM sampling.

## REST API Reference

### Health
GET /health → {"status": "ok", "server": "database-operations-mcp"}

### Capabilities
GET /api/capabilities → Full capability matrix with tool counts, prompts, resources, skills, and sampling info.

### List Tools
GET /api/tools → Array of all registered MCP tools with name, description, and inputSchema.

### Call Tool
POST /api/tools/call with body {"name": "db_operations", "arguments": {"operation": "execute_query", "connection_name": "test", "query": "SELECT 1"}} → {"result": ..., "isError": false}

### Activity
GET /api/activity?limit=50 → Array of recent activity log entries.

### Query Logs
GET /api/logs?level=ERROR&search=timeout&limit=100&sort=desc → Filtered, paginated log entries.

### Log Stats
GET /api/logs/stats → Total entries, breakdown by level and kind, oldest/newest timestamps.

### Export Logs
GET /api/logs/export?format=csv&level=WARNING → CSV or JSON download with Content-Disposition header.

### Clear Logs
DELETE /api/logs → Clears the ring buffer.

## Troubleshooting

### Connection fails
Verify connection string format, database is running, and network access. Call test_connection for diagnostics.

### Query returns empty
Check table name spelling, schema visibility (schemas other than public in PostgreSQL), and database selection.

### Activity log seems small
Default max is 2,000 entries. Set DBOPS_LOG_MAX_ENTRIES=50000 for larger buffer.

### Server won't start
Check MCP_PORT is free. Clear zombie processes: `Get-NetTCPConnection -LocalPort 10709 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }`.

## Advanced Workflows

### Workflow: Cross-Database Data Migration
Register connections to both source and target databases. Use db_schema(operation="list_tables") on the source to identify tables. Export each table with db_operations(operation="export_query_results", format="csv"). Transform data as needed, then batch insert into the target with db_operations(operation="batch_insert"). Use transactions for atomicity when migrating related tables. Monitor progress with the activity log. This workflow supports migrating between any supported database types (e.g., SQLite to PostgreSQL, MongoDB to DuckDB).

### Workflow: Database Performance Audit
Register a connection to the target database. Run db_management(operation="database_health_check") for overall health. Use db_analyzer(operation="structure") to understand the schema. Run db_analyzer(operation="health") for specific performance metrics. Check slow queries via logs_query(level="WARNING", search="query"). Export the performance report with logs_export(format="csv", level="WARNING"). Take corrective action: add indexes, rewrite queries, vacuum the database.

### Workflow: Multi-Source Data Consolidation
Register connections to multiple source databases (e.g., PostgreSQL production, SQLite local cache, MongoDB analytics). Use db_schema(operation="list_tables") on each to understand available data. Execute queries against each source with db_operations(operation="execute_query"). Consolidate results in code or by inserting into a target DuckDB database for analysis. Export the consolidated results with export_query_results. The activity log tracks all queries for auditability.

### Workflow: Scheduled Database Maintenance
Set up a recurring maintenance routine. First, run db_management(operation="database_health_check") to assess current state. Run db_management(operation="get_database_metrics") for detailed metrics. If fragmentation is high, run db_management(operation="vacuum_database"). Check for errors with logs_query(level="ERROR"). Export a maintenance report. Schedule this workflow via the Windows Task Scheduler or cron, calling the REST API endpoint for each operation.

### Workflow: Calibre Library Analysis
Use media_library(operation="search_calibre_library", query="sci-fi") to find books in your Calibre library. Get detailed metadata with media_library(operation="get_calibre_book_metadata", book_id=123). Search inside books with media_library(operation="search_calibre_fts", query="time travel"). Export the library schema with media_library(operation="export_database_schema"). This workflow helps analyze and explore your personal ebook collection through the database lens.

### Workflow: Plex Database Optimization
Find the Plex database with media_library(operation="find_plex_database"). Check statistics with media_library(operation="get_plex_library_stats"). Optimize the database with media_library(operation="optimize_plex_database"). Monitor the Plex library sections with media_library(operation="get_plex_library_sections"). This keeps your Plex Media Server database healthy and responsive.

### Workflow: Redis Cache Management
Register your Redis connection: db_connection(operation="register", connection_name="cache", connection_string="redis://localhost:6379/0", database_type="redis"). List keys with db_operations_extended(operation="get_keys", connection_name="cache", pattern="session:*"). Inspect values with db_operations_extended(operation="get_value", connection_name="cache", key="session:abc123"). Use set_value for cache updates. Health check with db_operations_extended(operation="health_check", connection_name="cache").

### Workflow: Agentic Multi-Step Operations
Use agentic_workflow_tool for complex multi-step tasks. Example: "Connect to the PostgreSQL production database, list all tables, describe the orders table schema, find its foreign key relationships, and export the schema documentation as JSON." The agentic workflow uses FastMCP sampling to autonomously plan and execute the sequence of tool calls, handling intermediate results and error recovery.

## Database-Specific Query Syntax
Each database type has unique query syntax considerations. For SQLite, use LIMIT/OFFSET for pagination, LIKE for pattern matching with % wildcards, and datetime() for date functions. SQLite uses dynamic typing — values are stored with the type affinity of the column but any value type can be inserted into any column. For PostgreSQL, use LIMIT/OFFSET for pagination, ILIKE for case-insensitive pattern matching, NOW() for current timestamp, and ARRAY_AGG() for array aggregation. PostgreSQL is strongly typed — type mismatches cause errors. For MySQL/MariaDB, use LIMIT/OFFSET for pagination, LIKE (case-insensitive by default for ASCII), NOW() for current timestamp, and GROUP_CONCAT() for string aggregation. For MongoDB, queries use JSON-like document syntax with operators like $match, $group, $sort, $project for aggregation pipelines. For Redis, use GET/SET for key-value operations, KEYS/SCAN for key discovery, and HSET/HGET for hash operations. For DuckDB, the syntax is similar to PostgreSQL with additional analytical functions like PIVOT, UNPIVOT, and window functions optimized for OLAP workloads. For ChromaDB, queries use the collection.query() interface with text embeddings and metadata filters. For LanceDB, queries use the table.search() interface with vector similarity and metadata filtering.

## Session Management and Connection Lifecycle
Database connections persist for the duration of the server session unless explicitly closed. The DatabaseManager singleton tracks the status of each registered connection (DISCONNECTED, CONNECTING, CONNECTED, ERROR). Connections are established lazily — registering a connection does not immediately connect to the database. The init operation explicitly establishes the connection. Connections that encounter errors transition to ERROR status and must be re-initialized after the underlying issue is resolved. To close a connection, use the close operation which transitions to DISCONNECTED. All connections are automatically closed when the server shuts down via the registered signal handlers. The set_active/get_active operations manage which connection is used by default when no connection_name is specified. Connection metadata (type, config, status) is available via get_info. Preferences (default limit, timeout, output format) are managed via get_preferences/set_preferences and persist for the session.

## Best Practices for Query Construction
Write efficient, safe queries following these guidelines: always use parameterized queries via the parameters dict to prevent SQL injection — never concatenate user input into query strings. Use EXPLAIN ANALYZE (PostgreSQL) or EXPLAIN QUERY PLAN (SQLite) to understand query execution plans. Add indexes for columns used in WHERE, JOIN, and ORDER BY clauses. Avoid SELECT * in production queries — specify only the columns you need. Use LIMIT with ORDER BY for pagination instead of fetching all rows. For aggregation queries, use GROUP BY with appropriate aggregate functions (COUNT, SUM, AVG, MAX, MIN). Use JOIN instead of subqueries when possible for better performance. For large INSERT operations, use batch_insert instead of individual INSERT statements wrapped in a transaction. Use prepared statements for repeated queries with different parameters. Set appropriate transaction isolation levels for your use case — READ COMMITTED is suitable for most applications, REPEATABLE READ for financial transactions, SERIALIZABLE for critical consistency requirements.

## CLI Tool Reference
The server includes a CLI tool (mcp-db) for direct database operations outside of MCP. Run `uv run python -m database_operations_mcp.cli` to access the CLI help. The CLI supports: database list-tables (list tables with connection string and type), database list-databases (list available databases), database describe-table (show table schema), firefox list-profiles (list Firefox profiles), health (check system health and dependencies). The CLI uses the Click library with Rich console output for formatted tables. Connection strings and database types are passed as command-line options. Output formats include table (default), JSON, and CSV. The CLI is useful for ad-hoc database operations without requiring an MCP client or web dashboard. It shares the same connector implementations as the MCP server.

## Migration Between Database Types
When migrating between database types, be aware of these compatibility considerations. Data types differ: SQLite INTEGER maps to PostgreSQL INTEGER or BIGINT, TEXT maps to VARCHAR or TEXT, REAL maps to FLOAT or DOUBLE PRECISION. SQL functions differ: SQLite's datetime() uses a different syntax than PostgreSQL's NOW() or MySQL's CURDATE(). Transaction support varies: SQLite supports transactions but with limited concurrency (one writer at a time), PostgreSQL supports full ACID with MVCC, MySQL/InnoDB supports transactions but MyISAM does not. Query syntax differences: string concatenation uses || in SQLite/PostgreSQL, CONCAT() in MySQL. LIMIT/OFFSET syntax is consistent across SQLite, PostgreSQL, MySQL, and DuckDB. MongoDB uses an entirely different query model (documents, aggregation pipelines) — migration requires significant query rewriting. Use the export_query_results and batch_insert tools for cross-database data migration with transformation in between.

## Connector Configuration Reference
Each database type requires specific connection parameters. For SQLite, the connection string is a file path (e.g., C:/data/mydb.sqlite, :memory: for in-memory databases). File paths must be absolute. The parent directory must exist — the server does not create databases automatically. For PostgreSQL, use the standard URI format: postgresql://username:password@host:port/database. SSL connections use postgresql+sslmode=require://... or set sslmode in the connection parameters. For MongoDB: mongodb://username:password@host:port/database?options. For Redis: redis://host:port/db_number or redis://username:password@host:port/db_number. For ChromaDB: http://host:port (the HTTP endpoint of the ChromaDB server). For DuckDB: file path to the DuckDB database file or :memory:. For LanceDB: directory path where the LanceDB dataset is stored. For MySQL/MariaDB: mysql://username:password@host:port/database. Connection pooling is handled automatically by each connector implementation — tuning parameters are available in the connector source code.

## Error Recovery Procedures
When a database connection fails, first verify the connection string format. Use list_supported_databases to confirm the database type is supported. Use test_connection for detailed diagnostics. Check that the database server is running and accessible from the host machine. If the connection was previously working, check for network changes, credential rotation, or database server restarts. For SQLite, verify the file path exists and is readable. For PostgreSQL/MySQL, check host, port, and firewall rules. For Redis, verify the server is listening on the expected port. For ChromaDB, verify the HTTP endpoint is reachable. If a query fails, check the SQL syntax for compatibility with the database dialect. Use the activity log to review recent errors. The error_type field helps identify the class of failure: fatal (unrecoverable), retryable (transient network issue), user_fixable (wrong credentials), invalid_input (bad query syntax).

## Web Dashboard Usage Guide
The web_sota dashboard on port 10708 provides a visual interface for all database operations. The Dashboard page shows server health, active connections, and recent activity. The Tools page lists all registered MCP tools with their input schemas — portmanteau tools show the operation enum values for easy selection. The Logs page provides interactive log filtering with level, kind, and text search — results can be exported as CSV or JSON. The API Docs page embeds Swagger UI and ReDoc for the REST API. The sidebar provides navigation between all pages with a connection status indicator. The chat page enables direct tool calling through the MCP interface. The dashboard uses the fleet SOTA Slate/Amber dark theme with Tailwind CSS and Framer Motion animations. The Vite dev server proxies /api requests to the backend on port 10709. For production, build the frontend and serve it from the backend as static files.

## Database-Specific Configuration Examples
Each database type has specific configuration requirements. For SQLite: the connection string is a file path (C:/data/mydb.sqlite). The file is created if it does not exist. For in-memory databases, use ":memory:" as the connection string — data is lost when the connection is closed. For PostgreSQL: include the database name in the connection string URI (postgresql://user:pass@host:5432/dbname). Set search_path in connection parameters for schema selection. For MySQL: similar URI format to PostgreSQL but with mysql:// prefix. Use charset=utf8mb4 for full Unicode support. For MongoDB: include the database name in the path (mongodb://host:27017/mydb). Use replicaSet parameter for replica set connections. For Redis: specify the database number in the path (redis://host:6379/0). For cluster mode, use redis://host:6379/0?cluster=true. For ChromaDB: the connection string is the HTTP endpoint (http://host:8000). No database name is needed — ChromaDB manages collections internally. For DuckDB: file path to the database file or :memory:. For LanceDB: directory path. The connection is established lazily on first query or explicit init.

## Security Best Practices
When using the database-operations-mcp server, follow these security practices. Never share connection strings containing credentials. Use environment variables or a secrets manager for connection configuration. Use parameterized queries via the parameters dict to prevent SQL injection — never concatenate user input into query strings. Restrict database user permissions to the minimum required for the operations being performed. Use read-only database users for read-only operations. Monitor the activity log for suspicious query patterns. Close connections that are no longer needed. Use TLS for network connections to database servers. For production deployments, run the server behind a reverse proxy with authentication. Do not expose the MCP HTTP port (10709) to the public internet. The activity log records all tool calls with parameters — review it periodically for unauthorized access patterns. Use the safety_guard_status tool to verify that MUTATING/DESTRUCTIVE tool filtering is active.

## Version History and Changelog
The database-operations-mcp server follows semantic versioning. Version 1.4.1 is the current release with full support for 8 database types, portmanteau tool architecture, activity log ring buffer with CSV/JSON export, web_sota dashboard integration, agentic workflow support, and Firefox bookmarks integration. Version 1.4.0 added LanceDB connector support, extended export functionality, and improved error handling with structured error responses. Version 1.3.0 added the activity log system, web_sota API bridge, and Calibre integration. Version 1.2.0 added DuckDB and ChromaDB support, FTS search, and database analysis tools. Version 1.1.0 added MongoDB and Redis connectors, batch insert operations, and improved connection management. Version 1.0.0 was the initial release supporting SQLite, PostgreSQL, and MySQL with basic query and schema operations.

## Log Configuration Reference
The activity log captures server events and tool calls. Log levels are: DEBUG (detailed diagnostic), INFO (normal operations), WARNING (recoverable issues), ERROR (operation failures), CRITICAL (system failures). The ring buffer capacity is configurable from 100 to 50000 entries via DBOPS_LOG_MAX_ENTRIES. Export formats: JSON (structured, machine-readable) and CSV (spreadsheet-compatible). Log entries include: id (timestamp-based), timestamp (ISO 8601), level, kind (system, tool_call, error), detail (message), and meta (structured data).

## Best Practices for Data Export
When exporting query results, you should choose the format that best suits your specific needs. CSV format is ideal for spreadsheet import and simple data exchange — it is widely supported but has limitations with complex data types (nested objects, arrays). JSON is best for programmatic consumption — it preserves data types and structure. Use appropriate WHERE clauses to limit export size. For large exports, paginate with LIMIT/OFFSET or use date filters to export in batches. Always verify export completeness by comparing row counts with the source query. For sensitive data, ensure export files are stored securely and access is restricted.

## Common Troubleshooting Scenarios
When the server cannot connect to a database, check: the database server is running, the host and port are correct, firewall rules allow the connection, authentication credentials are valid, and the database client library is installed. When a query returns unexpected results, check: the query logic, data types and comparisons, NULL handling, and transaction isolation level. When the logs show no entries, check: the log level filter (INFO shows INFO+ only), the kind filter, and whether DBOPS_LOG_MAX_ENTRIES was exceeded (entries are evicted oldest-first). When the REST API returns 404, check: the URL path prefix (/api/ for most endpoints), the port (10709 for web bridge, 10708 for MCP HTTP), and whether the server is in HTTP mode.

## Uninstallation and Cleanup
To remove the server, delete the repository and any running processes. The server creates no system-wide files or registry entries. The activity log and connection registry are in-memory and cleared on shutdown. No persistent data is created outside the repository directory.

## Example Workflows for Common Tasks
Common database tasks are easily accomplished through the portmanteau tools. To explore a new database: register the connection, call list_tables to see available tables, call describe_table on each to understand the schema, then call quick_data_sample to preview the data. To clean up old data: query records older than a date, export them as a backup, then delete them. To migrate data between databases: query from the source, transform the results, then batch insert into the target. To generate a schema report: call get_schema_diff between staging and production, call describe_table on changed tables, and export the report as JSON. To optimize database performance: call database_health_check for overall health, call get_database_metrics for detailed metrics, vacuum the database if fragmentation is high, and review the activity log for slow queries. Each workflow chains multiple tool calls together, with intermediate results informing the next step.

## Database-Specific Notes
Each supported database type has unique characteristics to be aware of. SQLite uses dynamic typing — any column can store any type. It supports concurrent reads but only one writer at a time. The VACUUM command reclaims space but requires an exclusive lock. PostgreSQL uses strong typing with full MVCC for concurrent access. It supports schemas (like namespaces) for table organization. The pg_stat_statements extension provides query performance statistics. MySQL/MariaDB supports multiple storage engines (InnoDB for transactions, MyISAM for read-heavy workloads). InnoDB uses clustered indexes. MongoDB uses document-oriented storage with automatic sharding and replication. Redis is an in-memory data store with optional persistence. DuckDB is optimized for analytical queries on large datasets with columnar storage. ChromaDB provides vector similarity search for embeddings. LanceDB provides vector search with disk-based indexing.

## Best Practices for Connection Management
Follow these guidelines for managing database connections. Register connections with descriptive, unique names that indicate the database purpose and environment (e.g., "prod_pg_orders", "dev_sqlite_local", "staging_mongo_analytics"). Use test_all_connections periodically to verify all registered connections are healthy. Close connections that are no longer needed to free server resources. Use set_active to define a default connection for convenience — most tools use the active connection when connection_name is omitted. Store connection strings securely — avoid hardcoding credentials in configuration files. Use environment variables or a secrets manager for sensitive connection strings. Register connections at server startup via the restore_saved_database_connections mechanism for persistent configuration. Monitor connection status with the list operation — connections in ERROR status need attention before they can be used.

## Common Error Messages
Understanding error messages helps with troubleshooting. "Connection not registered" means the connection_name was not found in the DatabaseManager's registry — use list_connections to see available names and register if needed. "Unknown operation" means the operation value is not in the allowed enum — check the available values in the tool description or use help_system for documentation. "Database error" with a connection refused message means the database server is not running or the connection string is wrong — verify the database is accessible. "Query execution error" with a syntax error means the SQL is malformed — check for dialect-specific syntax differences. "Transaction failed" with a constraint violation means a UNIQUE, FOREIGN KEY, or CHECK constraint was violated — check the data being inserted. "Timeout" means the query took longer than the configured timeout — optimize the query or increase the timeout. "Already connected" means the connection was already initialized — use close first if you need to reconnect.

## Performance Optimization Tips
For slow queries, use indexed columns in WHERE clauses. Avoid SELECT * in production queries — specify only needed columns. Use LIMIT/OFFSET for pagination instead of fetching all rows. For batch operations, use batch_insert instead of individual inserts within a loop. The batch operation wraps multiple rows in a single transaction. Use the quick_data_sample tool for initial data exploration instead of full table scans. For large export operations, add appropriate WHERE clauses to limit the result set. The activity log records query execution times — use it to identify slow queries. For PostgreSQL, analyze query performance with EXPLAIN ANALYZE via the execute_query tool. For analytical workloads, consider DuckDB which is optimized for large-scale data analysis. The server supports parallel connections to different database types — queries against different databases run concurrently without blocking each other.

## REST API Detailed Reference

### Health Endpoint
GET /health — Returns {"status": "ok", "mcp": "database-operations-mcp"}. Use for load balancer health checks and container orchestration liveness probes.

### Capabilities Endpoint
GET /api/capabilities — Returns comprehensive capability matrix including total tools, portmanteau count, atomic count, prompt names, resource URIs, skill URIs, sampling tool indicators, and agentic workflow tool names. Use this for dynamic UI generation in the web dashboard.

### Tools List
GET /api/tools — Returns all registered MCP tools with their name, description, and inputSchema. The schema includes parameter names, types, defaults, and descriptions. Use for dynamic tool discovery and form generation.

### Call Tool
POST /api/tools/call with body {"name": "db_operations", "arguments": {"operation": "execute_query", "connection_name": "mydb", "query": "SELECT 1"}}.
Returns {"result": ..., "isError": false}. Errors are returned with isError=true and descriptive messages in the result.

### Activity Feed
GET /api/activity?limit=20 — Returns the most recent activity log entries. The activity captures tool calls, errors, and system events for real-time monitoring.

### Log Query
GET /api/logs?level=WARNING&search=timeout&limit=50&sort=desc&after_id=123456.789 — Advanced log query with level filter (ranked), text search, limit/offset pagination, sort direction, and cursor-based pagination via after_id.

### Log Statistics
GET /api/logs/stats — Returns aggregate log statistics: total entries, max capacity, rotation strategy, breakdown by level and kind, and oldest/newest timestamps.

### Log Export
GET /api/logs/export?format=csv&level=ERROR — Download all matching log entries as a file. JSON format returns structured data. CSV format is suitable for spreadsheet import. The filename includes a timestamp stamp.

## Troubleshooting

### Connection Refused
Database server not running or wrong connection string. Verify the database is running: check service status, port availability, and network connectivity. Use test_database_connection for diagnostics. Check logs for connection timeout details.

### Query Syntax Error
SQL syntax issue or incompatible database dialect. Verify the query syntax matches the database type (e.g., PostgreSQL uses LIMIT/OFFSET, SQL Server uses TOP, MySQL uses LIMIT). Check for reserved word conflicts. Use the database-specific documentation for dialect differences.

### Batch Insert Fails
Data type mismatch or constraint violation. Check that all records have the same keys matching the table columns. Verify data types (string vs. numeric vs. datetime). Check for NOT NULL constraints, unique constraints, and foreign key references. Reduce batch size for debugging.

### Transaction Rollback
One of the statements in the transaction failed. Check the transaction response for which statement caused the failure. Fix the offending statement and retry. The activity log will have ERROR-level entries with details.

### Agentic Workflow Timeout
The LLM sampling step exceeded the timeout. Simplify the goal into smaller sub-tasks. Reduce the number of intermediate steps. Ensure the MCP client supports sampling with adequate timeout.

## FAQ

**Q: Can I use multiple database types simultaneously?**
A: Yes. Register connections for each type and switch between them with set_active.

**Q: Are connections persistent?**
A: Registered connections persist for the session. Saved connections can be restored with restore_saved_database_connections.

**Q: Does the server support prepared statements?**
A: Yes. Use the parameters dict for parameterized queries to prevent SQL injection.

**Q: Can I export large result sets?**
A: Yes, but there's no streaming export yet. For large exports, use the export_query_results operation with pagination.

**Q: What databases can I connect to?**
A: SQLite, PostgreSQL, MySQL/MariaDB, MongoDB, ChromaDB, Redis, DuckDB, and LanceDB.

**Q: Is there a web interface?**
A: Yes. A Vite React dashboard on port 10708 provides visual database management.

**Q: Does the server support vector databases?**
A: Yes. ChromaDB and LanceDB are supported for vector/embedding operations.
