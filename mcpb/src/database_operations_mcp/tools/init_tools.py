"""
Database initialization and management tools.

DEPRECATED: This module is deprecated. Use db_connection portmanteau tool instead.

All operations have been consolidated into db_connection():
- init_database() → db_connection(operation='init')
- list_connections() → db_connection(operation='list')
- close_connection() → db_connection(operation='close')
- test_connection() → db_connection(operation='test')
- get_connection_info() → db_connection(operation='get_info')
- restore_saved_connections() → db_connection(operation='restore')
- set_active_connection() → db_connection(operation='set_active')
- get_active_connection() → db_connection(operation='get_active')
- get_user_preferences() → db_connection(operation='get_preferences')
- set_user_preferences() → db_connection(operation='set_preferences')

This module is kept for backwards compatibility but tools are no longer registered.
"""

import logging
from typing import Any

# NOTE: @mcp.tool decorators removed - functionality moved to db_connection portmanteau
# Import kept for backwards compatibility in case code references these functions
from database_operations_mcp.services.database.connectors import (
    ChromaDBConnector,
    MongoDBConnector,
    PostgreSQLConnector,
    SQLiteConnector,
)

logger = logging.getLogger(__name__)

# Active database connections (legacy, use db_manager instead)
DATABASE_CONNECTIONS: dict[str, Any] = {}


# DEPRECATED: Use db_connection(operation='init') instead
async def init_database(
    db_type: str, connection_params: dict[str, Any], connection_name: str = "default"
) -> dict[str, Any]:
    """Initialize new database connection and register it.

    Creates and registers a new database connection for SQL, NoSQL, or Vector
    databases. The connection is tested and stored for use with other tools.

    Parameters:
        db_type: Type of database to connect to
            - 'sqlite': SQLite database file
            - 'postgresql': PostgreSQL server
            - 'mongodb': MongoDB server
            - 'chromadb': ChromaDB vector database

        connection_params: Database-specific connection parameters
            - SQLite: {'database': '/path/to/file.db'}
            - PostgreSQL: {'host': 'localhost', 'port': 5432, 'user': 'admin',
              'password': 'pwd', 'database': 'mydb'}
            - MongoDB: {'host': 'localhost', 'port': 27017, 'database': 'mydb'}
            - ChromaDB: {'path': '/path/to/chroma', 'collection': 'mycoll'}

        connection_name: Unique name for this connection (default: "default")
            - Must be unique across all connections
            - Alphanumeric and underscores only
            - Used to reference connection in other tools

    Returns:
        Dictionary containing:
            - status: 'success' or 'error'
            - message: Human-readable status message
            - connection_name: Name of registered connection
            - db_type: Type of database connected
            - error: Error details if status is 'error'

    Usage:
        Use this as first step before any database operations. It establishes
        the connection and makes it available to all other database tools.

        Common scenarios:
        - Connect to new database for first time
        - Create multiple named connections
        - Switch between dev/staging/prod databases
        - Initialize connections at server startup

        Best practices:
        - Use descriptive connection names
        - Test connection after initialization
        - Store connection params securely
        - Use different names for different environments

    Examples:
        Initialize SQLite connection:
            result = await init_database(
                db_type="sqlite",
                connection_params={"database": "C:/data/app.db"},
                connection_name="local_db"
            )
            # Returns: {
            #     'status': 'success',
            #     'message': 'Successfully connected to sqlite database',
            #     'connection_name': 'local_db',
            #     'db_type': 'sqlite'
            # }

        Initialize PostgreSQL connection:
            result = await init_database(
                db_type="postgresql",
                connection_params={
                    "host": "db.example.com",
                    "port": 5432,
                    "user": "admin",
                    "password": "secret",
                    "database": "production"
                },
                connection_name="prod_postgres"
            )
            # Returns: Connection established and registered as 'prod_postgres'

        Initialize MongoDB connection:
            result = await init_database(
                db_type="mongodb",
                connection_params={
                    "host": "localhost",
                    "port": 27017,
                    "database": "myapp"
                },
                connection_name="mongo_main"
            )
            # Returns: MongoDB connection ready

        Error handling:
            result = await init_database(
                db_type="postgresql",
                connection_params={"host": "invalid.server"},
                connection_name="bad_conn"
            )
            if result['status'] == 'error':
                print(f"Connection failed: {result['message']}")
            # Logs: Connection failed: Failed to initialize database: Connection refused

    Notes:
        - Connection is tested before registration
        - Failed connections are not registered
        - Duplicate connection names overwrite previous
        - Connection params stored in memory (not persistent)
        - SSL/TLS params can be included in connection_params

    See Also:
        - list_connections: View all registered connections
        - test_connection: Verify connection health
        - close_connection: Properly close connections
    """
    connectors = {
        "sqlite": SQLiteConnector,
        "postgresql": PostgreSQLConnector,
        "mongodb": MongoDBConnector,
        "chromadb": ChromaDBConnector,
    }

    if db_type.lower() not in connectors:
        return {"status": "error", "message": f"Unsupported database type: {db_type}"}

    try:
        # Create a new connection
        connector = connectors[db_type.lower()](**connection_params)
        await connector.connect()

        # Store the connection in memory
        DATABASE_CONNECTIONS[connection_name] = {
            "type": db_type,
            "connection": connector,
            "params": connection_params,
        }

        # Save connection config to persistent storage (without password)
        try:
            from database_operations_mcp.storage.persistence import get_storage

            storage = get_storage()
            if storage:
                await storage.save_connection(connection_name, db_type, connection_params)
                logger.info(f"Saved connection '{connection_name}' to persistent storage")
        except Exception as storage_error:
            # Storage might not be initialized yet - that's ok
            logger.debug(f"Could not save to storage: {storage_error}")

        return {
            "status": "success",
            "message": f"Successfully connected to {db_type} database",
            "connection_name": connection_name,
            "db_type": db_type,
        }
    except Exception as e:
        logger.error(f"Error initializing {db_type} database: {e}")
        return {"status": "error", "message": f"Failed to initialize database: {str(e)}"}


# DEPRECATED: Use db_connection(operation='list') instead
async def list_connections() -> dict[str, Any]:
    """List all active database connections with status.

    Retrieves complete list of registered database connections along with their
    current status and configuration. Useful for monitoring and managing multiple
    database connections.

    Parameters:
        None

    Returns:
        Dictionary containing:
            - status: 'success' (always succeeds)
            - connections: List of connection dictionaries with:
                - name: Connection name
                - type: Database type
                - status: 'connected', 'disconnected', or 'error'
                - params: Connection parameters
                - error: Error message if status is 'error'
            - total_connections: Count of registered connections

    Usage:
        Use this to view all database connections and their health status.
        Essential for connection management and troubleshooting.

        Common scenarios:
        - View all available connections
        - Check connection health
        - Audit active database sessions
        - Troubleshoot connection issues

        Best practices:
        - Run periodically to check connection health
        - Use before other operations to verify connections
        - Monitor for unexpected disconnections

    Examples:
        List all connections:
            result = await list_connections()
            # Returns: {
            #     'status': 'success',
            #     'connections': [
            #         {
            #             'name': 'prod_db',
            #             'type': 'postgresql',
            #             'status': 'connected',
            #             'params': {'host': 'db.example.com', 'port': 5432}
            #         },
            #         {
            #             'name': 'local_sqlite',
            #             'type': 'sqlite',
            #             'status': 'connected',
            #             'params': {'database': 'app.db'}
            #         }
            #     ],
            #     'total_connections': 2
            # }

        Check if specific connection exists:
            result = await list_connections()
            conn_names = [c['name'] for c in result['connections']]
            if 'prod_db' in conn_names:
                print("Production database is registered")

        Find disconnected connections:
            result = await list_connections()
            disconnected = [c['name'] for c in result['connections'] if c['status'] != 'connected']
            if disconnected:
                print(f"Disconnected: {disconnected}")

    Notes:
        - Always returns success (even if no connections)
        - Connection params may contain sensitive info
        - Status checked at call time (may change)
        - Empty list returned if no connections

    See Also:
        - init_database: Create new connections
        - test_connection: Test specific connection
        - close_connection: Close connections
    """
    connections = []
    for name, conn_info in DATABASE_CONNECTIONS.items():
        try:
            is_connected = await conn_info["connection"].is_connected()
            connections.append(
                {
                    "name": name,
                    "type": conn_info["type"],
                    "status": "connected" if is_connected else "disconnected",
                    "params": conn_info["params"],
                }
            )
        except Exception as e:
            logger.error(f"Error checking connection {name}: {e}")
            connections.append(
                {"name": name, "type": conn_info["type"], "status": "error", "error": str(e)}
            )

    return {"status": "success", "connections": connections, "total_connections": len(connections)}


# DEPRECATED: Use db_connection(operation='restore') instead
async def restore_saved_connections(auto_reconnect: bool = False) -> dict[str, Any]:
    """Restore saved database connections from persistent storage.

    Lists all saved connection configurations and optionally reconnects automatically.
    Connections are restored from persistent storage that survives Claude Desktop
    and OS restarts.

    Parameters:
        auto_reconnect: If True, automatically reconnect to saved connections
                       (DEV MODE: Only works if ENABLE_PASSWORD_STORAGE=1)

    Returns:
        Dictionary containing:
            - status: 'success' or 'error'
            - saved_connections: List of saved connection configurations
            - reconnected: List of connection names that were reconnected
            - message: Status message

    Usage:
        Use this after server restart to see saved connections and reconnect.

        DEV MODE (ENABLE_PASSWORD_STORAGE=1):
        - Passwords are saved, so auto_reconnect=True will restore automatically

        PRODUCTION MODE:
        - Passwords not saved, use init_database() manually with password

    Examples:
        List saved connections:
            result = await restore_saved_connections()
            # Returns saved connection configs

        Auto-reconnect (dev mode only):
            result = await restore_saved_connections(auto_reconnect=True)
            # Automatically reconnects if passwords were saved
    """
    try:
        from database_operations_mcp.storage.persistence import get_storage

        storage = get_storage()
        if not storage:
            return {
                "status": "error",
                "message": "Persistent storage not available",
                "saved_connections": [],
                "reconnected": [],
            }

        saved_connections = await storage.get_all_connections()
        reconnected = []

        # DEV MODE: Auto-reconnect if passwords are saved
        if auto_reconnect:
            import os

            enable_password_storage = os.getenv("ENABLE_PASSWORD_STORAGE", "0").lower() in (
                "1",
                "true",
                "yes",
            )

            if enable_password_storage:
                for conn_name, conn_info in saved_connections.items():
                    try:
                        # Check if password is present (dev mode)
                        params = conn_info.get("params", {})
                        if "password" in params:
                            # Auto-reconnect using saved password
                            result = await init_database(
                                db_type=conn_info["type"],
                                connection_params=params,
                                connection_name=conn_name,
                            )
                            if result.get("status") == "success":
                                reconnected.append(conn_name)
                                logger.info(f"Auto-reconnected to {conn_name} (dev mode)")
                    except Exception as e:
                        logger.error(f"Failed to auto-reconnect {conn_name}: {e}")
            else:
                logger.warning(
                    "auto_reconnect=True but ENABLE_PASSWORD_STORAGE not set. "
                    "Passwords not saved, cannot auto-reconnect."
                )

        return {
            "status": "success",
            "saved_connections": saved_connections,
            "reconnected": reconnected,
            "message": f"Found {len(saved_connections)} saved connections, "
            f"reconnected {len(reconnected)}",
        }
    except Exception as e:
        logger.error(f"Error restoring saved connections: {e}")
        return {
            "status": "error",
            "message": f"Failed to restore: {str(e)}",
            "saved_connections": [],
            "reconnected": [],
        }


# DEPRECATED: Use db_connection(operation='close') instead
async def close_connection(connection_name: str) -> dict[str, Any]:
    """Close database connection and release resources.

    Properly closes database connection and removes it from active connections.
    Frees database resources and connection pool slots.

    Parameters:
        connection_name: Name of connection to close
            - Must be previously registered
            - Case-sensitive

    Returns:
        Dictionary containing:
            - status: 'success' or 'error'
            - message: Human-readable result
            - connection_name: Name of closed connection

    Usage:
        Use this to properly close connections when done or to free resources.
        Important for avoiding connection leaks and resource exhaustion.

        Common scenarios:
        - Clean up after batch operations
        - Free resources when switching databases
        - Close before application shutdown
        - Remove failed connections

        Best practices:
        - Always close connections when done
        - Close before server shutdown
        - Don't close connections still in use

    Examples:
        Close specific connection:
            result = await close_connection("temp_db")
            # Returns: {
            #     'status': 'success',
            #     'message': 'Closed connection: temp_db'
            # }

        Error handling:
            result = await close_connection("nonexistent")
            if result['status'] == 'error':
                print(f"Failed: {result['message']}")
            # Logs: Failed: No such connection: nonexistent

    Notes:
        - Connection is removed from active list
        - Cannot use connection after closing
        - Safe to call on already closed connections
        - Resources released immediately

    See Also:
        - init_database: Create connections
        - list_connections: View active connections
    """
    if connection_name in DATABASE_CONNECTIONS:
        try:
            if hasattr(DATABASE_CONNECTIONS[connection_name]["connection"], "close"):
                await DATABASE_CONNECTIONS[connection_name]["connection"].close()
            del DATABASE_CONNECTIONS[connection_name]

            # Remove from persistent storage
            try:
                from database_operations_mcp.storage.persistence import get_storage

                storage = get_storage()
                if storage:
                    await storage.delete_connection(connection_name)
            except Exception:
                pass  # Graceful degradation

            return {"status": "success", "message": f"Closed connection: {connection_name}"}
        except Exception as e:
            return {"status": "error", "message": f"Error closing connection: {str(e)}"}
    return {"status": "error", "message": f"No such connection: {connection_name}"}


# DEPRECATED: Use db_connection(operation='test') instead
async def test_connection(connection_name: str) -> dict[str, Any]:
    """Test database connection health and responsiveness.

    Verifies that database connection is active and responsive by checking
    connection status. Quick health check for troubleshooting.

    Parameters:
        connection_name: Name of connection to test
            - Must be previously registered
            - Case-sensitive

    Returns:
        Dictionary containing:
            - status: 'success' or 'error'
            - connection_name: Name of tested connection
            - is_connected: Boolean connection status
            - message: Human-readable status message

    Usage:
        Use this for quick connection health checks and troubleshooting.

        Common scenarios:
        - Verify connection before operations
        - Troubleshoot connection issues
        - Monitor connection health
        - Test after connection problems

    Examples:
        Test connection health:
            result = await test_connection("prod_db")
            # Returns: {
            #     'status': 'success',
            #     'connection_name': 'prod_db',
            #     'is_connected': True,
            #     'message': 'Connection is active'
            # }

        Handle connection errors:
            result = await test_connection("prod_db")
            if not result.get('is_connected'):
                print("Connection down, reinitializing...")
                await init_database(...)

    Notes:
        - Quick check, does not run queries
        - Does not reconnect if disconnected
        - Use for health monitoring

    See Also:
        - init_database: Initialize connections
        - list_connections: View all connections
    """
    if connection_name not in DATABASE_CONNECTIONS:
        return {"status": "error", "message": f"No such connection: {connection_name}"}

    try:
        is_connected = await DATABASE_CONNECTIONS[connection_name]["connection"].is_connected()
        return {
            "status": "success",
            "connection_name": connection_name,
            "is_connected": is_connected,
            "message": "Connection is active" if is_connected else "Connection is not active",
        }
    except Exception as e:
        return {
            "status": "error",
            "connection_name": connection_name,
            "message": f"Error testing connection: {str(e)}",
        }


# DEPRECATED: Use db_connection(operation='get_info') instead
async def get_connection_info(connection_name: str) -> dict[str, Any]:
    """Get detailed information about registered database connection.

    Retrieves comprehensive details about a registered connection including
    configuration, status, and metadata. Useful for debugging and auditing.

    Parameters:
        connection_name: Name of connection to inspect
            - Must be previously registered
            - Case-sensitive

    Returns:
        Dictionary containing:
            - status: 'success' or 'error'
            - connection_name: Name of connection
            - db_type: Type of database
            - is_connected: Boolean connection status
            - params: Connection parameters
            - connection_info: Database-specific metadata
            - message: Error message if status is 'error'

    Usage:
        Use this to get detailed connection information for debugging,
        auditing, or understanding connection configuration.

        Common scenarios:
        - Debug connection issues
        - Audit connection configurations
        - Verify connection parameters
        - Document active connections

    Examples:
        Get connection details:
            result = await get_connection_info("prod_postgres")
            # Returns: {
            #     'status': 'success',
            #     'connection_name': 'prod_postgres',
            #     'db_type': 'postgresql',
            #     'is_connected': True,
            #     'params': {
            #         'host': 'db.example.com',
            #         'port': 5432,
            #         'database': 'production'
            #     },
            #     'connection_info': {
            #         'server_version': 'PostgreSQL 14.5',
            #         'connection_id': 12345
            #     }
            # }

        Error handling:
            result = await get_connection_info("unknown")
            if result['status'] == 'error':
                print(f"Not found: {result['message']}")
            # Logs: Not found: No such connection: unknown

    Notes:
        - Returns sensitive connection params
        - Does not test connectivity (use test_connection)
        - Shows configuration at registration time

    See Also:
        - list_connections: View all connections
        - test_connection: Test connection health
    """
    if connection_name not in DATABASE_CONNECTIONS:
        return {"status": "error", "message": f"No such connection: {connection_name}"}

    conn_info = DATABASE_CONNECTIONS[connection_name]
    try:
        is_connected = await conn_info["connection"].is_connected()
        return {
            "status": "success",
            "connection_name": connection_name,
            "db_type": conn_info["type"],
            "is_connected": is_connected,
            "params": conn_info["params"],
            "connection_info": await conn_info["connection"].get_connection_info(),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting connection info: {str(e)}",
            "connection_name": connection_name,
            "db_type": conn_info["type"],
        }


# DEPRECATED: Use db_connection(operation='set_active') instead
async def set_active_connection(connection_name: str) -> dict[str, Any]:
    """Set the active/default database connection.

    Stores the connection name as the active/default connection in persistent
    storage. This preference survives Claude Desktop and OS restarts.

    Parameters:
        connection_name: Name of connection to set as active
            - Must be a currently active connection or a saved connection

    Returns:
        Dictionary with status and message

    Examples:
        Set active connection:
            result = await set_active_connection("prod_db")
    """
    try:
        from database_operations_mcp.storage.persistence import get_storage

        storage = get_storage()
        if not storage:
            return {"status": "error", "message": "Persistent storage not available"}

        await storage.set_active_connection(connection_name)
        return {"status": "success", "message": f"Set active connection: {connection_name}"}
    except Exception as e:
        logger.error(f"Error setting active connection: {e}")
        return {"status": "error", "message": f"Failed to set active connection: {str(e)}"}


# DEPRECATED: Use db_connection(operation='get_active') instead
async def get_active_connection() -> dict[str, Any]:
    """Get the active/default database connection name.

    Retrieves the stored active connection preference from persistent storage.

    Returns:
        Dictionary with active connection name or None

    Examples:
        Get active connection:
            result = await get_active_connection()
            # Returns: {'status': 'success', 'active_connection': 'prod_db'}
    """
    try:
        from database_operations_mcp.storage.persistence import get_storage

        storage = get_storage()
        if not storage:
            return {
                "status": "error",
                "message": "Persistent storage not available",
                "active_connection": None,
            }

        active_conn = await storage.get_active_connection()
        return {"status": "success", "active_connection": active_conn}
    except Exception as e:
        logger.error(f"Error getting active connection: {e}")
        return {
            "status": "error",
            "message": f"Failed to get active connection: {str(e)}",
            "active_connection": None,
        }


# DEPRECATED: Use db_connection(operation='get_preferences') instead
async def get_user_preferences() -> dict[str, Any]:
    """Get user preferences from persistent storage.

    Retrieves all user preferences including query limits, page sizes,
    display settings, etc. Preferences survive Claude Desktop and OS restarts.

    Returns:
        Dictionary with all user preferences

    Examples:
        Get preferences:
            result = await get_user_preferences()
            # Returns: {
            #     'default_query_limit': 50,
            #     'default_page_size': 20,
            #     ...
            # }
    """
    try:
        from database_operations_mcp.storage.persistence import get_storage

        storage = get_storage()
        if not storage:
            return {
                "status": "error",
                "message": "Persistent storage not available",
                "preferences": {},
            }

        prefs = await storage.get_user_preferences()
        return {"status": "success", "preferences": prefs}
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        return {
            "status": "error",
            "message": f"Failed to get preferences: {str(e)}",
            "preferences": {},
        }


# DEPRECATED: Use db_connection(operation='set_preferences') instead
async def set_user_preferences(preferences: dict[str, Any]) -> dict[str, Any]:
    """Set user preferences in persistent storage.

    Stores user preferences that survive Claude Desktop and OS restarts.
    Common preferences include:
    - default_query_limit: Default limit for queries
    - default_page_size: Default page size for pagination
    - show_metadata: Whether to show metadata in results
    - sort_order: Default sort order

    Parameters:
        preferences: Dictionary of preference key-value pairs

    Returns:
        Dictionary with status

    Examples:
        Set preferences:
            result = await set_user_preferences({
                "default_query_limit": 50,
                "default_page_size": 20,
                "show_metadata": True
            })
    """
    try:
        from database_operations_mcp.storage.persistence import get_storage

        storage = get_storage()
        if not storage:
            return {"status": "error", "message": "Persistent storage not available"}

        await storage.set_user_preferences(preferences)
        return {"status": "success", "message": "Preferences saved"}
    except Exception as e:
        logger.error(f"Error setting preferences: {e}")
        return {"status": "error", "message": f"Failed to set preferences: {str(e)}"}
