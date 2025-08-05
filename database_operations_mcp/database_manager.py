"""
Database abstraction layer for universal database operations.

Provides a unified interface across all supported database types:
- Traditional SQL: PostgreSQL, MySQL, SQLite, SQL Server
- NoSQL: MongoDB, Redis
- Vector: ChromaDB, Pinecone
- Time Series: InfluxDB
- Graph: Neo4j
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    SQLSERVER = "sqlserver"
    MONGODB = "mongodb"
    REDIS = "redis"
    CHROMADB = "chromadb"
    PINECONE = "pinecone"
    INFLUXDB = "influxdb"
    NEO4J = "neo4j"

class ConnectionStatus(Enum):
    """Database connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    UNKNOWN = "unknown"

class DatabaseError(Exception):
    """Base exception for database operations."""
    pass

class ConnectionError(DatabaseError):
    """Database connection errors."""
    pass

class QueryError(DatabaseError):
    """Query execution errors."""
    pass

class SchemaError(DatabaseError):
    """Schema operation errors."""
    pass

class BaseDatabaseConnector(ABC):
    """Abstract base class for all database connectors."""
    
    def __init__(self, connection_config: Dict[str, Any]):
        """Initialize connector with connection configuration."""
        self.config = connection_config
        self.connection = None
        self.status = ConnectionStatus.DISCONNECTED
        self.last_error = None
    
    @property
    @abstractmethod
    def database_type(self) -> DatabaseType:
        """Return the database type this connector handles."""
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Test database connectivity."""
        pass
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Close database connection."""
        pass
    
    @abstractmethod
    def list_databases(self) -> List[Dict[str, Any]]:
        """List available databases."""
        pass
    
    @abstractmethod
    def list_tables(self, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tables/collections in database."""
        pass
    
    @abstractmethod
    def describe_table(self, table_name: str, database: Optional[str] = None) -> Dict[str, Any]:
        """Get table schema and metadata."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute query and return results."""
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics."""
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        pass
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection information."""
        return {
            "database_type": self.database_type.value,
            "status": self.status.value,
            "config": {k: v for k, v in self.config.items() if k not in ['password', 'api_key', 'secret']},
            "last_error": self.last_error
        }

class DatabaseManager:
    """Central manager for all database connections and operations."""
    
    def __init__(self):
        """Initialize the database manager."""
        self.connectors: Dict[str, BaseDatabaseConnector] = {}
        self.active_connections: Dict[str, str] = {}  # name -> connector_id
        
    def register_connector(self, name: str, connector: BaseDatabaseConnector) -> bool:
        """Register a database connector."""
        try:
            connector_id = f"{connector.database_type.value}_{name}"
            self.connectors[connector_id] = connector
            logger.info(f"Registered {connector.database_type.value} connector: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register connector {name}: {e}")
            return False
    
    def get_connector(self, name: str) -> Optional[BaseDatabaseConnector]:
        """Get a registered connector by name."""
        return self.connectors.get(name)
    
    def list_connectors(self) -> List[Dict[str, Any]]:
        """List all registered connectors."""
        return [
            {
                "name": name,
                "database_type": connector.database_type.value,
                "status": connector.status.value,
                "config": connector.get_connection_info()["config"]
            }
            for name, connector in self.connectors.items()
        ]
    
    def test_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Test all registered database connections."""
        results = {}
        for name, connector in self.connectors.items():
            try:
                results[name] = connector.test_connection()
            except Exception as e:
                results[name] = {
                    "success": False,
                    "error": str(e),
                    "database_type": connector.database_type.value
                }
        return results

# Global database manager instance
db_manager = DatabaseManager()

def create_connector(database_type: str, connection_config: Dict[str, Any]) -> Optional[BaseDatabaseConnector]:
    """Factory function to create database connectors."""
    try:
        db_type = DatabaseType(database_type.lower())
        
        if db_type == DatabaseType.POSTGRESQL:
            from .connectors.postgresql_connector import PostgreSQLConnector
            return PostgreSQLConnector(connection_config)
        elif db_type == DatabaseType.SQLITE:
            from .connectors.sqlite_connector import SQLiteConnector
            return SQLiteConnector(connection_config)
        elif db_type == DatabaseType.CHROMADB:
            from .connectors.chromadb_connector import ChromaDBConnector
            return ChromaDBConnector(connection_config)
        elif db_type == DatabaseType.MYSQL:
            from .connectors.mysql_connector import MySQLConnector
            return MySQLConnector(connection_config)
        elif db_type == DatabaseType.MONGODB:
            from .connectors.mongodb_connector import MongoDBConnector
            return MongoDBConnector(connection_config)
        elif db_type == DatabaseType.REDIS:
            from .connectors.redis_connector import RedisConnector
            return RedisConnector(connection_config)
        else:
            logger.warning(f"Database type {database_type} not yet implemented")
            return None
            
    except ValueError:
        logger.error(f"Unsupported database type: {database_type}")
        return None
    except ImportError as e:
        logger.error(f"Database connector not available: {e}")
        return None

def get_supported_databases() -> List[Dict[str, Any]]:
    """Get list of supported database types."""
    return [
        {
            "type": db_type.value,
            "name": db_type.value.title(),
            "category": _get_database_category(db_type),
            "description": _get_database_description(db_type)
        }
        for db_type in DatabaseType
    ]

def _get_database_category(db_type: DatabaseType) -> str:
    """Get database category for organization."""
    if db_type in [DatabaseType.POSTGRESQL, DatabaseType.MYSQL, DatabaseType.SQLITE, DatabaseType.SQLSERVER]:
        return "SQL"
    elif db_type in [DatabaseType.CHROMADB, DatabaseType.PINECONE]:
        return "Vector"
    elif db_type in [DatabaseType.MONGODB]:
        return "Document"
    elif db_type in [DatabaseType.REDIS]:
        return "Key-Value"
    elif db_type in [DatabaseType.INFLUXDB]:
        return "Time Series"
    elif db_type in [DatabaseType.NEO4J]:
        return "Graph"
    else:
        return "Other"

def _get_database_description(db_type: DatabaseType) -> str:
    """Get database description."""
    descriptions = {
        DatabaseType.POSTGRESQL: "Advanced open-source relational database",
        DatabaseType.MYSQL: "Popular open-source relational database",
        DatabaseType.SQLITE: "Lightweight embedded SQL database",
        DatabaseType.SQLSERVER: "Microsoft SQL Server enterprise database",
        DatabaseType.MONGODB: "Popular NoSQL document database",
        DatabaseType.REDIS: "In-memory key-value store and cache",
        DatabaseType.CHROMADB: "Vector database for AI embeddings and semantic search",
        DatabaseType.PINECONE: "Cloud-native vector database for AI applications",
        DatabaseType.INFLUXDB: "Time series database for metrics and monitoring",
        DatabaseType.NEO4J: "Graph database for connected data"
    }
    return descriptions.get(db_type, "Database system")
