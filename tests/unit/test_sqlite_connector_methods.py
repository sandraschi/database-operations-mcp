"""
Tests for SQLite connector missing methods implementation.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from database_operations_mcp.database_manager import ConnectionError, QueryError
from database_operations_mcp.services.database.connectors.sqlite_connector import SQLiteConnector


class TestSQLiteConnectorMethods:
    """Test the newly implemented SQLite connector methods."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary SQLite database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        # Create a test database with some tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create test tables
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Insert test data
        cursor.execute("INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com')")
        cursor.execute("INSERT INTO users (name, email) VALUES ('Jane Smith', 'jane@example.com')")
        cursor.execute(
            "INSERT INTO posts (title, content, user_id) VALUES "
            "('Test Post', 'Content here', 1)"
        )
        
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup - ensure connection is closed
        try:
            Path(db_path).unlink(missing_ok=True)
        except PermissionError:
            # File might be locked, try again after a short delay
            import time
            time.sleep(0.1)
            try:
                Path(db_path).unlink(missing_ok=True)
            except PermissionError:
                pass  # Give up if still locked

    @pytest.fixture
    def sqlite_connector(self, temp_db_path):
        """Create a SQLite connector instance."""
        config = {
            "database_path": temp_db_path,
            "database_name": "test_db"
        }
        return SQLiteConnector(config)

    @pytest.mark.asyncio
    async def test_list_databases(self, sqlite_connector):
        """Test list_databases method."""
        databases = await sqlite_connector.list_databases()
        
        assert isinstance(databases, list)
        assert len(databases) == 1
        assert databases[0]["database_name"].endswith(".db")
        assert databases[0]["type"] == "main"
        assert "path" in databases[0]

    @pytest.mark.asyncio
    async def test_list_tables(self, sqlite_connector):
        """Test list_tables method."""
        tables = await sqlite_connector.list_tables()
        
        assert isinstance(tables, list)
        assert len(tables) == 2
        
        # Check table names
        table_names = [table["table_name"] for table in tables]
        assert "users" in table_names
        assert "posts" in table_names
        
        # Check table structure
        for table in tables:
            assert "table_name" in table
            assert "table_type" in table
            assert "schema_name" in table
            assert "owner" in table
            assert "row_count" in table

    @pytest.mark.asyncio
    async def test_list_tables_with_database_name(self, sqlite_connector):
        """Test list_tables method with database_name parameter."""
        tables = await sqlite_connector.list_tables(database="test_db")
        
        assert isinstance(tables, list)
        assert len(tables) == 2
        
        # Check table names
        table_names = [table["table_name"] for table in tables]
        assert "users" in table_names
        assert "posts" in table_names

    @pytest.mark.asyncio
    async def test_get_table_schema_users(self, sqlite_connector):
        """Test get_table_schema method for users table."""
        schema = await sqlite_connector.get_table_schema("users")
        
        assert isinstance(schema, dict)
        assert schema["table_name"] == "users"
        assert "columns" in schema
        
        columns = schema["columns"]
        assert len(columns) == 3
        
        # Check column details
        id_col = next(col for col in columns if col["name"] == "id")
        assert id_col["type"] == "INTEGER"
        assert id_col["primary_key"] is True
        
        name_col = next(col for col in columns if col["name"] == "name")
        assert name_col["type"] == "TEXT"
        assert name_col["nullable"] is False  # NOT NULL constraint
        
        email_col = next(col for col in columns if col["name"] == "email")
        assert email_col["type"] == "TEXT"

    @pytest.mark.asyncio
    async def test_get_table_schema_posts(self, sqlite_connector):
        """Test get_table_schema method for posts table."""
        schema = await sqlite_connector.get_table_schema("posts")
        
        assert isinstance(schema, dict)
        assert schema["table_name"] == "posts"
        assert "columns" in schema
        
        columns = schema["columns"]
        assert len(columns) == 4
        
        # Check foreign key column
        user_id_col = next(col for col in columns if col["name"] == "user_id")
        assert user_id_col["type"] == "INTEGER"

    @pytest.mark.asyncio
    async def test_get_table_schema_nonexistent_table(self, sqlite_connector):
        """Test get_table_schema method with nonexistent table."""
        with pytest.raises(QueryError):
            await sqlite_connector.get_table_schema("nonexistent_table")

    @pytest.mark.asyncio
    async def test_list_databases_error_handling(self, sqlite_connector):
        """Test list_databases error handling."""
        # Test with non-existent database path
        sqlite_connector.database_path = "C:\\nonexistent\\path\\that\\cannot\\be\\created.db"
        databases = await sqlite_connector.list_databases()
        assert databases == []

    @pytest.mark.asyncio
    async def test_list_tables_error_handling(self, sqlite_connector):
        """Test list_tables error handling."""
        # Test with non-existent database path
        sqlite_connector.database_path = "C:\\nonexistent\\path\\that\\cannot\\be\\created.db"
        with pytest.raises(ConnectionError):
            await sqlite_connector.list_tables()

    @pytest.mark.asyncio
    async def test_get_table_schema_error_handling(self, sqlite_connector):
        """Test get_table_schema error handling."""
        # Test with non-existent database path
        sqlite_connector.database_path = "C:\\nonexistent\\path\\that\\cannot\\be\\created.db"
        with pytest.raises(ConnectionError):
            await sqlite_connector.get_table_schema("users")
