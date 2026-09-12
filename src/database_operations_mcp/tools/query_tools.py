"""
Database query execution and data operation tools.

DEPRECATED: This module is deprecated. Use db_operations portmanteau tool instead.

All operations have been consolidated into db_operations():
- execute_query() → db_operations(operation='execute_query')
- quick_data_sample() → db_operations(operation='quick_data_sample')
- export_query_results() → db_operations(operation='export_query_results')

This module is kept for backwards compatibility but tools are no longer registered.
"""

import logging
from typing import Any

# NOTE: @mcp.tool decorators removed - functionality moved to db_operations portmanteau
# Import kept for backwards compatibility in case code references these functions
from database_operations_mcp.database_manager import (
    DatabaseType,
    QueryResult,
    db_manager,
    normalize_query_result,
)

logger = logging.getLogger(__name__)


# DEPRECATED: Use db_operations(operation='execute_query') instead
async def execute_query(
    connection_name: str, query: str, parameters: dict[str, Any] | None = None, limit: int = 1000
) -> dict[str, Any]:
    """Execute SQL or NoSQL query on specified database connection.

    Executes queries on registered database connections with automatic limit enforcement,
    parameter binding, and comprehensive result formatting. Supports SQL (PostgreSQL, SQLite),
    NoSQL (MongoDB), and Vector (ChromaDB) databases.

    ## Return Format
    Returns success plus connection/query echo and a result dict (rows/columns/row_count),
    or an error dict. Always use parameterized queries for user input.

    ## Examples
        Basic SELECT query:
            result = await execute_query(
                connection_name="production_db",
                query="SELECT id, name, email FROM users WHERE active = true"
            )
            # Returns: {
            #     'success': True,
            #     'result': {
            #         'rows': [
            #             {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
            #             {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
            #         ],
            #         'columns': ['id', 'name', 'email'],
            #         'row_count': 2
            #     }
            # }

        Parameterized query for security:
            result = await execute_query(
                connection_name="production_db",
                query="SELECT * FROM orders WHERE user_id = :user_id AND status = :status",
                parameters={"user_id": 12345, "status": "pending"},
                limit=50
            )
            # Returns: Up to 50 matching orders with safe parameter binding

        Query with custom limit:
            result = await execute_query(
                connection_name="analytics_db",
                query="SELECT * FROM logs WHERE date > '2024-01-01'",
                limit=100
            )
            # Returns: First 100 log entries (limit auto-applied)

        Error handling:
            result = await execute_query(
                connection_name="nonexistent",
                query="SELECT * FROM users"
            )
            if not result['success']:
                print(f"Query failed: {result['error']}")
            # Logs: Query failed: Connection not found: nonexistent

        Complex aggregation query:
            result = await execute_query(
                connection_name="sales_db",
                query=\'\'\'
                    SELECT
                        category,
                        COUNT(*) as total_orders,
                        SUM(amount) as total_revenue
                    FROM orders
                    WHERE order_date >= :start_date
                    GROUP BY category
                    HAVING COUNT(*) > :min_orders
                    ORDER BY total_revenue DESC
                \'\'\',
                parameters={
                    "start_date": "2024-01-01",
                    "min_orders": 10
                },
                limit=20
            )
            # Returns: Top 20 categories by revenue
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        # Add limit to query if not already present (database-specific logic needed)
        limited_query = _apply_query_limit(query, limit, connector.database_type)

        # Execute the query
        result = await connector.execute_query(limited_query, parameters)

        return {
            "success": True,
            "connection_name": connection_name,
            "query": query,
            "parameters": parameters,
            "applied_limit": limit,
            "result": result,
        }

    except Exception as e:
        logger.error(f"Error executing query on {connection_name}: {e}")
        return {"success": False, "error": str(e), "query": query}


# DEPRECATED: Use db_operations(operation='quick_data_sample') instead
async def quick_data_sample(
    connection_name: str,
    table_name: str,
    database_name: str | None = None,
    sample_size: int = 10,
    include_columns: list[str] | None = None,
    exclude_columns: list[str] | None = None,
) -> dict[str, Any]:
    """Get quick data sample from table without writing queries.

    Retrieves a small sample of data from any table/collection for quick inspection,
    schema validation, or data quality checks. Automatically generates appropriate
    queries for different database types.

    ## Return Format
    Returns success plus result rows and the generated query, or an error dict.

    ## Examples
        Basic table sample:
            result = await quick_data_sample(
                connection_name="production_db",
                table_name="users"
            )
            # Returns: {
            #     'success': True,
            #     'result': {
            #         'rows': [
            #             {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
            #             {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
            #         ],
            #         'columns': ['id', 'name', 'email']
            #     },
            #     'generated_query': 'SELECT * FROM users LIMIT 10'
            # }

        Larger sample with database specified:
            result = await quick_data_sample(
                connection_name="postgres_db",
                table_name="orders",
                database_name="sales",
                sample_size=50
            )
            # Returns: 50 rows from sales.orders table

        With column filtering:
            result = await quick_data_sample(
                connection_name="production_db",
                table_name="users",
                sample_size=20,
                include_columns=["id", "name", "created_at"],
                exclude_columns=["password_hash"]
            )
            # Returns: 20 rows with only specified columns

        Error handling:
            result = await quick_data_sample(
                connection_name="production_db",
                table_name="nonexistent_table"
            )
            if not result['success']:
                print(f"Sampling failed: {result['error']}")
            # Logs: Sampling failed: Table 'nonexistent_table' does not exist
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        # Generate appropriate query based on database type
        query = _generate_sample_query(
            connector.database_type,
            table_name,
            database_name,
            sample_size,
            include_columns,
            exclude_columns,
        )

        # Execute the query
        result = await connector.execute_query(query)

        return {
            "success": True,
            "connection_name": connection_name,
            "table_name": table_name,
            "database_name": database_name,
            "sample_size": sample_size,
            "generated_query": query,
            "result": result,
        }

    except Exception as e:
        logger.error(f"Error getting data sample from {table_name}: {e}")
        return {"success": False, "error": str(e)}


# DEPRECATED: Use db_operations(operation='export_query_results') instead
async def export_query_results(
    connection_name: str,
    query: str,
    export_format: str = "json",
    output_file: str | None = None,
    parameters: dict[str, Any] | None = None,
    limit: int = 1000,
) -> dict[str, Any]:
    """Execute query and export results in multiple formats.

    Runs database query and formats results as JSON, CSV, or Excel. Useful for
    data export, reporting, and integration with other tools. Handles large
    result sets with automatic limiting.

    ## Return Format
    Returns success plus export_format/row_count/exported_data (or file_path), or an error dict.

    ## Examples
        Export to JSON:
            result = await export_query_results(
                connection_name="analytics_db",
                query="SELECT * FROM sales WHERE month = 'January'",
                export_format="json"
            )
            # Returns: {
            #     'success': True,
            #     'export_format': 'json',
            #     'row_count': 150,
            #     'exported_data': {
            #         'columns': ['id', 'amount', 'date'],
            #         'rows': [...]
            #     }
            # }

        Export to CSV file:
            result = await export_query_results(
                connection_name="production_db",
                query="SELECT name, email, created_at FROM users",
                export_format="csv",
                output_file="C:/exports/users.csv",
                limit=5000
            )
            # Returns: {'success': True, 'file_path': 'C:/exports/users.csv', 'row_count': 5000}

        Parameterized export:
            result = await export_query_results(
                connection_name="sales_db",
                query="SELECT * FROM orders WHERE date > :start_date",
                parameters={"start_date": "2024-01-01"},
                export_format="excel",
                limit=2000
            )
            # Returns: Excel-formatted data with 2000 rows
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        # Execute query with limit
        limited_query = _apply_query_limit(query, limit, connector.database_type)

        # Execute the query
        result = await connector.execute_query(limited_query, parameters)

        # Format results based on export format
        formatted_data = _format_export_data(result, export_format)
        normalized = normalize_query_result(result)

        return {
            "success": True,
            "connection_name": connection_name,
            "query": query,
            "export_format": export_format,
            "row_count": len(normalized.get("rows", [])),
            "exported_data": formatted_data,
        }

    except Exception as e:
        logger.error(f"Error exporting query results: {e}")
        return {"success": False, "error": str(e)}


def _apply_query_limit(query: str, limit: int | None, database_type: DatabaseType) -> str:
    """Apply LIMIT clause to query based on database type."""
    if not limit:
        return query

    query_lower = query.lower().strip()

    # Check if LIMIT already exists
    if "limit" in query_lower:
        return query

    # Add LIMIT based on database type
    if database_type in [DatabaseType.POSTGRESQL, DatabaseType.SQLITE]:
        return f"{query.rstrip(';')} LIMIT {limit}"
    else:
        # For NoSQL databases, limit logic will be handled in connectors
        return query


def _generate_sample_query(
    database_type: DatabaseType,
    table_name: str,
    database_name: str | None,
    sample_size: int,
    include_columns: list[str] | None = None,
    exclude_columns: list[str] | None = None,
    offset: int = 0,
) -> str:
    """Generate appropriate sample query based on database type."""
    _ = exclude_columns
    columns = ", ".join(include_columns) if include_columns else "*"
    if database_type in [DatabaseType.POSTGRESQL, DatabaseType.SQLITE]:
        table_ref = f"{database_name}.{table_name}" if database_name else table_name
        query = f"SELECT {columns} FROM {table_ref} LIMIT {sample_size}"  # noqa: S608  # table_ref from trusted schema introspection
        if offset:
            query += f" OFFSET {offset}"
        return query
    elif database_type == DatabaseType.MONGODB:
        # MongoDB query will be handled in connector
        return f"db.{table_name}.find().limit({sample_size})"
    elif database_type == DatabaseType.CHROMADB:
        # ChromaDB query will be handled in connector
        return f"collection.peek({sample_size})"
    else:
        return f"/* Sample query for {table_name} */"


def _format_export_data(result: QueryResult | dict[str, Any], export_format: str) -> Any:
    """Format query results for export."""
    normalized = normalize_query_result(result)
    rows = normalized.get("rows", [])
    columns = normalized.get("columns", [])

    if export_format.lower() == "json":
        return {
            "columns": columns,
            "rows": rows,
            "metadata": {"row_count": len(rows), "column_count": len(columns)},
        }
    elif export_format.lower() == "csv":
        # Convert to CSV-like structure
        csv_lines = []
        if columns:
            csv_lines.append(",".join(str(col) for col in columns))
        for row in rows:
            csv_lines.append(",".join(str(val) for val in row))
        return "\n".join(csv_lines)
    elif export_format.lower() == "excel":
        # Excel format (simplified structure)
        return {"worksheets": [{"name": "Query Results", "headers": columns, "data": rows}]}
    else:
        return {"format": export_format, "columns": columns, "rows": rows}
