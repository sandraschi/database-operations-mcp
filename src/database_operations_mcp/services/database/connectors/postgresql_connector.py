"""
PostgreSQL database connector implementation.

Handles PostgreSQL databases with advanced features like schemas, custom types,
and complex queries. Perfect for production applications and development.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras

from ....database_manager import (
    BaseDatabaseConnector,
    ConnectionError,
    ConnectionStatus,
    DatabaseType,
    QueryError,
)

logger = logging.getLogger(__name__)


class PostgreSQLConnector(BaseDatabaseConnector):
    """PostgreSQL database connector."""

    @property
    def database_type(self) -> DatabaseType:
        """Return the database type."""
        return DatabaseType.POSTGRESQL

    def __init__(self, connection_config: Dict[str, Any]):
        """Initialize PostgreSQL connector.

        Args:
            connection_config: Must contain connection parameters
                - host: PostgreSQL server host
                - port: PostgreSQL server port (default: 5432)
                - database: Database name
                - user: Username
                - password: Password
                - sslmode: SSL mode (optional, default: prefer)
        """
        super().__init__(connection_config)

        # Required parameters
        required_params = ["host", "database", "user", "password"]
        for param in required_params:
            if param not in connection_config:
                raise ValueError(f"PostgreSQL connector requires '{param}' in connection config")

        self.host = connection_config["host"]
        self.port = connection_config.get("port", 5432)
        self.database = connection_config["database"]
        self.user = connection_config["user"]
        self.password = connection_config["password"]
        self.sslmode = connection_config.get("sslmode", "prefer")

        self.connection = None

    def test_connection(self) -> Dict[str, Any]:
        """Test PostgreSQL database connectivity."""
        try:
            # Build connection string
            conn_string = self._build_connection_string()

            # Test connection
            test_conn = psycopg2.connect(conn_string)

            # Get server information
            with test_conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                server_version = cursor.fetchone()[0]

                cursor.execute("SELECT current_database()")
                current_db = cursor.fetchone()[0]

                cursor.execute("SELECT current_user")
                current_user = cursor.fetchone()[0]

                cursor.execute("SELECT pg_database_size(current_database())")
                db_size = cursor.fetchone()[0]

                # Check if we can create tables (write permissions)
                try:
                    cursor.execute("CREATE TEMPORARY TABLE test_permissions (id INT)")
                    cursor.execute("DROP TABLE test_permissions")
                    write_permissions = True
                except Exception:
                    write_permissions = False

            test_conn.close()

            return {
                "success": True,
                "server_version": server_version,
                "current_database": current_db,
                "current_user": current_user,
                "database_size_bytes": db_size,
                "database_size_mb": round(db_size / (1024 * 1024), 2),
                "write_permissions": write_permissions,
                "connection_params": {
                    "host": self.host,
                    "port": self.port,
                    "database": self.database,
                    "user": self.user,
                    "sslmode": self.sslmode,
                },
                "timestamp": datetime.now().isoformat(),
            }

        except psycopg2.OperationalError as e:
            logger.error(f"PostgreSQL connection test failed: {e}")
            return {
                "success": False,
                "error": f"Connection failed: {str(e)}",
                "error_type": "connection",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"PostgreSQL test error: {e}")
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    def connect(self) -> bool:
        """Establish PostgreSQL database connection."""
        try:
            if self.connection:
                self.connection.close()

            conn_string = self._build_connection_string()
            self.connection = psycopg2.connect(conn_string)

            # Use RealDictCursor for column name access
            self.connection.cursor_factory = psycopg2.extras.RealDictCursor

            self.status = ConnectionStatus.CONNECTED
            self.last_error = None

            logger.info(
                f"Connected to PostgreSQL database: {self.host}:{self.port}/{self.database}"
            )
            return True

        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to connect to PostgreSQL database: {e}")
            return False

    def disconnect(self) -> bool:
        """Close PostgreSQL database connection."""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None

            self.status = ConnectionStatus.DISCONNECTED
            self.last_error = None

            logger.info(
                f"Disconnected from PostgreSQL database: {self.host}:{self.port}/{self.database}"
            )
            return True

        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error disconnecting from PostgreSQL database: {e}")
            return False

    def _build_connection_string(self) -> str:
        """Build PostgreSQL connection string."""
        return (
            f"host={self.host} "
            f"port={self.port} "
            f"database={self.database} "
            f"user={self.user} "
            f"password={self.password} "
            f"sslmode={self.sslmode}"
        )

    def list_databases(self) -> List[Dict[str, Any]]:
        """List all databases on the PostgreSQL server."""
        try:
            if not self.connection:
                if not self.connect():
                    raise ConnectionError("Failed to connect to PostgreSQL database")

            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        d.datname as database_name,
                        u.usename as owner,
                        pg_database_size(d.datname) as size_bytes,
                        d.datcollate as collation,
                        d.datctype as character_type,
                        d.datistemplate as is_template,
                        d.datallowconn as allow_connections
                    FROM pg_database d
                    JOIN pg_user u ON d.datdba = u.usesysid
                    WHERE d.datistemplate = false
                    ORDER BY d.datname
                """)

                databases = []
                for row in cursor.fetchall():
                    databases.append(
                        {
                            "name": row["database_name"],
                            "owner": row["owner"],
                            "size_bytes": row["size_bytes"],
                            "size_mb": round(row["size_bytes"] / (1024 * 1024), 2)
                            if row["size_bytes"]
                            else 0,
                            "collation": row["collation"],
                            "character_type": row["character_type"],
                            "is_template": row["is_template"],
                            "allow_connections": row["allow_connections"],
                        }
                    )

                return databases

        except Exception as e:
            logger.error(f"Error listing PostgreSQL databases: {e}")
            raise QueryError(f"Failed to list databases: {e}") from e

    def list_tables(self, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tables in the PostgreSQL database."""
        try:
            if not self.connection:
                if not self.connect():
                    raise ConnectionError("Failed to connect to PostgreSQL database")

            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        schemaname,
                        tablename,
                        tableowner,
                        hasindexes,
                        hasrules,
                        hastriggers,
                        rowsecurity
                    FROM pg_tables 
                    WHERE schemaname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    ORDER BY schemaname, tablename
                """)

                tables = []
                for row in cursor.fetchall():
                    # Get row count
                    try:
                        cursor.execute(
                            f'SELECT COUNT(*) FROM "{row["schemaname"]}"."{row["tablename"]}"'
                        )
                        row_count = cursor.fetchone()[0]
                    except Exception:
                        row_count = 0

                    tables.append(
                        {
                            "schema": row["schemaname"],
                            "name": row["tablename"],
                            "full_name": f"{row['schemaname']}.{row['tablename']}",
                            "owner": row["tableowner"],
                            "row_count": row_count,
                            "has_indexes": row["hasindexes"],
                            "has_rules": row["hasrules"],
                            "has_triggers": row["hastriggers"],
                            "row_security": row["rowsecurity"],
                        }
                    )

                return tables

        except Exception as e:
            logger.error(f"Error listing PostgreSQL tables: {e}")
            raise QueryError(f"Failed to list tables: {e}") from e

    def describe_table(self, table_name: str, database: Optional[str] = None) -> Dict[str, Any]:
        """Get table schema and metadata."""
        try:
            if not self.connection:
                if not self.connect():
                    raise ConnectionError("Failed to connect to PostgreSQL database")

            # Parse schema and table name
            if "." in table_name:
                schema_name, table_name = table_name.split(".", 1)
            else:
                schema_name = "public"

            with self.connection.cursor() as cursor:
                # Get column information
                cursor.execute(
                    """
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        character_maximum_length,
                        numeric_precision,
                        numeric_scale,
                        ordinal_position
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                """,
                    (schema_name, table_name),
                )

                columns_info = cursor.fetchall()
                if not columns_info:
                    raise QueryError(f"Table '{schema_name}.{table_name}' not found")

                columns = []
                for col in columns_info:
                    columns.append(
                        {
                            "name": col["column_name"],
                            "type": col["data_type"],
                            "nullable": col["is_nullable"] == "YES",
                            "default": col["column_default"],
                            "max_length": col["character_maximum_length"],
                            "precision": col["numeric_precision"],
                            "scale": col["numeric_scale"],
                            "position": col["ordinal_position"],
                        }
                    )

                # Get primary key information
                cursor.execute(
                    """
                    SELECT column_name
                    FROM information_schema.key_column_usage kcu
                    JOIN information_schema.table_constraints tc
                        ON kcu.constraint_name = tc.constraint_name
                        AND kcu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                        AND tc.table_schema = %s 
                        AND tc.table_name = %s
                    ORDER BY kcu.ordinal_position
                """,
                    (schema_name, table_name),
                )

                primary_keys = [row["column_name"] for row in cursor.fetchall()]

                # Get foreign key information
                cursor.execute(
                    """
                    SELECT 
                        kcu.column_name,
                        ccu.table_schema AS foreign_table_schema,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.key_column_usage kcu
                    JOIN information_schema.constraint_column_usage ccu
                        ON kcu.constraint_name = ccu.constraint_name
                    JOIN information_schema.table_constraints tc
                        ON kcu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND kcu.table_schema = %s 
                        AND kcu.table_name = %s
                """,
                    (schema_name, table_name),
                )

                foreign_keys = []
                for fk in cursor.fetchall():
                    foreign_keys.append(
                        {
                            "column": fk["column_name"],
                            "references_schema": fk["foreign_table_schema"],
                            "references_table": fk["foreign_table_name"],
                            "references_column": fk["foreign_column_name"],
                        }
                    )

                # Get indexes
                cursor.execute(
                    """
                    SELECT 
                        indexname,
                        indexdef
                    FROM pg_indexes
                    WHERE schemaname = %s AND tablename = %s
                """,
                    (schema_name, table_name),
                )

                indexes = []
                for idx in cursor.fetchall():
                    indexes.append({"name": idx["indexname"], "definition": idx["indexdef"]})

                # Get row count
                cursor.execute(f'SELECT COUNT(*) FROM "{schema_name}"."{table_name}"')
                row_count = cursor.fetchone()[0]

                return {
                    "schema": schema_name,
                    "table_name": table_name,
                    "full_name": f"{schema_name}.{table_name}",
                    "columns": columns,
                    "primary_keys": primary_keys,
                    "foreign_keys": foreign_keys,
                    "indexes": indexes,
                    "row_count": row_count,
                    "column_count": len(columns),
                }

        except Exception as e:
            logger.error(f"Error describing PostgreSQL table {table_name}: {e}")
            raise QueryError(f"Failed to describe table: {e}") from e

    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute query and return results."""
        try:
            if not self.connection:
                if not self.connect():
                    raise ConnectionError("Failed to connect to PostgreSQL database")

            with self.connection.cursor() as cursor:
                # Execute query with parameters
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)

                # Check if this is a SELECT query
                query_lower = query.strip().lower()
                if query_lower.startswith("select") or query_lower.startswith("with"):
                    # Fetch results
                    rows = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []

                    # Convert RealDictRow objects to regular dicts/lists
                    row_data = []
                    for row in rows:
                        if isinstance(row, psycopg2.extras.RealDictRow):
                            row_data.append(dict(row))
                        else:
                            row_data.append(list(row))

                    return {
                        "query_type": "SELECT",
                        "columns": columns,
                        "rows": row_data,
                        "row_count": len(row_data),
                        "column_count": len(columns),
                    }
                else:
                    # For INSERT, UPDATE, DELETE, etc.
                    affected_rows = cursor.rowcount
                    self.connection.commit()

                    return {"query_type": "MODIFICATION", "affected_rows": affected_rows}

        except Exception as e:
            if self.connection:
                self.connection.rollback()
            logger.error(f"Error executing PostgreSQL query: {e}")
            raise QueryError(f"Query execution failed: {e}") from e

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get PostgreSQL performance metrics."""
        try:
            if not self.connection:
                if not self.connect():
                    raise ConnectionError("Failed to connect to PostgreSQL database")

            metrics = {}

            with self.connection.cursor() as cursor:
                # Database size
                cursor.execute("SELECT pg_database_size(current_database())")
                db_size = cursor.fetchone()[0]
                metrics["database_size_bytes"] = db_size
                metrics["database_size_mb"] = round(db_size / (1024 * 1024), 2)

                # Connection stats
                cursor.execute("""
                    SELECT 
                        max_conn,
                        used,
                        res_for_super,
                        max_conn - used - res_for_super as available
                    FROM 
                        (SELECT count(*) used FROM pg_stat_activity) q1,
                        (SELECT setting::int res_for_super FROM pg_settings 
                         WHERE name = 'superuser_reserved_connections') q2,
                        (SELECT setting::int max_conn FROM pg_settings 
                         WHERE name = 'max_connections') q3
                """)

                conn_stats = cursor.fetchone()
                metrics["connections"] = {
                    "max_connections": conn_stats[0],
                    "used_connections": conn_stats[1],
                    "reserved_connections": conn_stats[2],
                    "available_connections": conn_stats[3],
                }

                # Cache hit ratio
                cursor.execute("""
                    SELECT 
                        sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) 
                        as cache_hit_ratio
                    FROM pg_statio_user_tables
                """)

                cache_hit = cursor.fetchone()[0]
                metrics["cache_hit_ratio"] = round(float(cache_hit or 0) * 100, 2)

                # Transaction stats
                cursor.execute("""
                    SELECT 
                        xact_commit,
                        xact_rollback,
                        xact_commit + xact_rollback as total_transactions
                    FROM pg_stat_database 
                    WHERE datname = current_database()
                """)

                tx_stats = cursor.fetchone()
                metrics["transactions"] = {
                    "committed": tx_stats[0],
                    "rolled_back": tx_stats[1],
                    "total": tx_stats[2],
                }

            return {
                "database_metrics": metrics,
                "performance_status": "healthy"
                if metrics.get("cache_hit_ratio", 0) > 95
                else "needs_tuning",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting PostgreSQL performance metrics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive PostgreSQL health check."""
        try:
            health_status = "healthy"
            issues = []

            # Test connection
            connection_test = self.test_connection()
            if not connection_test["success"]:
                health_status = "unhealthy"
                issues.append(f"Connection failed: {connection_test['error']}")

            # Get performance metrics
            metrics = self.get_performance_metrics()

            # Check connection usage
            conn_stats = metrics.get("database_metrics", {}).get("connections", {})
            if conn_stats:
                used_pct = (conn_stats["used_connections"] / conn_stats["max_connections"]) * 100
                if used_pct > 80:
                    health_status = "warning" if health_status == "healthy" else health_status
                    issues.append(f"High connection usage: {used_pct:.1f}%")

            # Check cache hit ratio
            cache_hit_ratio = metrics.get("database_metrics", {}).get("cache_hit_ratio", 0)
            if cache_hit_ratio < 95:
                health_status = "warning" if health_status == "healthy" else health_status
                issues.append(f"Low cache hit ratio: {cache_hit_ratio}%")

            # Try a simple query if connected
            query_test = None
            if self.connection or self.connect():
                try:
                    with self.connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                    query_test = {"success": True}
                except Exception as e:
                    query_test = {"success": False, "error": str(e)}
                    health_status = "unhealthy"
                    issues.append(f"Query test failed: {str(e)}")

            return {
                "status": health_status,
                "issues": issues,
                "connection_test": connection_test,
                "query_test": query_test,
                "metrics": metrics,
                "connection_info": {
                    "host": self.host,
                    "port": self.port,
                    "database": self.database,
                    "user": self.user,
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error performing PostgreSQL health check: {e}")
            return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}
