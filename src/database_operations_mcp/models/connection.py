"""Database connection models."""
from typing import Dict, List, Optional, Union
from enum import Enum
from datetime import datetime
from pydantic import Field, validator

from .base import BaseDBModel

class DatabaseType(str, Enum):
    """Supported database types."""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    CHROMADB = "chromadb"
    INFLUXDB = "influxdb"
    NEO4J = "neo4j"
    ELASTICSEARCH = "elasticsearch"
    REDIS = "redis"
    CASSANDRA = "cassandra"

class ConnectionStatus(str, Enum):
    """Connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class ConnectionConfig(BaseDBModel):
    """Database connection configuration."""
    name: str
    db_type: DatabaseType
    host: str = "localhost"
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic config."""
        use_enum_values = True
        
    @validator('port', always=True)
    def set_default_port(cls, v, values):
        """Set default port based on database type."""
        if v is not None:
            return v
            
        db_type = values.get('db_type')
        if db_type == DatabaseType.POSTGRESQL:
            return 5432
        elif db_type == DatabaseType.MONGODB:
            return 27017
        elif db_type == DatabaseType.INFLUXDB:
            return 8086
        elif db_type == DatabaseType.NEO4J:
            return 7687
        elif db_type == DatabaseType.ELASTICSEARCH:
            return 9200
        elif db_type == DatabaseType.REDIS:
            return 6379
        elif db_type == DatabaseType.CASSANDRA:
            return 9042
        return None

class ConnectionInfo(BaseDBModel):
    """Connection information with status."""
    config: ConnectionConfig
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    last_used: Optional[datetime] = None
    error: Optional[str] = None
    stats: Dict[str, Any] = Field(default_factory=dict)
