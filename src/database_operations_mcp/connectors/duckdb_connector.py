"""DuckDB database connector."""

from typing import Any, Dict, List, Optional

try:
    import duckdb
except ImportError:
    duckdb = None


class DuckDBConnector:
    """DuckDB database connector.

    DuckDB is an in-process analytical database. Provides fast analytical
    queries and Parquet file reading capabilities.
    """

    def __init__(self):
        """Initialize DuckDB connector."""
        self.conn: Optional[Any] = None

    async def connect(self, db_path: Optional[str] = None) -> Any:
        """Connect to DuckDB database.

        Args:
            db_path: Path to DuckDB database file (optional, uses in-memory by default)

        Returns:
            DuckDB connection object

        Raises:
            RuntimeError: If duckdb not installed
        """
        if duckdb is None:
            raise RuntimeError("duckdb not installed. Install with: pip install duckdb")

        if db_path:
            self.conn = duckdb.connect(db_path)
        else:
            self.conn = duckdb.connect()

        return self.conn

    async def execute_query(
        self, query: str, parameters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Execute SELECT query.

        Args:
            query: SQL query string
            parameters: Query parameters

        Returns:
            List of result rows as dictionaries
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")

        cursor = self.conn.execute(query, parameters or {})
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        return [dict(zip(columns, row, strict=False)) for row in results]

    async def execute_non_query(self, query: str, parameters: Optional[Dict] = None) -> int:
        """Execute non-SELECT query (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query string
            parameters: Query parameters

        Returns:
            Number of affected rows
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")

        cursor = self.conn.execute(query, parameters or {})
        return cursor.rowcount

    async def read_parquet(self, file_path: str, table_name: Optional[str] = None) -> int:
        """Read Parquet file into DuckDB.

        Args:
            file_path: Path to Parquet file
            table_name: Optional table name to create

        Returns:
            Number of rows read
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")

        query = f"SELECT * FROM '{file_path}'"
        cursor = self.conn.execute(query)

        if table_name:
            self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM '{file_path}'")

        return cursor.rowcount

    async def get_tables(self) -> List[str]:
        """Get list of tables in database.

        Returns:
            List of table names
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")

        query = "SHOW TABLES"
        results = await self.execute_query(query)
        return [row.get("name", "") for row in results if "name" in row]

    async def get_table_structure(self, table_name: str) -> List[Dict[str, Any]]:
        """Get table structure information.

        Args:
            table_name: Name of table

        Returns:
            List of column information dictionaries
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")

        query = f"DESCRIBE {table_name}"
        return await self.execute_query(query)

    async def close(self):
        """Close DuckDB connection."""
        if self.conn:
            self.conn.close()
