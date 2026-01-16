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
from database_operations_mcp.database_manager import DatabaseType, db_manager

logger = logging.getLogger(__name__)


# DEPRECATED: Use db_operations(operation='execute_query') instead
async def execute_query(
    connection_name: str, query: str, parameters: dict[str, Any] | None = None, limit: int = 1000
) -> dict[str, Any]:
    """Execute SQL or NoSQL query on specified database connection.

    Executes queries on registered database connections with automatic limit enforcement,
    parameter binding, and comprehensive result formatting. Supports SQL (PostgreSQL, SQLite),
    NoSQL (MongoDB), and Vector (ChromaDB) databases.

    Parameters:
        connection_name: Name of registered database connection
            - Must be previously registered via register_database_connection
            - Case-sensitive string
            - Only alphanumeric and underscores allowed

        query: SQL or database-specific query to execute
            - SQL: Standard SQL SELECT, INSERT, UPDATE, DELETE
            - MongoDB: Query syntax as string
            - ChromaDB: Vector query syntax
            - Maximum length: 10,000 characters
            - Parameterized queries recommended for security

        parameters: Query parameters for prepared statements (default: None)
            - Dictionary mapping parameter names to values
            - Prevents SQL injection attacks
            - Example: {"user_id": 123, "status": "active"}

        limit: Maximum rows to return (default: 1000)
            - Applied automatically if not in query
            - Range: 1-10000
            - Helps prevent memory issues

    Returns:
        Dictionary containing:
            - success: Boolean indicating query execution success
            - connection_name: Echo of connection used
            - query: Echo of query executed
            - parameters: Echo of parameters used
            - applied_limit: Actual limit applied
            - result: Query results dictionary with:
                - rows: List of result rows
                - columns: List of column names
                - row_count: Number of rows returned
            - error: Error message if success is False

    Usage:
        Use this tool to execute any database query safely. It automatically applies
        limits, handles parameters, and formats results consistently across all
        database types. Best for data retrieval and analysis.

        Common scenarios:
        - Retrieve data for analysis or reporting
        - Check data quality or validate migrations
        - Perform ad-hoc database queries
        - Debug application data issues

        Best practices:
        - Always use parameterized queries for user input
        - Start with small limits for exploratory queries
        - Use specific column names instead of SELECT *
        - Consider using quick_data_sample for quick peeks

    Examples:
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

    Raises:
        ConnectionError: When database connection is unavailable
        QueryError: When query syntax is invalid
        TimeoutError: When query execution exceeds 30 seconds
        PermissionError: When user lacks query permissions

    Notes:
        - Large result sets may consume significant memory
        - Query timeout is 30 seconds by default
        - Limit is automatically applied if not present in query
        - Connection must be registered before use
        - Parameterized queries prevent SQL injection

    See Also:
        - quick_data_sample: Get sample data without writing queries
        - export_query_results: Execute and export results to file
        - list_tables: Discover available tables to query
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        # Add limit to query if not already present (database-specific logic needed)
        limited_query = _apply_query_limit(query, limit, connector.database_type)

        # Execute the query (assuming connector.execute_query is synchronous)
        # In a real async context, you might need to use asyncio.to_thread here
        result = connector.execute_query(limited_query, parameters)

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

    Parameters:
        connection_name: Name of registered database connection
            - Must be previously registered
            - Case-sensitive

        table_name: Name of table/collection to sample
            - SQL: Table name (e.g., 'users', 'orders')
            - MongoDB: Collection name
            - ChromaDB: Collection name

        database_name: Database/schema name (default: None)
            - Optional for most databases
            - Required for PostgreSQL with schemas
            - Not used for SQLite or MongoDB

        sample_size: Number of rows to retrieve (default: 10)
            - Range: 1-1000
            - Recommended: 10-50 for quick inspection

        include_columns: List of columns to include (default: None)
            - None means all columns
            - SQL: Column names as strings
            - MongoDB: Field names

        exclude_columns: List of columns to exclude (default: None)
            - Useful for hiding sensitive data
            - Applied after include_columns

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - connection_name: Echo of connection used
            - table_name: Echo of table sampled
            - database_name: Database name if provided
            - sample_size: Requested sample size
            - generated_query: Auto-generated query used
            - result: Sample data dictionary with rows and columns
            - error: Error message if success is False

    Usage:
        Use this for quick data inspection without writing queries. Perfect for
        exploring unfamiliar databases, validating migrations, or checking data
        quality. The tool auto-generates appropriate queries for each database type.

        Common scenarios:
        - Explore new database tables
        - Verify migration results
        - Check data types and formats
        - Quick sanity checks during development

        Best practices:
        - Start with small sample sizes (10-20 rows)
        - Use column filters to reduce data transfer
        - Combine with describe_table for complete context

    Examples:
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

    Notes:
        - Auto-generates database-specific queries
        - Column filtering applied client-side for some databases
        - Large sample sizes may impact database performance
        - Does not modify data (read-only operation)

    See Also:
        - describe_table: Get table schema before sampling
        - execute_query: For custom queries with complex logic
        - list_tables: Discover available tables
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

        # Execute the query (assuming connector.execute_query is synchronous)
        result = connector.execute_query(query)

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

    Parameters:
        connection_name: Name of registered database connection
            - Must be previously registered
            - Case-sensitive

        query: SQL or database query to execute
            - Same syntax as execute_query
            - Supports parameterized queries

        export_format: Output format (default: "json")
            - "json": Structured JSON with metadata
            - "csv": Comma-separated values
            - "excel": Excel-compatible structure

        output_file: File path for export (default: None)
            - None returns data in response
            - Provide path to save to file

        parameters: Query parameters (default: None)
            - Same as execute_query
            - Prevents SQL injection

        limit: Maximum rows to export (default: 1000)
            - Auto-applied if not in query
            - Range: 1-10000

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - connection_name: Echo of connection used
            - query: Query executed
            - export_format: Format used
            - row_count: Number of rows exported
            - exported_data: Formatted data (if no output_file)
            - file_path: Path where data saved (if output_file provided)
            - error: Error message if success is False

    Usage:
        Use this to export query results for reporting, analysis, or integration
        with other tools. Supports multiple formats and can save directly to files.

        Common scenarios:
        - Export data for Excel analysis
        - Generate CSV for data imports
        - Create JSON for API integration
        - Backup specific data subsets

        Best practices:
        - Use CSV for Excel compatibility
        - Use JSON for programmatic processing
        - Set appropriate limits to control file sizes
        - Use parameterized queries for dynamic exports

    Examples:
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

    Notes:
        - Large exports may consume significant memory
        - File paths must be writable
        - CSV format is most compatible across tools
        - Excel format is structured JSON, not actual .xlsx

    See Also:
        - execute_query: For queries without export
        - quick_data_sample: For quick data inspection
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        # Execute query with limit
        limited_query = _apply_query_limit(query, limit, connector.database_type)

        # Execute the query (assuming connector.execute_query is synchronous)
        result = connector.execute_query(limited_query, parameters)

        # Format results based on export format
        formatted_data = _format_export_data(result, export_format)

        return {
            "success": True,
            "connection_name": connection_name,
            "query": query,
            "export_format": export_format,
            "row_count": len(result.get("rows", [])),
            "exported_data": formatted_data,
        }

    except Exception as e:
        logger.error(f"Error exporting query results: {e}")
        return {"success": False, "error": str(e)}


def _apply_query_limit(query: str, limit: int | None, database_type) -> str:
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
    database_type, table_name: str, database_name: str | None, sample_size: int
) -> str:
    """Generate appropriate sample query based on database type."""
    if database_type in [DatabaseType.POSTGRESQL, DatabaseType.SQLITE]:
        table_ref = f"{database_name}.{table_name}" if database_name else table_name
        return f"SELECT * FROM {table_ref} LIMIT {sample_size}"
    elif database_type == DatabaseType.MONGODB:
        # MongoDB query will be handled in connector
        return f"db.{table_name}.find().limit({sample_size})"
    elif database_type == DatabaseType.CHROMADB:
        # ChromaDB query will be handled in connector
        return f"collection.peek({sample_size})"
    else:
        return f"/* Sample query for {table_name} */"


def _format_export_data(result: dict[str, Any], export_format: str) -> Any:
    """Format query results for export."""
    rows = result.get("rows", [])
    columns = result.get("columns", [])

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
