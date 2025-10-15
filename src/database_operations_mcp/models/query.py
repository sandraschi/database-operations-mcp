"""Query and result models for database operations."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseDBModel


class QueryType(str, Enum):
    """Types of database queries."""

    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    ALTER = "alter"
    DROP = "drop"
    RAW = "raw"
    AGGREGATE = "aggregate"
    TRANSACTION = "transaction"


class QueryStatus(str, Enum):
    """Query execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueryResult(BaseDBModel):
    """Result of a database query."""

    query_id: str
    status: QueryStatus = QueryStatus.PENDING
    data: List[Dict[str, Any]] = Field(default_factory=list)
    columns: Optional[List[str]] = None
    rowcount: int = 0
    execution_time: Optional[float] = None  # in seconds
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DatabaseQuery(BaseDBModel):
    """Database query model."""

    query: str
    query_type: QueryType
    parameters: Optional[Dict[str, Any]] = None
    connection_id: str
    status: QueryStatus = QueryStatus.PENDING
    result: Optional[QueryResult] = None
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        use_enum_values = True

    def start_execution(self) -> None:
        """Mark query as started."""
        self.status = QueryStatus.RUNNING
        self.executed_at = datetime.utcnow()

    def complete(self, result: QueryResult) -> None:
        """Mark query as completed with results."""
        self.status = QueryStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.result = result

    def fail(self, error: str) -> None:
        """Mark query as failed with error."""
        self.status = QueryStatus.FAILED
        self.completed_at = datetime.utcnow()
        if not self.result:
            self.result = QueryResult(query_id=self.id or "")
        self.result.status = QueryStatus.FAILED
        self.result.error = error
