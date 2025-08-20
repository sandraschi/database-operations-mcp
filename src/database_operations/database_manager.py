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

# Export commonly used classes and types
__all__ = [
    'BaseDatabaseConnector',
    'DatabaseType',
    'ConnectionStatus',
    'QueryResult',
    'DatabaseError',
    'ConnectionError',
    'QueryError'
]
