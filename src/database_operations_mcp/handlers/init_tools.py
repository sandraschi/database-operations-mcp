"""
Database initialization and management tools.

Provides tools for initializing, configuring, and managing database connections.
"""

from typing import Dict, Any, Optional, List
from fastmcp import mcp_tool
from ..services.database.connectors import (
    SQLiteConnector,
    PostgreSQLConnector,
    MongoDBConnector,
    ChromaDBConnector
)
from .help_tools import HelpSystem
import logging

def register_tools(mcp):
    """Register all initialization tools with the MCP server."""
    mcp.tool()(init_database)
    mcp.tool()(list_connections)
    mcp.tool()(close_connection)
    mcp.tool()(init_schema)
    
    logger.info("Registered initialization tools")

logger = logging.getLogger(__name__)

# Active database connections
DATABASE_CONNECTIONS: Dict[str, Any] = {}

@HelpSystem.register_tool
@mcp_tool()
async def init_database(
    db_type: str, 
    connection_params: Dict[str, Any],
    connection_name: str = "default"
) -> Dict[str, Any]:
    """Initialize a database connection.
    
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
    
    if db_type not in connectors:
        return {
            'status': 'error',
            'message': f'Unsupported database type: {db_type}',
            'supported_types': list(connectors.keys())
        }
    
    try:
        connector = connectors[db_type](connection_params)
        connected = await connector.connect()
        
        if connected:
            DATABASE_CONNECTIONS[connection_name] = {
                'connector': connector,
                'type': db_type,
                'params': connection_params
            }
            return {
                'status': 'success',
                'connection': connection_name,
                'type': db_type,
                'message': f'Successfully connected to {db_type} database'
            }
        else:
            return {
                'status': 'error',
                'message': f'Failed to connect to {db_type} database',
                'details': str(connector.last_error)
            }
    except Exception as e:
        logger.exception(f"Error initializing {db_type} database")
        return {
            'status': 'error',
            'message': f'Error initializing {db_type} database',
            'error': str(e)
        }

@HelpSystem.register_tool
@mcp_tool()
async def list_connections() -> Dict[str, Any]:
    """List all active database connections.
    
    Returns:
        Dictionary of active connections with their types and status
    """
    result = {}
    for name, conn in DATABASE_CONNECTIONS.items():
        result[name] = {
            'type': conn['type'],
            'status': 'connected' if conn['connector'].is_connected else 'disconnected',
            'params': {k: '***' if k.lower() in ['password', 'passwd'] else v 
                     for k, v in conn['params'].items()}
        }
    return result

@HelpSystem.register_tool
@mcp_tool()
async def close_connection(connection_name: str) -> Dict[str, Any]:
    """Close a database connection.
    
    Args:
        connection_name: Name of the connection to close
        
    Returns:
        Status of the operation
    """
    if connection_name not in DATABASE_CONNECTIONS:
        return {
            'status': 'error',
            'message': f'No such connection: {connection_name}'
        }
    
    try:
        connector = DATABASE_CONNECTIONS[connection_name]['connector']
        await connector.disconnect()
        DATABASE_CONNECTIONS.pop(connection_name)
        return {
            'status': 'success',
            'message': f'Closed connection: {connection_name}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error closing connection: {str(e)}'
        }

@HelpSystem.register_tool
@mcp_tool()
async def init_schema(
    connection_name: str = "default",
    schema_definition: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Initialize database schema.
    
    Args:
        connection_name: Name of the database connection
        schema_definition: Schema definition (format depends on database type)
        
    Returns:
        Status of schema initialization
    """
    if connection_name not in DATABASE_CONNECTIONS:
        return {
            'status': 'error',
            'message': f'No such connection: {connection_name}'
        }
    
    connector = DATABASE_CONNECTIONS[connection_name]['connector']
    db_type = DATABASE_CONNECTIONS[connection_name]['type']
    
    try:
        if db_type == 'sqlite':
            # Example for SQLite
            if schema_definition and 'tables' in schema_definition:
                for table_def in schema_definition['tables']:
                    await connector.execute_query(table_def['create_statement'])
                return {'status': 'success', 'message': 'Schema initialized'}
            
        elif db_type == 'postgresql':
            # Example for PostgreSQL
            if schema_definition and 'schemas' in schema_definition:
                for schema_def in schema_definition['schemas']:
                    await connector.execute_query(f"CREATE SCHEMA IF NOT EXISTS {schema_def['name']}")
                    for table_def in schema_def.get('tables', []):
                        await connector.execute_query(table_def['create_statement'])
                return {'status': 'success', 'message': 'Schema initialized'}
            
        return {
            'status': 'success',
            'message': 'No schema definition provided, using existing schema',
            'current_schema': await connector.get_schema()
        }
        
    except Exception as e:
        logger.exception(f"Error initializing schema for {db_type}")
        return {
            'status': 'error',
            'message': f'Error initializing schema: {str(e)}'
        }
