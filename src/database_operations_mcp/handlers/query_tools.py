"""
Database query execution and data operation tools.

Handles SQL queries, data retrieval, and result formatting.
"""

import logging
from typing import Any, Dict, List, Optional

from ..database_manager import db_manager, DatabaseType

logger = logging.getLogger(__name__)

def register_tools(mcp):
    """Register query execution tools with the MCP server."""
    
    @mcp.tool()
    def execute_query(
        connection_name: str,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 1000
    ) -> Dict[str, Any]:
        """Execute a query on the specified database connection.
        
        Args:
            connection_name: Name of the registered connection
            query: SQL query or database-specific query to execute
            parameters: Optional query parameters for prepared statements
            limit: Maximum number of rows to return (default: 1000)
        """
        try:
            connector = db_manager.get_connector(connection_name)
            if not connector:
                return {
                    "success": False,
                    "error": f"Connection not found: {connection_name}"
                }
            
            # Add limit to query if not already present (database-specific logic needed)
            limited_query = _apply_query_limit(query, limit, connector.database_type)
            
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
    def quick_data_sample(
        connection_name: str,
        table_name: str,
        database_name: Optional[str] = None,
        sample_size: int = 10
    ) -> Dict[str, Any]:
        """Get a quick sample of data from a table/collection.
        
        Args:
            connection_name: Name of the registered connection
            table_name: Name of the table/collection to sample
            database_name: Optional database name
            sample_size: Number of rows to retrieve (default: 10)
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
                sample_size
            )
            
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
    def export_query_results(
        connection_name: str,
        query: str,
        export_format: str = "json",
        parameters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 10000
    ) -> Dict[str, Any]:
        """Execute query and export results in specified format.
        
        Args:
            connection_name: Name of the registered connection
            query: Query to execute
            export_format: Output format (json, csv, excel)
            parameters: Optional query parameters
            limit: Maximum rows to export
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
