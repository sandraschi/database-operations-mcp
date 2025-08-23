"""
Database initialization and management tools.

Provides tools for initializing, configuring, and managing database connections.
"""

from typing import Dict, Any, Optional, List
from fastmcp import FastMCP
from ..services.database.connectors import (
    SQLiteConnector,
    PostgreSQLConnector,
    MongoDBConnector,
    ChromaDBConnector
)
from .help_tools import HelpSystem
import logging

logger = logging.getLogger(__name__)

# Active database connections
DATABASE_CONNECTIONS: Dict[str, Any] = {}

def register_tools(mcp: FastMCP) -> None:
    """Register all initialization tools with the MCP server."""
    
    @mcp.tool()
    @HelpSystem.register_tool
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
                    'details': str(getattr(connector, 'last_error', 'Unknown error'))
                }
        except Exception as e:
            logger.exception(f"Error initializing {db_type} database")
            return {
                'status': 'error',
                'message': f'Error initializing {db_type} database',
                'error': str(e)
            }

    @mcp.tool()
    @HelpSystem.register_tool
    async def list_connections() -> Dict[str, Any]:
        """List all active database connections.
        
        Returns:
            Dictionary of active connections with their types and status
        """
        result = {}
        for name, conn in DATABASE_CONNECTIONS.items():
            result[name] = {
                'type': conn['type'],
                'status': 'connected' if getattr(conn['connector'], 'is_connected', False) else 'disconnected',
                'params': {k: '***' if k.lower() in ['password', 'passwd'] else v 
                         for k, v in conn['params'].items()}
            }
        return {'connections': result}
    
    @mcp.tool()
    @HelpSystem.register_tool
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
            conn = DATABASE_CONNECTIONS[connection_name]
            if hasattr(conn['connector'], 'disconnect'):
                await conn['connector'].disconnect()
            
            del DATABASE_CONNECTIONS[connection_name]
            return {
                'status': 'success',
                'message': f'Successfully closed connection: {connection_name}'
            }
        except Exception as e:
            logger.exception(f"Error closing connection {connection_name}")
            return {
                'status': 'error',
                'message': f'Error closing connection {connection_name}',
                'error': str(e)
            }
    
    @mcp.tool()
    @HelpSystem.register_tool
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
            
        if not schema_definition:
            return {
                'status': 'error',
                'message': 'No schema definition provided'
            }
            
        try:
            conn = DATABASE_CONNECTIONS[connection_name]
            if hasattr(conn['connector'], 'init_schema'):
                result = await conn['connector'].init_schema(schema_definition)
                return {
                    'status': 'success',
                    'message': 'Schema initialized successfully',
                    'result': result
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Database type {conn["type"]} does not support schema initialization'
                }
        except Exception as e:
            logger.exception(f"Error initializing schema for {connection_name}")
            return {
                'status': 'error',
                'message': f'Error initializing schema: {str(e)}'
            }
    
    logger.info("Registered database initialization tools")
