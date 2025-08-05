"""
SQLite database connector implementation.

Handles SQLite databases with embedded file-based storage.
Perfect for development, testing, and lightweight applications.
"""

import sqlite3
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..database_manager import (
    BaseDatabaseConnector, 
    DatabaseType, 
    ConnectionStatus,
    ConnectionError,
    QueryError
)

logger = logging.getLogger(__name__)

class SQLiteConnector(BaseDatabaseConnector):
    """SQLite database connector."""
    
    @property
    def database_type(self) -> DatabaseType:
        """Return the database type."""
        return DatabaseType.SQLITE
    
    def __init__(self, connection_config: Dict[str, Any]):
        """Initialize SQLite connector.
        
        Args:
            connection_config: Must contain 'database_path' key
        """
        super().__init__(connection_config)
        
        self.database_path = connection_config.get("database_path")
        if not self.database_path:
            raise ValueError("SQLite connector requires 'database_path' in connection config")
        
        # Convert relative paths to absolute
        if not os.path.isabs(self.database_path):
            self.database_path = os.path.abspath(self.database_path)
        
        self.connection = None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test SQLite database connectivity."""
        try:
            # Check if file exists or can be created
            db_dir = os.path.dirname(self.database_path)
            if not os.path.exists(db_dir):
                return {
                    "success": False,
                    "error": f"Directory does not exist: {db_dir}",
                    "database_path": self.database_path,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Try to connect and run a simple query
            test_conn = sqlite3.connect(self.database_path)
            cursor = test_conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            test_conn.close()
            
            file_size = os.path.getsize(self.database_path) if os.path.exists(self.database_path) else 0
            
            return {
                "success": True,
                "database_path": self.database_path,
                "sqlite_version": version,
                "file_exists": os.path.exists(self.database_path),
                "file_size_bytes": file_size,
                "readable": os.access(self.database_path, os.R_OK) if os.path.exists(self.database_path) else True,
                "writable": os.access(db_dir, os.W_OK),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"SQLite connection test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "database_path": self.database_path,
                "timestamp": datetime.now().isoformat()
            }
    
    def connect(self) -> bool:
        """Establish SQLite database connection."""
        try:
            if self.connection:
                self.connection.close()
            
            self.connection = sqlite3.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            self.status = ConnectionStatus.CONNECTED
            self.last_error = None
            
            logger.info(f"Connected to SQLite database: {self.database_path}")
            return True
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to connect to SQLite database: {e}")
            return False
    
    def disconnect(self) -> bool:
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
    
    def list_databases(self) -> List[Dict[str, Any]]:
        """List databases (SQLite has only one database per file)."""
        try:
            if not self.connection:
                if not self.connect():
                    raise ConnectionError("Failed to connect to SQLite database")
            
            # SQLite has only one database per file
            return [{
                "name": os.path.basename(self.database_path),
                "path": self.database_path,
                "size_bytes": os.path.getsize(self.database_path) if os.path.exists(self.database_path) else 0,
                "type": "sqlite"
            }]
            
        except Exception as e:
            logger.error(f"Error listing SQLite databases: {e}")
            raise QueryError(f"Failed to list databases: {e}")
    
    def list_tables(self, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tables in the SQLite database."""
        try:
            if not self.connection:
                if not self.connect():
                    raise ConnectionError("Failed to connect to SQLite database")
            
            cursor = self.connection.cursor()
            
            # Get tables and views
            cursor.execute("""
                SELECT name, type, sql 
                FROM sqlite_master 
                WHERE type IN ('table', 'view') 
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            tables = []
            for row in cursor.fetchall():
                name, table_type, sql = row
                
                # Get row count for tables
                row_count = 0
                if table_type == 'table':
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM [{name}]")
                        row_count = cursor.fetchone()[0]
                    except:
                        row_count = 0
                
                tables.append({
                    "name": name,
                    "type": table_type,
                    "row_count": row_count,
                    "sql": sql
                })
            
            return tables
            
        except Exception as e:
            logger.error(f"Error listing SQLite tables: {e}")
            raise QueryError(f"Failed to list tables: {e}")
    
    def describe_table(self, table_name: str, database: Optional[str] = None) -> Dict[str, Any]:
        """Get table schema and metadata."""
        try:
            if not self.connection:
                if not self.connect():
                    raise ConnectionError("Failed to connect to SQLite database")
            
            cursor = self.connection.cursor()
            
            # Get table info
            cursor.execute("PRAGMA table_info(?)", (table_name,))
            columns_info = cursor.fetchall()
            
            if not columns_info:
                raise QueryError(f"Table '{table_name}' not found")
            
            columns = []
            for col in columns_info:
                cid, name, data_type, not_null, default_value, pk = col
                columns.append({
                    "name": name,
                    "type": data_type,
                    "nullable": not not_null,
                    "default": default_value,
                    "primary_key": bool(pk),
                    "position": cid
                })
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
            row_count = cursor.fetchone()[0]
            
            # Get indexes
            cursor.execute("PRAGMA index_list(?)", (table_name,))
            indexes_info = cursor.fetchall()
            
            indexes = []
            for idx in indexes_info:
                seq, name, unique, origin, partial = idx
                cursor.execute("PRAGMA index_info(?)", (name,))
                index_columns = [col[2] for col in cursor.fetchall()]
                
                indexes.append({
                    "name": name,
                    "columns": index_columns,
                    "unique": bool(unique),
                    "origin": origin
                })
            
            # Get foreign keys
            cursor.execute("PRAGMA foreign_key_list(?)", (table_name,))
            foreign_keys_info = cursor.fetchall()
            
            foreign_keys = []
            for fk in foreign_keys_info:
                id, seq, table, from_col, to_col, on_update, on_delete, match = fk
                foreign_keys.append({
                    "column": from_col,
                    "references_table": table,
                    "references_column": to_col,
                    "on_update": on_update,
                    "on_delete": on_delete
                })
            
            return {
                "table_name": table_name,
                "columns": columns,
                "row_count": row_count,
                "indexes": indexes,
                "foreign_keys": foreign_keys,
                "column_count": len(columns)
            }
            
        except Exception as e:
            logger.error(f"Error describing SQLite table {table_name}: {e}")
            raise QueryError(f"Failed to describe table: {e}")
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute query and return results."""
        try:
            if not self.connection:
                if not self.connect():
                    raise ConnectionError("Failed to connect to SQLite database")
            
            cursor = self.connection.cursor()
            
            # Execute query with parameters
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            
            # Check if this is a SELECT query
            query_lower = query.strip().lower()
            if query_lower.startswith('select') or query_lower.startswith('with'):
                # Fetch results
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Convert Row objects to lists
                row_data = [list(row) for row in rows]
                
                return {
                    "query_type": "SELECT",
                    "columns": columns,
                    "rows": row_data,
                    "row_count": len(row_data),
                    "column_count": len(columns)
                }
            else:
                # For INSERT, UPDATE, DELETE, etc.
                affected_rows = cursor.rowcount
                self.connection.commit()
                
                return {
                    "query_type": "MODIFICATION",
                    "affected_rows": affected_rows,
                    "last_row_id": cursor.lastrowid if hasattr(cursor, 'lastrowid') else None
                }
                
        except Exception as e:
            logger.error(f"Error executing SQLite query: {e}")
            raise QueryError(f"Query execution failed: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get SQLite performance metrics."""
        try:
            if not self.connection:
                if not self.connect():
                    raise ConnectionError("Failed to connect to SQLite database")
            
            cursor = self.connection.cursor()
            
            # Get database statistics
            metrics = {}
            
            # File size
            file_size = os.path.getsize(self.database_path) if os.path.exists(self.database_path) else 0
            metrics["file_size_bytes"] = file_size
            metrics["file_size_mb"] = round(file_size / (1024 * 1024), 2)
            
            # Page count and size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            metrics["page_count"] = page_count
            metrics["page_size"] = page_size
            metrics["database_size_pages"] = page_count
            
            # Cache and memory info
            cursor.execute("PRAGMA cache_size")
            cache_size = cursor.fetchone()[0]
            metrics["cache_size"] = cache_size
            
            # Journal mode
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            metrics["journal_mode"] = journal_mode
            
            # Synchronous mode
            cursor.execute("PRAGMA synchronous")
            synchronous = cursor.fetchone()[0]
            metrics["synchronous_mode"] = synchronous
            
            # Auto vacuum
            cursor.execute("PRAGMA auto_vacuum")
            auto_vacuum = cursor.fetchone()[0]
            metrics["auto_vacuum"] = auto_vacuum
            
            return {
                "database_metrics": metrics,
                "performance_status": "healthy" if file_size < 1000000000 else "large_database",  # 1GB threshold
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting SQLite performance metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive SQLite health check."""
        try:
            health_status = "healthy"
            issues = []
            
            # Test connection
            connection_test = self.test_connection()
            if not connection_test["success"]:
                health_status = "unhealthy"
                issues.append(f"Connection failed: {connection_test['error']}")
            
            # Check file permissions and existence
            if os.path.exists(self.database_path):
                if not os.access(self.database_path, os.R_OK):
                    health_status = "unhealthy"
                    issues.append("Database file is not readable")
                
                if not os.access(self.database_path, os.W_OK):
                    health_status = "warning"
                    issues.append("Database file is not writable")
            
            # Get basic metrics
            metrics = self.get_performance_metrics()
            
            # Check for large database
            file_size = metrics.get("database_metrics", {}).get("file_size_bytes", 0)
            if file_size > 1000000000:  # 1GB
                health_status = "warning" if health_status == "healthy" else health_status
                issues.append("Database file is very large (>1GB)")
            
            # Try a simple query if connected
            query_test = None
            if self.connection or self.connect():
                try:
                    cursor = self.connection.cursor()
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
                "database_path": self.database_path,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error performing SQLite health check: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
