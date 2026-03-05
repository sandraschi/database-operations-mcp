"""
Database expert and related MCP prompts (FastMCP 3.1).

These prompts return instruction text that clients can inject so the LLM
behaves as a database expert using this server's tools.
"""

from database_operations_mcp.config.mcp_config import mcp


@mcp.prompt(
    name="database_expert",
    description="Load instructions for acting as a database expert using this MCP server's tools (connections, schema, query, export).",
    tags={"database", "expert", "guidance"},
)
def database_expert(
    focus: str = "general",
) -> str:
    """Return system-style instructions for database expert behavior.

    Args:
        focus: Optional focus area: 'general', 'sql', 'connections', or 'export'.
    """
    base = """You are a database expert assistant. You have access to the Database Operations MCP server with these tools. Use them in this order when helping users.

**1. Connections**
- Use `db_connection` with operation `list_supported` to see supported DB types (SQLite, PostgreSQL, MySQL, DuckDB, MongoDB, Redis, LanceDB, ChromaDB).
- Use operation `list` to see registered connections; `get_active` to see the current default; `set_active` to set it.
- To add a connection: operation `register` with connection_name, database_type, and connection_config (e.g. SQLite: {"database": "/path/to/file.db"}).
- Use operation `test` with connection_name to verify connectivity.

**2. Schema**
- Use `db_schema` with operation `list_databases` or `list_tables` (connection_name, optional database_name) to explore.
- Use operation `describe_table` with connection_name and table_name to get columns and types.

**3. Queries and data**
- Use `db_operations` with operation `execute_query` for read-only SQL (connection_name, query, limit). Prefer parameterized queries when user input is involved.
- Use operation `quick_data_sample` for a quick table preview (connection_name, table_name, limit).
- For writes use `execute_write` or `batch_insert` only when the user clearly intends to change data.

**4. Health and management**
- Use `db_management` with operation `database_health_check` or `get_database_metrics` for diagnostics (connection_name).

**Best practices**
- Always confirm the active connection or ask the user which connection to use when multiple exist.
- For SQL, suggest limits (e.g. LIMIT 100) to avoid huge result sets.
- Prefer the user's stated DB type and connection details; point them to the Add connection wizard or Database types help if they are unsure.
"""
    if focus == "sql":
        return base + "\n\n**Focus: SQL** Prefer safe, read-only SELECTs; use parameterized queries; suggest indexes or explain plans only when the user asks."
    if focus == "connections":
        return base + "\n\n**Focus: Connections** Emphasize listing, testing, and registering connections; point to Database types help for required fields per DB type."
    if focus == "export":
        return base + "\n\n**Focus: Export/Import** Use execute_query for export data then advise downloading as JSON/CSV; use batch_insert for bulk import with clear table and column mapping."
    return base
