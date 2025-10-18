"""
SQLite database connector implementation.

Handles SQLite databases with embedded file-based storage.
Perfect for development, testing, and lightweight applications.
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from ....database_manager import (
    BaseDatabaseConnector,
    ConnectionError,
    ConnectionStatus,
    DatabaseType,
    QueryError,
    QueryResult,
)

logger = logging.getLogger(__name__)


class SQLiteConnector(BaseDatabaseConnector):
    """SQLite database connector."""

    @property
    def database_type(self) -> DatabaseType:
        """Return the database type."""
        return DatabaseType.SQLITE

    def __init__(self, connection_config: Dict[str, Any]):
        """Initialize SQLite connector."""
        super().__init__(connection_config)
        self.database_path = connection_config.get("database_path")
        if not self.database_path:
            raise ValueError("SQLite connector requires 'database_path' in connection config")

        if not os.path.isabs(self.database_path):
            self.database_path = os.path.abspath(self.database_path)

        self.connection = None

    async def connect(self) -> bool:
        """Establish SQLite database connection."""
        try:
            if self.connection:
                self.connection.close()

            self.connection = sqlite3.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row
            self.status = ConnectionStatus.CONNECTED
            self.last_error = None

            logger.info(f"Connected to SQLite database: {self.database_path}")
            return True

        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to connect to SQLite database: {e}")
            return False

    async def disconnect(self) -> bool:
        """Close SQLite database connection."""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None

            self.status = ConnectionStatus.DISCONNECTED
            self.last_error = None
            logger.info(f"Disconnected from SQLite database: {self.database_path}")
            return True

        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error disconnecting from SQLite database: {e}")
            return False

    async def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> QueryResult:
        """Execute query and return results."""
        try:
            if not self.connection:
                if not await self.connect():
                    raise ConnectionError("Failed to connect to SQLite database")

            cursor = self.connection.cursor()
            start_time = datetime.now()

            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)

            execution_time = (datetime.now() - start_time).total_seconds()

            query_lower = query.strip().lower()
            if query_lower.startswith("select") or query_lower.startswith("with"):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                row_data = [dict(row) for row in rows]

                return QueryResult(
                    success=True,
                    data=row_data,
                    columns=columns,
                    rowcount=len(row_data),
                    execution_time=execution_time,
                )
            else:
                affected_rows = cursor.rowcount
                self.connection.commit()

                return QueryResult(
                    success=True,
                    data=[],
                    rowcount=affected_rows,
                    execution_time=execution_time,
                    message=f"Query executed successfully. {affected_rows} rows affected.",
                )

        except Exception as e:
            logger.error(f"Error executing SQLite query: {e}")
            return QueryResult(success=False, data=[], message=f"Query execution failed: {e}")

    async def get_schema(self, **kwargs: Any) -> Dict[str, Any]:
        """Get the database schema."""
        try:
            if not self.connection:
                if not await self.connect():
                    raise ConnectionError("Failed to connect to SQLite database")

            tables = await self.get_tables()
            return {
                "database": os.path.basename(self.database_path),
                "tables": tables,
                "table_count": len(tables),
            }
        except Exception as e:
            logger.error(f"Error getting SQLite schema: {e}")
            raise QueryError(f"Failed to get schema: {e}") from e

    async def get_tables(self, **kwargs: Any) -> List[str]:
        """Get list of tables in the database."""
        try:
            if not self.connection:
                if not await self.connect():
                    raise ConnectionError("Failed to connect to SQLite database")

            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' 
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)

            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error listing SQLite tables: {e}")
            raise QueryError(f"Failed to list tables: {e}") from e

    async def get_table_schema(self, table_name: str, **kwargs: Any) -> Dict[str, Any]:
        """Get schema information for a specific table."""
        try:
            if not self.connection:
                if not await self.connect():
                    raise ConnectionError("Failed to connect to SQLite database")

            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info([{table_name}])")
            columns_info = cursor.fetchall()

            if not columns_info:
                raise QueryError(f"Table '{table_name}' not found")

            columns = []
            for col in columns_info:
                cid, name, data_type, not_null, default_value, pk = col
                columns.append(
                    {
                        "name": name,
                        "type": data_type,
                        "nullable": not not_null,
                        "default": default_value,
                        "primary_key": bool(pk),
                        "position": cid,
                    }
                )

            cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
            row_count = cursor.fetchone()[0]

            return {
                "table_name": table_name,
                "columns": columns,
                "row_count": row_count,
                "column_count": len(columns),
            }

        except Exception as e:
            logger.error(f"Error describing SQLite table {table_name}: {e}")
            raise QueryError(f"Failed to describe table: {e}") from e

    async def list_databases(self) -> List[Dict[str, Any]]:
        """List databases (SQLite only has one database per file)."""
        try:
            if not os.path.exists(self.database_path):
                return []
            
            # SQLite only has one database per file
            db_name = os.path.basename(self.database_path)
            file_size = os.path.getsize(self.database_path)
            
            return [{
                "database_name": db_name,
                "path": self.database_path,
                "size_bytes": file_size,
                "type": "main",
                "owner": "sqlite",
                "collation": "BINARY",
                "character_type": "UTF8",
                "is_template": False,
                "allow_connections": True
            }]
        except Exception as e:
            logger.error(f"Error listing SQLite databases: {e}")
            return []

    async def list_tables(self, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tables in the SQLite database."""
        try:
            if not self.connection:
                if not await self.connect():
                    raise ConnectionError("Failed to connect to SQLite database")

            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT 
                    name as table_name,
                    'table' as table_type,
                    'main' as schema_name,
                    'sqlite' as owner
                FROM sqlite_master 
                WHERE type='table' 
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            tables = []
            for row in cursor.fetchall():
                # Get row count for each table
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM [{row[0]}]")
                    row_count = cursor.fetchone()[0]
                except Exception:
                    row_count = 0
                
                tables.append({
                    "table_name": row[0],
                    "table_type": row[1],
                    "schema_name": row[2],
                    "owner": row[3],
                    "row_count": row_count
                })
            
            return tables
        except Exception as e:
            logger.error(f"Error listing SQLite tables: {e}")
            raise QueryError(f"Failed to list tables: {e}") from e

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive SQLite health check."""
        try:
            health_status = "healthy"
            issues = []

            if os.path.exists(self.database_path):
                if not os.access(self.database_path, os.R_OK):
                    health_status = "unhealthy"
                    issues.append("Database file is not readable")

                if not os.access(self.database_path, os.W_OK):
                    health_status = "warning"
                    issues.append("Database file is not writable")

            file_size = (
                os.path.getsize(self.database_path) if os.path.exists(self.database_path) else 0
            )
            if file_size > 1000000000:  # 1GB
                health_status = "warning" if health_status == "healthy" else health_status
                issues.append("Database file is very large (>1GB)")

            if self.connection or await self.connect():
                try:
                    cursor = self.connection.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                except Exception as e:
                    health_status = "unhealthy"
                    issues.append(f"Query test failed: {str(e)}")

            return {
                "status": health_status,
                "issues": issues,
                "database_path": self.database_path,
                "file_size_bytes": file_size,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error performing SQLite health check: {e}")
            return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}
