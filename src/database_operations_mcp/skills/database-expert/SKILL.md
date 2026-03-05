---
description: Act as a database expert using the Database Operations MCP tools (connections, schema, query, export)
---

# Database expert skill

When helping with databases, use the Database Operations MCP server's tools in this order.

## 1. Connections

- **List supported types**: `db_connection(operation="list_supported")` — SQLite, PostgreSQL, MySQL, DuckDB, MongoDB, Redis, LanceDB, ChromaDB.
- **List registered**: `db_connection(operation="list")`; **get/set active**: `get_active`, `set_active` with connection_name.
- **Register**: `db_connection(operation="register", connection_name=..., database_type=..., connection_config={...})`. For SQLite use `{"database": "/path/to/file.db"}`; for PostgreSQL use host, port, user, password, database.
- **Test**: `db_connection(operation="test", connection_name=...)`.

Refer users to the **Database types help** page or in-app help for required fields per DB type.

## 2. Schema

- **List databases**: `db_schema(operation="list_databases", connection_name=...)`.
- **List tables**: `db_schema(operation="list_tables", connection_name=..., database_name=...)`.
- **Describe table**: `db_schema(operation="describe_table", connection_name=..., table_name=...)` for columns and types.

## 3. Queries and data

- **Read-only SQL**: `db_operations(operation="execute_query", connection_name=..., query="SELECT ...", limit=...)`. Prefer parameterized queries when user input is involved.
- **Quick sample**: `db_operations(operation="quick_data_sample", connection_name=..., table_name=..., limit=...)`.
- **Writes**: Use `execute_write` or `batch_insert` only when the user clearly intends to change data.

## 4. Health and management

- **Health check**: `db_management(operation="database_health_check", connection_name=...)`.
- **Metrics**: `db_management(operation="get_database_metrics", connection_name=...)`.

## Best practices

- Confirm the active connection or ask which connection to use when multiple exist.
- Suggest limits (e.g. LIMIT 100) for ad-hoc SELECTs.
- Point users to the Add connection wizard or Database types help when they are unsure how to connect.
