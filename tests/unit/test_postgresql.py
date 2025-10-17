"""
Test script for PostgreSQL connection using the database-operations-mcp package.
"""

from database_operations_mcp.database_manager import DatabaseManager


def test_postgres_connection(postgresql_config):
    """Test PostgreSQL connection with the provided configuration."""
    try:
        # Initialize the database manager
        db_manager = DatabaseManager()

        # Create and register the PostgreSQL connector
        from database_operations_mcp.connectors.postgresql_connector import PostgreSQLConnector

        connector = PostgreSQLConnector(postgresql_config)

        # Test the connection
        test_result = connector.test_connection()
        print("\n=== Connection Test Result ===")
        print(f"Success: {test_result['success']}")
        print(f"Server Version: {test_result.get('server_version')}")
        print(f"Current Database: {test_result.get('current_database')}")

        # List databases if connection successful
        if test_result["success"]:
            print("\n=== Available Databases ===")
            databases = connector.list_databases()
            for db in databases:
                print(f"- {db['database_name']} (Size: {db.get('size_mb', 0):.2f} MB)")

            # List tables in the current database
            print(f"\n=== Tables in {connection_config['database']} ===")
            tables = connector.list_tables()
            for table in tables:
                print(f"- {table['full_name']} ({table.get('row_count', 0)} rows)")

        return test_result

    except Exception as e:
        print(f"\nError: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Replace these with your PostgreSQL connection details
    POSTGRES_CONFIG = {
        "host": "localhost",  # Your PostgreSQL server host
        "port": 5432,  # Default PostgreSQL port is 5432
        "database": "postgres",  # Default database to connect to
        "user": "postgres",  # Your PostgreSQL username
        "password": "your_password",  # Your PostgreSQL password
        "sslmode": "prefer",  # SSL mode (prefer, require, disable, etc.)
    }

    print("Testing PostgreSQL connection...")
    test_postgres_connection(POSTGRES_CONFIG)
