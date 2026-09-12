"""
Database management and administration tools.

DEPRECATED: This module is deprecated. Use db_management portmanteau tool instead.

All operations have been consolidated into db_management():
- database_health_check() → db_management(operation='database_health_check')
- get_database_metrics() → db_management(operation='get_database_metrics')
- vacuum_database() → db_management(operation='vacuum_database')
- disconnect_database() → db_management(operation='disconnect_database')

This module is kept for backwards compatibility but tools are no longer registered.
"""

import logging
from datetime import datetime
from typing import Any

# NOTE: @mcp.tool decorators removed - functionality moved to db_management portmanteau
# Import kept for backwards compatibility in case code references these functions
from ..database_manager import db_manager

logger = logging.getLogger(__name__)


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat()


# DEPRECATED: Use db_management(operation='database_health_check') instead
async def database_health_check(connection_name: str) -> dict[str, Any]:
    """Perform comprehensive health check on a database connection.

    ## Return Format
    Returns success plus the health report, or an error dict.

    ## Examples
    Check a connection:
        result = await database_health_check("production_db")
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        health_check = await connector.health_check()

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
            "error": f"Health check failed: {e!s}",
            "connection_name": connection_name,
            "timestamp": _get_timestamp(),
        }


# DEPRECATED: Use db_management(operation='get_database_metrics') instead
async def get_database_metrics(connection_name: str, metric_names: list[str] | None = None) -> dict[str, Any]:
    """Get performance metrics for a database connection.

    ## Return Format
    Returns success plus metrics, or an error dict.

    ## Examples
    Fetch metrics:
        result = await get_database_metrics("production_db")
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        metrics = await connector.get_metrics()
        if metric_names:
            metrics = {k: v for k, v in metrics.items() if k in metric_names}

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
            "error": f"Failed to get metrics: {e!s}",
            "connection_name": connection_name,
            "timestamp": _get_timestamp(),
        }


# DEPRECATED: Use db_management(operation='vacuum_database') instead
async def vacuum_database(connection_name: str, analyze: bool = True, full: bool = False) -> dict[str, Any]:
    """Run VACUUM on a database to optimize storage.

    ## Return Format
    Returns success plus the vacuum result, or an error dict.

    ## Examples
    Vacuum a database:
        result = await vacuum_database("production_db")
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        mode = "full" if full else ("analyze" if analyze else "auto")
        result = await connector.vacuum(mode)

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
            "error": f"VACUUM failed: {e!s}",
            "connection_name": connection_name,
            "timestamp": _get_timestamp(),
        }


# DEPRECATED: Use db_management(operation='disconnect_database') instead
async def disconnect_database(connection_name: str) -> dict[str, Any]:
    """Safely disconnect from a database.

    ## Return Format
    Returns success plus a message, or an error dict.

    ## Examples
    Disconnect:
        result = await disconnect_database("production_db")
    """
    try:
        success = await db_manager.disconnect(connection_name)
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
            "error": f"Failed to disconnect: {e!s}",
            "connection_name": connection_name,
            "timestamp": _get_timestamp(),
        }
