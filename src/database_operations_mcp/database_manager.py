"""
Database Manager Module.

Defines the base database connector interface and common functionality
for all database connectors in the application.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union
from dataclasses import dataclass
from datetime import datetime
import logging

# Type variable for the connection type
T = TypeVar('T')

class DatabaseType(str, Enum):
    """Supported database types."""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    CHROMADB = "chromadb"

class ConnectionStatus(str, Enum):
    """Connection status enumeration."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class QueryResult:
    """Container for query results."""
    success: bool
    data: List[Dict[str, Any]]
    columns: Optional[List[str]] = None
    rowcount: int = 0
    message: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class DatabaseError(Exception):
    """Base exception for database-related errors."""
    pass

class ConnectionError(DatabaseError):
    """Raised when a database connection fails."""
    pass

class QueryError(DatabaseError):
    """Raised when a database query fails."""
    pass

class BaseDatabaseConnector(ABC, Generic[T]):
    """
    Abstract base class for all database connectors.
    
    This class defines the common interface that all database connectors
    must implement to be used with the database operations MCP.
    """
    
    def __init__(self, connection_config: Dict[str, Any]):
        """Initialize the database connector with connection configuration."""
        self.connection_config = connection_config
        self.connection: Optional[T] = None
        self.status: ConnectionStatus = ConnectionStatus.DISCONNECTED
        self.last_error: Optional[str] = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    @abstractmethod
    def database_type(self) -> DatabaseType:
        """Return the type of the database this connector handles."""
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish a connection to the database."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close the database connection."""
        pass
    
    @abstractmethod
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> QueryResult:
        """Execute a query and return the results."""
        pass
    
    @abstractmethod
    async def get_schema(self, **kwargs: Any) -> Dict[str, Any]:
        """Get the database schema."""
        pass
    
    @abstractmethod
    async def get_tables(self, **kwargs: Any) -> List[str]:
        """Get list of tables in the database."""
        pass
    
    @abstractmethod
    async def get_table_schema(self, table_name: str, **kwargs: Any) -> Dict[str, Any]:
        """Get schema information for a specific table."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the database connection."""
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if the connector is currently connected to the database."""
        return self.status == ConnectionStatus.CONNECTED and self.connection is not None
    
    def _handle_error(self, error: Exception, error_message: str) -> None:
        """Handle database errors consistently."""
        self.status = ConnectionStatus.ERROR
        self.last_error = str(error)
        self.logger.error(f"{error_message}: {error}", exc_info=True)
        raise DatabaseError(f"{error_message}: {error}") from error
    
    def __str__(self) -> str:
        """String representation of the connector."""
        return f"{self.__class__.__name__}(status={self.status}, database={self.database_type})"


class DatabaseManager:
    """Centralized database connection manager."""
    
    def __init__(self):
        self.connectors: Dict[str, BaseDatabaseConnector] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def register_connector(self, name: str, connector: BaseDatabaseConnector) -> bool:
        """Register a database connector."""
        try:
            self.connectors[name] = connector
            self.logger.info(f"Registered connector: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register connector {name}: {e}")
            return False
    
    def get_connector(self, name: str) -> Optional[BaseDatabaseConnector]:
        """Get a registered connector by name."""
        return self.connectors.get(name)
    
    def list_connectors(self) -> Dict[str, Dict[str, Any]]:
        """List all registered connectors."""
        result = {}
        for name, connector in self.connectors.items():
            result[name] = {
                "name": name,
                "type": connector.database_type,
                "status": connector.status,
                "connected": connector.is_connected
            }
        return result
    
    def test_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Test all registered connections."""
        results = {}
        for name, connector in self.connectors.items():
            try:
                # Basic test - check if connector exists and status
                results[name] = {
                    "success": connector.is_connected,
                    "status": connector.status,
                    "type": connector.database_type,
                    "error": connector.last_error
                }
            except Exception as e:
                results[name] = {
                    "success": False,
                    "error": str(e),
                    "type": connector.database_type if hasattr(connector, 'database_type') else 'unknown'
                }
        return results


def get_supported_databases() -> List[Dict[str, Any]]:
    """Get list of supported database types."""
    return [
        {
            "type": DatabaseType.SQLITE,
            "name": "SQLite",
            "category": "File-based",
            "description": "Lightweight file-based SQL database"
        },
        {
            "type": DatabaseType.POSTGRESQL,
            "name": "PostgreSQL", 
            "category": "SQL Server",
            "description": "Advanced open-source relational database"
        },
        {
            "type": DatabaseType.MONGODB,
            "name": "MongoDB",
            "category": "NoSQL",
            "description": "Document-oriented NoSQL database"
        },
        {
            "type": DatabaseType.CHROMADB,
            "name": "ChromaDB",
            "category": "Vector",
            "description": "Vector database for embeddings and AI applications"
        }
    ]


def create_connector(database_type: str, connection_config: Dict[str, Any]) -> Optional[BaseDatabaseConnector]:
    """Create a database connector instance."""
    from .services.database.connectors import get_connector_class
    
    try:
        connector_class = get_connector_class(database_type)
        if not connector_class:
            logging.error(f"Unsupported database type: {database_type}")
            return None
        
        # Create and return the connector instance
        connector = connector_class(connection_config)
        logging.info(f"Created connector for {database_type}")
        return connector
        
    except Exception as e:
        logging.error(f"Failed to create connector for {database_type}: {e}")
        return None


# Global instance
db_manager = DatabaseManager()

# Export commonly used classes and types
__all__ = [
    'BaseDatabaseConnector',
    'DatabaseType',
    'ConnectionStatus',
    'QueryResult',
    'DatabaseError',
    'ConnectionError',
    'QueryError',
    'DatabaseManager',
    'db_manager',
    'get_supported_databases',
    'create_connector'
]
