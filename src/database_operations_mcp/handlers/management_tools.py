"""
Database management and administration tools.

Handles health checks, performance monitoring, and administrative operations.
"""

import logging
from typing import Any, Dict, List, Optional

from ..database_manager import db_manager

logger = logging.getLogger(__name__)

def register_tools(mcp):
    """Register database management tools with the MCP server."""
    
    @mcp.tool()
    def database_health_check(connection_name: str) -> Dict[str, Any]:
        """Perform comprehensive health check on a database connection.
        
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
            
            health_check = connector.health_check()
            
            return {
                "success": True,
                "connection_name": connection_name,
                "health_check": health_check,
                "timestamp": _get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error performing health check for {connection_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": _get_timestamp()
            }

    @mcp.tool()
    def get_performance_metrics(connection_name: str) -> Dict[str, Any]:
        """Get performance metrics for a database connection.
        
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
            
            # Note: performance metrics method needs to be implemented in base class
            metrics = {"status": "not_implemented", "message": "Performance metrics feature needs implementation"}
            
            return {
                "success": True,
                "connection_name": connection_name,
                "performance_metrics": metrics,
                "timestamp": _get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics for {connection_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": _get_timestamp()
            }

    @mcp.tool()
    def monitor_all_databases() -> Dict[str, Any]:
        """Monitor health and performance of all registered database connections.
        """
        try:
            connections = db_manager.list_connectors()
            monitoring_results = {}
            
            for conn_name, conn_info in connections.items():
                try:
                    connector = db_manager.get_connector(conn_name)
                    if connector:
                        health = connector.health_check()
                        
                        monitoring_results[conn_name] = {
                            "database_type": conn_info["type"],
                            "status": conn_info["status"],
                            "health_check": health
                        }
                    else:
                        monitoring_results[conn_name] = {
                            "error": "Connector not found"
                        }
                except Exception as e:
                    monitoring_results[conn_name] = {
                        "error": str(e)
                    }
            
            # Generate summary
            total_connections = len(connections)
            healthy_connections = sum(
                1 for result in monitoring_results.values() 
                if result.get("health_check", {}).get("status") == "healthy"
            )
            
            return {
                "success": True,
                "monitoring_results": monitoring_results,
                "summary": {
                    "total_connections": total_connections,
                    "healthy_connections": healthy_connections,
                    "unhealthy_connections": total_connections - healthy_connections,
                    "health_percentage": f"{(healthy_connections/total_connections*100):.1f}%" if total_connections > 0 else "0%"
                },
                "timestamp": _get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error monitoring all databases: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": _get_timestamp()
            }

    @mcp.tool()
    def disconnect_database(connection_name: str) -> Dict[str, Any]:
        """Safely disconnect from a database.
        
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
            
            disconnect_success = connector.disconnect()
            
            return {
                "success": disconnect_success,
                "connection_name": connection_name,
                "message": "Database disconnected successfully" if disconnect_success else "Failed to disconnect database",
                "final_status": connector.status.value,
                "timestamp": _get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error disconnecting from {connection_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": _get_timestamp()
            }

    @mcp.tool()
    def reconnect_database(connection_name: str) -> Dict[str, Any]:
        """Reconnect to a database.
        
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
            
            # Disconnect first if connected
            if connector.status.value == "connected":
                connector.disconnect()
            
            # Reconnect
            connect_success = connector.connect()
            
            return {
                "success": connect_success,
                "connection_name": connection_name,
                "message": "Database reconnected successfully" if connect_success else "Failed to reconnect database",
                "new_status": connector.status.value,
                "timestamp": _get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error reconnecting to {connection_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": _get_timestamp()
            }

def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.now().isoformat()
