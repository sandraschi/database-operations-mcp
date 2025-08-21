"""
Database schema inspection and metadata tools.

Handles table/collection discovery, schema analysis, and metadata operations.
"""

import logging
from typing import Any, Dict, List, Optional

from ..database_manager import db_manager

logger = logging.getLogger(__name__)

def register_tools(mcp):
    """Register schema inspection tools with the MCP server."""
    
    @mcp.tool()
    def list_databases(connection_name: str) -> Dict[str, Any]:
        """List all databases/schemas available on the specified connection.
        
        Args:
            connection_name: Name of the registered connection
        """
        try:
            connector = db_manager.get_connector(connection_name)
            if not connector:
                return {
                    "success": False,
                    "error": f"Connection not found: {connection_name}"
                }
            
            # Note: list_databases method needs to be implemented in base class
            databases = ["default"]  # Placeholder until implementation
            
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
    def list_tables(connection_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """List all tables/collections in the specified database.
        
        Args:
            connection_name: Name of the registered connection
            database_name: Optional database name (for multi-database systems)
        """
        try:
            connector = db_manager.get_connector(connection_name)
            if not connector:
                return {
                    "success": False,
                    "error": f"Connection not found: {connection_name}"
                }
            
            tables = connector.get_tables(database=database_name)
            
            return {
                "success": True,
                "connection_name": connection_name,
                "database_name": database_name,
                "tables": tables,
                "total_tables": len(tables)
            }
            
        except Exception as e:
            logger.error(f"Error listing tables for {connection_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @mcp.tool()
    def describe_table(
        connection_name: str, 
        table_name: str, 
        database_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed schema information for a specific table/collection.
        
        Args:
            connection_name: Name of the registered connection
            table_name: Name of the table/collection to describe
            database_name: Optional database name (for multi-database systems)
        """
        try:
            connector = db_manager.get_connector(connection_name)
            if not connector:
                return {
                    "success": False,
                    "error": f"Connection not found: {connection_name}"
                }
            
            schema_info = connector.get_table_schema(table_name, database=database_name)
            
            return {
                "success": True,
                "connection_name": connection_name,
                "database_name": database_name,
                "table_name": table_name,
                "schema_info": schema_info
            }
            
        except Exception as e:
            logger.error(f"Error describing table {table_name} for {connection_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @mcp.tool()
    def analyze_database_schema(
        connection_name: str, 
        database_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive schema analysis of a database.
        
        Args:
            connection_name: Name of the registered connection
            database_name: Optional database name (for multi-database systems)
        """
        try:
            connector = db_manager.get_connector(connection_name)
            if not connector:
                return {
                    "success": False,
                    "error": f"Connection not found: {connection_name}"
                }
            
            # Get all tables
            tables = connector.get_tables(database=database_name)
            
            # Analyze each table
            table_analysis = {}
            total_columns = 0
            
            for table in tables:
                table_name = table
                try:
                    schema_info = connector.get_table_schema(table_name, database=database_name)
                    table_analysis[table_name] = {
                        "schema": schema_info,
                        "column_count": len(schema_info.get("columns", [])),
                        "data_types": schema_info.get("data_types", [])
                    }
                    total_columns += table_analysis[table_name]["column_count"]
                except Exception as e:
                    table_analysis[table_name] = {
                        "error": f"Failed to analyze: {str(e)}"
                    }
            
            return {
                "success": True,
                "connection_name": connection_name,
                "database_name": database_name,
                "summary": {
                    "total_tables": len(tables),
                    "total_columns": total_columns,
                    "analyzed_tables": len([t for t in table_analysis.values() if "error" not in t]),
                    "failed_tables": len([t for t in table_analysis.values() if "error" in t])
                },
                "table_analysis": table_analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing schema for {connection_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
