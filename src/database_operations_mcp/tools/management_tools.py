"""
Database management and administration tools.

Handles health checks, performance monitoring, and administrative operations.
"""

import logging
from datetime import datetime
from typing import Any

# Import the global MCP instance
from database_operations_mcp.config.mcp_config import mcp

from ..database_manager import db_manager
from .help_tools import HelpSystem

logger = logging.getLogger(__name__)


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat()


# Register tools using the @mcp.tool decorator
# The mcp instance is imported from the centralized config


@mcp.tool()
@HelpSystem.register_tool
async def database_health_check(connection_name: str) -> dict[str, Any]:
    """Perform comprehensive health check on a database connection.

    Args:
        connection_name: Name of the registered connection
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        health_check = connector.health_check()

        return {
            "success": True,
            "connection_name": connection_name,
            "health_check": health_check,
            "timestamp": _get_timestamp(),
        }

    except Exception as e:
        logger.error(f"Error performing health check for {connection_name}: {e}")
        return {
            "success": False,
            "error": f"Health check failed: {str(e)}",
            "connection_name": connection_name,
            "timestamp": _get_timestamp(),
        }


@mcp.tool()
@HelpSystem.register_tool
async def get_database_metrics(
    connection_name: str, metric_names: list[str] | None = None
) -> dict[str, Any]:
    """Get performance metrics for a database connection.

    Args:
        connection_name: Name of the registered connection
        metric_names: Optional list of specific metrics to retrieve
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        metrics = connector.get_metrics(metric_names)

        return {
            "success": True,
            "connection_name": connection_name,
            "metrics": metrics,
            "timestamp": _get_timestamp(),
        }

    except Exception as e:
        logger.error(f"Error getting metrics for {connection_name}: {e}")
        return {
            "success": False,
            "error": f"Failed to get metrics: {str(e)}",
            "connection_name": connection_name,
            "timestamp": _get_timestamp(),
        }


@mcp.tool()
@HelpSystem.register_tool
async def vacuum_database(
    connection_name: str, analyze: bool = True, full: bool = False
) -> dict[str, Any]:
    """Run VACUUM on a database to optimize storage.

    Args:
        connection_name: Name of the registered connection
        analyze: Whether to run ANALYZE after VACUUM
        full: Whether to perform a full VACUUM (locks the database)
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        result = connector.vacuum(analyze=analyze, full=full)

        return {
            "success": True,
            "connection_name": connection_name,
            "operation": "VACUUM" + (" FULL" if full else "") + (" ANALYZE" if analyze else ""),
            "result": result,
            "timestamp": _get_timestamp(),
        }

    except Exception as e:
        logger.error(f"Error running VACUUM on {connection_name}: {e}")
        return {
            "success": False,
            "error": f"VACUUM failed: {str(e)}",
            "connection_name": connection_name,
            "timestamp": _get_timestamp(),
        }


@mcp.tool()
@HelpSystem.register_tool
async def disconnect_database(connection_name: str) -> dict[str, Any]:
    """Safely disconnect from a database.

    Args:
        connection_name: Name of the registered connection to disconnect

    Returns:
        Dictionary with operation status and details
    """
    try:
        success = db_manager.disconnect(connection_name)
        return {
            "success": success,
            "connection_name": connection_name,
            "message": f"Successfully disconnected from {connection_name}"
            if success
            else f"Failed to disconnect from {connection_name}",
            "timestamp": _get_timestamp(),
        }
    except Exception as e:
        logger.error(f"Error disconnecting from {connection_name}: {e}")
        return {
            "success": False,
            "error": f"Failed to disconnect: {str(e)}",
            "connection_name": connection_name,
            "timestamp": _get_timestamp(),
        }
