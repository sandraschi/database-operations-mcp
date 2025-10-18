"""
Database initialization and management tools.

Provides tools for initializing, configuring, and managing database connections.
"""

import logging
from typing import Any, Dict

# Import the global MCP instance
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.services.database.connectors import (
    ChromaDBConnector,
    MongoDBConnector,
    PostgreSQLConnector,
    SQLiteConnector,
)
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)

# Active database connections
DATABASE_CONNECTIONS: Dict[str, Any] = {}

# Register tools using the @mcp.tool decorator
# The mcp instance is imported from the centralized config


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def init_database(
    db_type: str, connection_params: Dict[str, Any], connection_name: str = "default"
) -> Dict[str, Any]:
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

        # Store the connection
        DATABASE_CONNECTIONS[connection_name] = {
            "type": db_type,
            "connection": connector,
            "params": connection_params,
        }

        return {
            "status": "success",
            "message": f"Successfully connected to {db_type} database",
            "connection_name": connection_name,
            "db_type": db_type,
        }
    except Exception as e:
        logger.error(f"Error initializing {db_type} database: {e}")
        return {"status": "error", "message": f"Failed to initialize database: {str(e)}"}


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def list_connections() -> Dict[str, Any]:
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


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def close_connection(connection_name: str) -> Dict[str, Any]:
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
            return {"status": "success", "message": f"Closed connection: {connection_name}"}
        except Exception as e:
            return {"status": "error", "message": f"Error closing connection: {str(e)}"}
    return {"status": "error", "message": f"No such connection: {connection_name}"}


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def test_connection(connection_name: str) -> Dict[str, Any]:
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


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def get_connection_info(connection_name: str) -> Dict[str, Any]:
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
