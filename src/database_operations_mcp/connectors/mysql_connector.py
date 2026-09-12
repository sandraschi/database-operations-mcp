"""MySQL database connector."""

from typing import Any

try:
    import aiomysql
except ImportError:
    aiomysql = None


class MySQLConnector:
    """MySQL database connector.

    Provides async connection to MySQL/MariaDB databases with connection
    pooling and transaction support.
    """

    def __init__(self):
        """Initialize MySQL connector."""
        self.pool: Any | None = None

    async def connect(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "",
        password: str = "",
        database: str = "",
    ) -> Any:
        """Connect to MySQL database.

        ## Return Format
        Returns the connection pool object.

        ## Examples
        Connect locally:
            pool = await connector.connect(user="root", database="mydb")
        """
        if aiomysql is None:
            raise RuntimeError("aiomysql not installed. Install with: pip install aiomysql")

        self.pool = await aiomysql.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            db=database,
            minsize=1,
            maxsize=10,
        )

        return self.pool

    async def execute_query(self, query: str, parameters: dict | None = None) -> list[dict[str, Any]]:
        """Execute SELECT query.

        ## Return Format
        Returns the result rows as a list of dicts.

        ## Examples
        Select rows:
            rows = await connector.execute_query("SELECT * FROM users LIMIT 5")
        """
        if not self.pool:
            raise RuntimeError("Not connected to database")
        if aiomysql is None:
            raise RuntimeError("aiomysql not installed. Install with: pip install aiomysql")

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, parameters or {})
                return await cursor.fetchall()

    async def execute_non_query(self, query: str, parameters: dict | None = None) -> int:
        """Execute non-SELECT query (INSERT, UPDATE, DELETE).

        ## Return Format
        Returns the number of affected rows.

        ## Examples
        Delete rows:
            n = await connector.execute_non_query("DELETE FROM sessions WHERE expired = 1")
        """
        if not self.pool:
            raise RuntimeError("Not connected to database")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, parameters or {})
                await conn.commit()
                return cursor.rowcount

    async def get_tables(self) -> list[str]:
        """Get list of tables in database.

        Returns:
            List of table names
        """
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()"
        results = await self.execute_query(query)
        return [row["table_name"] for row in results]

    async def get_table_structure(self, table_name: str) -> list[dict[str, Any]]:
        """Get table structure information.

        ## Return Format
        Returns the column info rows.

        ## Examples
        Describe a table:
            cols = await connector.get_table_structure("users")
        """
        query = f"DESCRIBE {table_name}"
        return await self.execute_query(query)

    async def close(self):
        """Close database connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
