"""DuckDB database connector."""

from typing import Any

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
        self.conn: Any | None = None

    async def connect(self, db_path: str | None = None) -> Any:
        """Connect to DuckDB database (in-memory when db_path is omitted).

        ## Return Format
        Returns the DuckDB connection object.

        ## Examples
        Connect in-memory:
            conn = await connector.connect()
        """
        if duckdb is None:
            raise RuntimeError("duckdb not installed. Install with: pip install duckdb")

        if db_path:
            self.conn = duckdb.connect(db_path)
        else:
            self.conn = duckdb.connect()

        return self.conn

    async def execute_query(self, query: str, parameters: dict | None = None) -> list[dict[str, Any]]:
        """Execute SELECT query.

        ## Return Format
        Returns the result rows as a list of dicts.

        ## Examples
        Show tables:
            rows = await connector.execute_query("SHOW TABLES")
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")

        cursor = self.conn.execute(query, parameters or {})
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        return [dict(zip(columns, row, strict=False)) for row in results]

    async def execute_non_query(self, query: str, parameters: dict | None = None) -> int:
        """Execute non-SELECT query (INSERT, UPDATE, DELETE).

        ## Return Format
        Returns the number of affected rows.

        ## Examples
        Create a table:
            n = await connector.execute_non_query("CREATE TABLE t (id INT)")
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")

        cursor = self.conn.execute(query, parameters or {})
        return cursor.rowcount

    async def read_parquet(self, file_path: str, table_name: str | None = None) -> int:
        """Read Parquet file into DuckDB.

        ## Return Format
        Returns the number of rows read.

        ## Examples
        Load a file:
            n = await connector.read_parquet("data/part.parquet", "events")
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")

        query = f"SELECT * FROM '{file_path}'"  # noqa: S608  # trusted file path
        cursor = self.conn.execute(query)

        if table_name:
            self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM '{file_path}'")  # noqa: S608  # trusted identifiers from caller

        return cursor.rowcount

    async def get_tables(self) -> list[str]:
        """Get list of tables in database.

        Returns:
            List of table names
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")

        query = "SHOW TABLES"
        results = await self.execute_query(query)
        return [row.get("name", "") for row in results if "name" in row]

    async def get_table_structure(self, table_name: str) -> list[dict[str, Any]]:
        """Get table structure information.

        ## Return Format
        Returns the column info rows.

        ## Examples
        Describe a table:
            cols = await connector.get_table_structure("events")
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")

        query = f"DESCRIBE {table_name}"
        return await self.execute_query(query)

    async def close(self):
        """Close DuckDB connection."""
        if self.conn:
            self.conn.close()
