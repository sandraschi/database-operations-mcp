"""
Database schema inspection and metadata tools.

Handles table/collection discovery, schema analysis, and metadata operations.
"""

import logging
from typing import Any, Dict, List, Optional

# Import the global MCP instance
from database_operations_mcp.config.mcp_config import mcp
from ..database_manager import db_manager, DatabaseType
from .help_tools import HelpSystem

logger = logging.getLogger(__name__)

# Register tools using the @mcp.tool decorator
# The mcp instance is imported from the centralized config

@mcp.tool()
@HelpSystem.register_tool
async def list_databases(connection_name: str) -> Dict[str, Any]:
    """List all databases/schemas available on the specified connection.
    
    Args:
        connection_name: Name of the registered connection
        
    Returns:
        Dictionary with database list and metadata
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {
                "success": False,
                "error": f"Connection not found: {connection_name}"
            }
        
        # Get list of databases (implementation depends on database type)
        databases = await connector.list_databases()
        
        return {
            "success": True,
            "connection_name": connection_name,
            "databases": databases,
            "total_databases": len(databases)
        }
        
    except Exception as e:
        logger.error(f"Error listing databases for {connection_name}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
@HelpSystem.register_tool
async def list_tables(
    connection_name: str, 
    database_name: Optional[str] = None
) -> Dict[str, Any]:
    """List all tables/collections in the specified database/schema.
    
    Args:
        connection_name: Name of the registered connection
        database_name: Optional database/schema name
        
    Returns:
        Dictionary with table list and metadata
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {
                "success": False,
                "error": f"Connection not found: {connection_name}"
            }
        
        # Get list of tables (implementation depends on database type)
        tables = await connector.list_tables(database=database_name)
        
        return {
            "success": True,
            "connection_name": connection_name,
            "database_name": database_name,
            "tables": tables,
            "total_tables": len(tables)
        }
        
    except Exception as e:
        logger.error(f"Error listing tables for {connection_name}.{database_name}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
@HelpSystem.register_tool
async def describe_table(
    connection_name: str,
    table_name: str,
    database_name: Optional[str] = None
) -> Dict[str, Any]:
    """Get detailed information about a specific table/collection.
    
    Args:
        connection_name: Name of the registered connection
        table_name: Name of the table/collection
        database_name: Optional database/schema name
        
    Returns:
        Dictionary with table schema and metadata
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {
                "success": False,
                "error": f"Connection not found: {connection_name}"
            }
        
        # Get table schema (implementation depends on database type)
        schema_info = await connector.get_table_schema(table_name, database=database_name)
        
        return {
            "success": True,
            "connection_name": connection_name,
            "database_name": database_name,
            "table_name": table_name,
            "schema": schema_info
        }
        
    except Exception as e:
        logger.error(f"Error describing table {table_name} in {connection_name}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
@HelpSystem.register_tool
async def get_schema_diff(
    connection_name: str,
    table1: str,
    table2: str,
    database1: Optional[str] = None,
    database2: Optional[str] = None
) -> Dict[str, Any]:
    """Compare the schemas of two tables/collections.
    
    Args:
        connection_name: Name of the registered connection
        table1: First table/collection name
        table2: Second table/collection name
        database1: Optional database/schema name for first table
        database2: Optional database/schema name for second table
        
    Returns:
        Dictionary with schema comparison results
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {
                "success": False,
                "error": f"Connection not found: {connection_name}"
            }
        
        # Get both table schemas
        schema1 = await connector.get_table_schema(table1, database=database1)
        schema2 = await connector.get_table_schema(table2, database=database2)
        
        # Compare schemas (simple implementation)
        diff = {
            "tables_match": table1 == table2,
            "column_differences": [],
            "type_differences": []
        }
        
        # This is a simplified comparison - actual implementation would be more detailed
        if isinstance(schema1, dict) and isinstance(schema2, dict):
            cols1 = {col["name"]: col for col in schema1.get("columns", [])}
            cols2 = {col["name"]: col for col in schema2.get("columns", [])}
            
            # Find columns in table1 but not in table2
            for col_name, col_info in cols1.items():
                if col_name not in cols2:
                    diff["column_differences"].append({
                        "column": col_name,
                        "status": "only_in_table1",
                        "table1_type": col_info.get("type")
                    })
            
            # Find columns in table2 but not in table1
            for col_name, col_info in cols2.items():
                if col_name not in cols1:
                    diff["column_differences"].append({
                        "column": col_name,
                        "status": "only_in_table2",
                        "table2_type": col_info.get("type")
                    })
            
            # Find columns with different types
            for col_name, col_info in cols1.items():
                if col_name in cols2 and col_info.get("type") != cols2[col_name].get("type"):
                    diff["type_differences"].append({
                        "column": col_name,
                        "table1_type": col_info.get("type"),
                        "table2_type": cols2[col_name].get("type")
                    })
        
        return {
            "success": True,
            "connection_name": connection_name,
            "table1": {"name": table1, "database": database1},
            "table2": {"name": table2, "database": database2},
            "diff": diff
        }
        
    except Exception as e:
        logger.error(f"Error comparing schemas for {table1} and {table2}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
