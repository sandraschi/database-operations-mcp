"""Database schema models."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseDBModel


class ColumnType(str, Enum):
    """Common database column types."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    BINARY = "binary"
    JSON = "json"
    ARRAY = "array"
    OBJECT = "object"
    CUSTOM = "custom"


class ConstraintType(str, Enum):
    """Database constraint types."""

    PRIMARY_KEY = "primary_key"
    FOREIGN_KEY = "foreign_key"
    UNIQUE = "unique"
    CHECK = "check"
    NOT_NULL = "not_null"
    DEFAULT = "default"
    INDEX = "index"


class ColumnConstraint(BaseDBModel):
    """Column constraint definition."""

    name: str
    constraint_type: ConstraintType
    value: Optional[Any] = None
    reference_table: Optional[str] = None
    reference_column: Optional[str] = None


class TableColumn(BaseDBModel):
    """Database table column definition."""

    name: str
    data_type: ColumnType
    max_length: Optional[int] = None
    nullable: bool = True
    default: Optional[Any] = None
    constraints: List[ColumnConstraint] = Field(default_factory=list)
    description: Optional[str] = None
    custom_type: Optional[str] = None

    @property
    def is_primary_key(self) -> bool:
        """Check if column is a primary key."""
        return any(c.constraint_type == ConstraintType.PRIMARY_KEY for c in self.constraints)

    @property
    def is_foreign_key(self) -> bool:
        """Check if column is a foreign key."""
        return any(c.constraint_type == ConstraintType.FOREIGN_KEY for c in self.constraints)


class TableIndex(BaseDBModel):
    """Database table index definition."""

    name: str
    columns: List[str]
    unique: bool = False
    method: Optional[str] = None  # e.g., 'btree', 'hash', 'gist', etc.


class TableSchema(BaseDBModel):
    """Database table schema definition."""

    name: str
    columns: Dict[str, TableColumn] = Field(default_factory=dict)
    indexes: List[TableIndex] = Field(default_factory=list)
    primary_key: List[str] = Field(default_factory=list)
    foreign_keys: Dict[str, Dict[str, str]] = Field(
        default_factory=dict
    )  # {column: {table: ref_column}}
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_column(self, column: TableColumn) -> None:
        """Add a column to the table."""
        self.columns[column.name] = column

    def remove_column(self, column_name: str) -> None:
        """Remove a column from the table."""
        if column_name in self.columns:
            del self.columns[column_name]
            # Remove from primary key if present
            if column_name in self.primary_key:
                self.primary_key.remove(column_name)
            # Remove from foreign keys if present
            if column_name in self.foreign_keys:
                del self.foreign_keys[column_name]


class DatabaseSchema(BaseDBModel):
    """Complete database schema."""

    name: str
    tables: Dict[str, TableSchema] = Field(default_factory=dict)
    views: Dict[str, str] = Field(default_factory=dict)  # view_name: view_definition
    functions: Dict[str, str] = Field(default_factory=dict)  # function_name: function_definition
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_table(self, table: TableSchema) -> None:
        """Add a table to the schema."""
        self.tables[table.name] = table

    def remove_table(self, table_name: str) -> None:
        """Remove a table from the schema."""
        if table_name in self.tables:
            del self.tables[table_name]
