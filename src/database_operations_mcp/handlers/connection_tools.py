"""
Database connection management tools.

Handles database registration, testing, and connection lifecycle.
"""

import logging
from typing import Any, Dict, List, Optional

from database_operations_mcp.database_manager import (
    db_manager, 
    create_connector, 
    get_supported_databases
)

logger = logging.getLogger(__name__)

def register_tools(mcp):
    """Register connection management tools with the MCP server."""
    
    @mcp.tool()
    def list_supported_databases() -> List[Dict[str, Any]]:
        """List all supported database types with categories and descriptions.
        
        Returns comprehensive information about supported databases organized by category.
        """
        try:
            databases = get_supported_databases()
            
            # Group by category for better organization
            categorized = {}
            for db in databases:
                category = db["category"]
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(db)
            
            return {
                "success": True,
                "databases_by_category": categorized,
                "total_supported": len(databases),
                "categories": list(categorized.keys())
            }
        except Exception as e:
            logger.error(f"Error listing supported databases: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @mcp.tool()
    def register_database_connection(
        connection_name: str,
        database_type: str,
        connection_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register a new database connection.
        
        Args:
            connection_name: Unique name for this connection
            database_type: Type of database (postgresql, sqlite, chromadb, etc.)
            connection_config: Database-specific connection parameters
            
        Example configs:
            PostgreSQL: {"host": "localhost", "port": 5432, "database": "mydb", "user": "user", "password": "pass"}
            SQLite: {"database_path": "/path/to/database.db"}
            ChromaDB: {"host": "localhost", "port": 8000} or {"persist_directory": "/path/to/persist"}
        """
        try:
            # Create connector
            connector = create_connector(database_type, connection_config)
            if not connector:
                return {
                    "success": False,
                    "error": f"Unsupported database type: {database_type}"
                }
            
            # Register with manager
            success = db_manager.register_connector(connection_name, connector)
            if not success:
                return {
                    "success": False,
                    "error": f"Failed to register connection: {connection_name}"
                }
            
            # Test connection
            test_result = connector.test_connection()
            
            return {
                "success": True,
                "connection_name": connection_name,
                "database_type": database_type,
                "test_result": test_result,
                "connection_info": connector.get_connection_info()
            }
            
        except Exception as e:
            logger.error(f"Error registering database connection {connection_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @mcp.tool()
    def list_database_connections() -> Dict[str, Any]:
        """List all registered database connections with their status."""
        try:
            connections = db_manager.list_connectors()
            
            return {
                "success": True,
                "connections": connections,
                "total_connections": len(connections)
            }
            
        except Exception as e:
            logger.error(f"Error listing database connections: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @mcp.tool()
    def test_database_connection(connection_name: str) -> Dict[str, Any]:
        """Test connectivity for a specific database connection.
        
        Args:
            connection_name: Name of the registered connection to test
        """
        try:
            connector = db_manager.get_connector(connection_name)
            if not connector:
                return {
                    "success": False,
                    "error": f"Connection not found: {connection_name}"
                }
            
            test_result = connector.test_connection()
            
            return {
                "success": True,
                "connection_name": connection_name,
                "test_result": test_result,
                "connection_info": connector.get_connection_info()
            }
            
        except Exception as e:
            logger.error(f"Error testing connection {connection_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @mcp.tool()
    def test_all_database_connections() -> Dict[str, Any]:
        """Test connectivity for all registered database connections."""
        try:
            test_results = db_manager.test_all_connections()
            
            # Summarize results
            total = len(test_results)
            successful = sum(1 for result in test_results.values() if result.get("success", False))
            failed = total - successful
            
            return {
                "success": True,
                "test_results": test_results,
                "summary": {
                    "total_connections": total,
                    "successful": successful,
                    "failed": failed,
                    "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "0%"
                }
            }
            
        except Exception as e:
            logger.error(f"Error testing all connections: {e}")
            return {
                "success": False,
                "error": str(e)
            }

