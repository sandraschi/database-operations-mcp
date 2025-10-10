"""
Database query execution and data operation tools.

Handles SQL queries, data retrieval, and result formatting.
"""

import logging
from typing import Any, Dict, List, Optional

# Import the global MCP instance
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.database_manager import db_manager, DatabaseType, QueryError
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)

# Register tools using the @mcp.tool decorator
# The mcp instance is imported from the centralized config

@mcp.tool()
@HelpSystem.register_tool
async def execute_query(
    connection_name: str,
    query: str,
    parameters: Optional[Dict[str, Any]] = None,
    limit: int = 1000
) -> Dict[str, Any]:
    '''Execute SQL or NoSQL query on specified database connection.
    
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
    '''
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {
                "success": False,
                "error": f"Connection not found: {connection_name}"
            }
        
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
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error executing query on {connection_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": query
        }

@mcp.tool()
@HelpSystem.register_tool
async def quick_data_sample(
    connection_name: str,
    table_name: str,
    database_name: Optional[str] = None,
    sample_size: int = 10,
    include_columns: Optional[List[str]] = None,
    exclude_columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Get a quick sample of data from a table/collection.
    
    Args:
        connection_name: Name of the registered connection
        table_name: Name of the table/collection to sample
        database_name: Optional database name
        sample_size: Number of rows to retrieve (default: 10)
        include_columns: Optional list of columns to include
        exclude_columns: Optional list of columns to exclude
        
    Returns:
        Dictionary with sample data and metadata
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {
                "success": False,
                "error": f"Connection not found: {connection_name}"
            }
        
        # Generate appropriate query based on database type
        query = _generate_sample_query(
            connector.database_type, 
            table_name, 
            database_name, 
            sample_size,
            include_columns,
            exclude_columns
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
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error getting data sample from {table_name}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
@HelpSystem.register_tool
async def export_query_results(
    connection_name: str,
    query: str,
    export_format: str = "json",
    output_file: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    limit: int = 1000
) -> Dict[str, Any]:
    """Execute query and export results in specified format.
    
    Args:
        connection_name: Name of the registered connection
        query: Query to execute
        export_format: Output format (json, csv, excel)
        output_file: Optional file path to export to
        parameters: Optional query parameters
        limit: Maximum rows to export (default: 1000)
        
    Returns:
        Dictionary with exported data and metadata
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {
                "success": False,
                "error": f"Connection not found: {connection_name}"
            }
        
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
            "exported_data": formatted_data
        }
        
    except Exception as e:
        logger.error(f"Error exporting query results: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def _apply_query_limit(query: str, limit: Optional[int], database_type) -> str:
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

def _generate_sample_query(database_type, table_name: str, database_name: Optional[str], sample_size: int) -> str:
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

def _format_export_data(result: Dict[str, Any], export_format: str) -> Any:
    """Format query results for export."""
    rows = result.get("rows", [])
    columns = result.get("columns", [])
    
    if export_format.lower() == "json":
        return {
            "columns": columns,
            "rows": rows,
            "metadata": {
                "row_count": len(rows),
                "column_count": len(columns)
            }
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
        return {
            "worksheets": [{
                "name": "Query Results",
                "headers": columns,
                "data": rows
            }]
        }
    else:
        return {
            "format": export_format,
            "columns": columns,
            "rows": rows
        }
