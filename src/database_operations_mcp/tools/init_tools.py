"""
Database initialization and management tools.

Provides tools for initializing, configuring, and managing database connections.
"""

from typing import Dict, Any, Optional, List, Callable

# Import the global MCP instance
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.services.database.connectors import (
    SQLiteConnector,
    PostgreSQLConnector,
    MongoDBConnector,
    ChromaDBConnector
)
from database_operations_mcp.tools.help_tools import HelpSystem
import logging

logger = logging.getLogger(__name__)

# Active database connections
DATABASE_CONNECTIONS: Dict[str, Any] = {}

# Register tools using the @mcp.tool decorator
# The mcp instance is imported from the centralized config

@mcp.tool()
@HelpSystem.register_tool(category='database')
async def init_database(
    db_type: str, 
    connection_params: Dict[str, Any],
    connection_name: str = "default"
) -> Dict[str, Any]:
    """Initialize a new database connection.
    
    Args:
        db_type: Type of database ('sqlite', 'postgresql', 'mongodb', 'chromadb')
        connection_params: Connection parameters specific to the database type
        connection_name: Name to give this connection (default: 'default')
        
    Returns:
        Dictionary with connection status and details
    """
    connectors = {
        'sqlite': SQLiteConnector,
        'postgresql': PostgreSQLConnector,
        'mongodb': MongoDBConnector,
        'chromadb': ChromaDBConnector
    }
    
    if db_type.lower() not in connectors:
        return {
            'status': 'error',
            'message': f'Unsupported database type: {db_type}'
        }
    
    try:
        # Create a new connection
        connector = connectors[db_type.lower()](**connection_params)
        await connector.connect()
        
        # Store the connection
        DATABASE_CONNECTIONS[connection_name] = {
            'type': db_type,
            'connection': connector,
            'params': connection_params
        }
        
        return {
            'status': 'success',
            'message': f'Successfully connected to {db_type} database',
            'connection_name': connection_name,
            'db_type': db_type
        }
    except Exception as e:
        logger.error(f"Error initializing {db_type} database: {e}")
        return {
            'status': 'error',
            'message': f'Failed to initialize database: {str(e)}'
        }

@mcp.tool()
@HelpSystem.register_tool(category='database')
async def list_connections() -> Dict[str, Any]:
    """List all active database connections.
    
    Returns:
        Dictionary with list of active connections and their status
    """
    connections = []
    for name, conn_info in DATABASE_CONNECTIONS.items():
        try:
            is_connected = await conn_info['connection'].is_connected()
            connections.append({
                'name': name,
                'type': conn_info['type'],
                'status': 'connected' if is_connected else 'disconnected',
                'params': conn_info['params']
            })
        except Exception as e:
            logger.error(f"Error checking connection {name}: {e}")
            connections.append({
                'name': name,
                'type': conn_info['type'],
                'status': 'error',
                'error': str(e)
            })
    
    return {
        'status': 'success',
        'connections': connections,
        'total_connections': len(connections)
    }

@mcp.tool()
@HelpSystem.register_tool(category='database')
async def close_connection(connection_name: str) -> Dict[str, Any]:
    """Close a database connection.
    
    Args:
        connection_name: Name of the connection to close
        
    Returns:
        Dictionary with operation status
    """
    if connection_name in DATABASE_CONNECTIONS:
        try:
            if hasattr(DATABASE_CONNECTIONS[connection_name]['connection'], 'close'):
                await DATABASE_CONNECTIONS[connection_name]['connection'].close()
            del DATABASE_CONNECTIONS[connection_name]
            return {
                'status': 'success',
                'message': f'Closed connection: {connection_name}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error closing connection: {str(e)}'
            }
    return {
        'status': 'error',
        'message': f'No such connection: {connection_name}'
    }

@mcp.tool()
@HelpSystem.register_tool(category='database')
async def test_connection(connection_name: str) -> Dict[str, Any]:
    """Test a database connection.
    
    Args:
        connection_name: Name of the connection to test
        
    Returns:
        Dictionary with test results
    """
    if connection_name not in DATABASE_CONNECTIONS:
        return {
            'status': 'error',
            'message': f'No such connection: {connection_name}'
        }
    
    try:
        is_connected = await DATABASE_CONNECTIONS[connection_name]['connection'].is_connected()
        return {
            'status': 'success',
            'connection_name': connection_name,
            'is_connected': is_connected,
            'message': 'Connection is active' if is_connected else 'Connection is not active'
        }
    except Exception as e:
        return {
            'status': 'error',
            'connection_name': connection_name,
            'message': f'Error testing connection: {str(e)}'
        }

@mcp.tool()
@HelpSystem.register_tool(category='database')
async def get_connection_info(connection_name: str) -> Dict[str, Any]:
    """Get information about a database connection.
    
    Args:
        connection_name: Name of the connection to get info for
        
    Returns:
        Dictionary with connection information
    """
    if connection_name not in DATABASE_CONNECTIONS:
        return {
            'status': 'error',
            'message': f'No such connection: {connection_name}'
        }
    
    conn_info = DATABASE_CONNECTIONS[connection_name]
    try:
        is_connected = await conn_info['connection'].is_connected()
        return {
            'status': 'success',
            'connection_name': connection_name,
            'db_type': conn_info['type'],
            'is_connected': is_connected,
            'params': conn_info['params'],
            'connection_info': await conn_info['connection'].get_connection_info()
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error getting connection info: {str(e)}',
            'connection_name': connection_name,
            'db_type': conn_info['type']
        }
