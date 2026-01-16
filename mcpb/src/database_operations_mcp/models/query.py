"""Query and result models for database operations."""

from datetime import datetime
from enum import Enum
from typing import Any

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
    data: list[dict[str, Any]] = Field(default_factory=list)
    columns: list[str] | None = None
    rowcount: int = 0
    execution_time: float | None = None  # in seconds
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DatabaseQuery(BaseDBModel):
    """Database query model."""

    query: str
    query_type: QueryType
    parameters: dict[str, Any] | None = None
    connection_id: str
    status: QueryStatus = QueryStatus.PENDING
    result: QueryResult | None = None
    executed_at: datetime | None = None
    completed_at: datetime | None = None

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
