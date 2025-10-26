"""
Database structure analysis service.

This module provides functionality to analyze and extract database structure
information including tables, columns, indexes, foreign keys, views, and triggers.
Supports multiple database types including SQLite, PostgreSQL, MySQL, MongoDB.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict

import aiosqlite


class StructureAnalyzer:
    """Analyze database structure and schema.

    Provides comprehensive database structure analysis including detection
    of database type, schema extraction, and metadata analysis. Supports
    SQLite, PostgreSQL, MySQL dumps, and other formats.
    """

    def __init__(self):
        """Initialize structure analyzer."""
        self.signatures = {
            b"SQLite format 3": "sqlite",
            b"PostgreSQL database": "postgresql",
            b"MySQL dump": "mysql",
            b"SQL DUMP": "generic_sql",
        }

    def detect_database_type(self, file_path: str) -> str:
        """Detect database type from file signature.

        Analyzes the file header to determine database type based on magic
        numbers and signature patterns.

        Args:
            file_path: Path to database file

        Returns:
            Database type identifier (sqlite, postgresql, mysql, etc.)

        Raises:
            FileNotFoundError: If database file doesn't exist
            ValueError: If database type cannot be determined
        """
        db_path = Path(file_path)
        if not db_path.exists():
            raise FileNotFoundError(f"Database file not found: {file_path}")

        try:
            with open(db_path, "rb") as f:
                header = f.read(32)

            for signature, db_type in self.signatures.items():
                if header.startswith(signature):
                    return db_type

            # Try SQLite by attempting connection
            try:
                with sqlite3.connect(db_path):
                    return "sqlite"
            except Exception:
                pass

            raise ValueError(f"Unknown database type for file: {file_path}")

        except Exception as e:
            raise ValueError(f"Error detecting database type: {e}") from e

    async def analyze_schema(self, db_path: str) -> Dict[str, Any]:
        """Extract complete database schema information.

        Analyzes the database structure to extract all schema elements including
        tables, columns, indexes, foreign keys, views, and triggers.

        Args:
            db_path: Path to database file

        Returns:
            Dictionary containing complete schema information:
                {
                    'database_type': str,
                    'tables': [
                        {
                            'name': str,
                            'columns': [...],
                            'indexes': [...],
                            'foreign_keys': [...],
                            'primary_key': str,
                            'row_count': int,
                            'size_bytes': int
                        },
                        ...
                    ],
                    'views': [...],
                    'triggers': [...],
                    'functions': [...],
                    'summary': {...}
                }

        Raises:
            ValueError: If database is invalid or unsupported
        """
        db_type = self.detect_database_type(db_path)

        if db_type == "sqlite":
            return await self._analyze_sqlite_schema(db_path)
        else:
            raise ValueError(f"Schema analysis for {db_type} not yet implemented")

    async def _analyze_sqlite_schema(self, db_path: str) -> Dict[str, Any]:
        """Analyze SQLite database schema.

        Extracts comprehensive schema information from SQLite database including
        table definitions, column types, indexes, constraints, and foreign keys.

        Args:
            db_path: Path to SQLite database file

        Returns:
            Complete schema information dictionary
        """
        async with aiosqlite.connect(db_path) as conn:
            tables = []
            views = []
            triggers = []

            # Get all table names
            async with conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ) as cursor:
                table_names = [row[0] for row in await cursor.fetchall()]

            # Analyze each table
            for table_name in table_names:
                table_info = await self._analyze_table(conn, table_name)
                tables.append(table_info)

            # Get views
            async with conn.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='view'"
            ) as cursor:
                views = [{"name": row[0], "definition": row[1]} for row in await cursor.fetchall()]

            # Get triggers
            async with conn.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='trigger'"
            ) as cursor:
                triggers = [
                    {"name": row[0], "definition": row[1]} for row in await cursor.fetchall()
                ]

            return {
                "database_type": "sqlite",
                "tables": tables,
                "views": views,
                "triggers": triggers,
                "functions": [],
                "summary": {
                    "table_count": len(tables),
                    "view_count": len(views),
                    "trigger_count": len(triggers),
                    "total_tables": len(table_names),
                },
            }

    async def _analyze_table(self, conn: aiosqlite.Connection, table_name: str) -> Dict[str, Any]:
        """Analyze individual table structure.

        Extracts detailed information about a table including columns, indexes,
        constraints, and foreign keys.

        Args:
            conn: Database connection
            table_name: Name of table to analyze

        Returns:
            Table information dictionary
        """
        # Get column information
        async with conn.execute(f"PRAGMA table_info({table_name})") as cursor:
            columns = []
            primary_key = None
            for row in await cursor.fetchall():
                col_info = {
                    "name": row[1],
                    "type": row[2],
                    "not_null": bool(row[3]),
                    "default_value": row[4],
                    "primary_key": bool(row[5]),
                }
                if col_info["primary_key"]:
                    primary_key = col_info["name"]
                columns.append(col_info)

        # Get indexes
        async with conn.execute(
            f"SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}'"
        ) as cursor:
            indexes = [{"name": row[0], "definition": row[1]} for row in await cursor.fetchall()]

        # Get foreign keys
        async with conn.execute(f"PRAGMA foreign_key_list({table_name})") as cursor:
            foreign_keys = []
            for row in await cursor.fetchall():
                foreign_keys.append(
                    {
                        "from_table": table_name,
                        "from_column": row[3],
                        "to_table": row[2],
                        "to_column": row[4],
                        "on_update": row[6],
                        "on_delete": row[7],
                    }
                )

        # Get row count
        async with conn.execute(f"SELECT COUNT(*) FROM {table_name}") as cursor:
            row_count = (await cursor.fetchone())[0]

        # Estimate table size
        size_bytes = await self._estimate_table_size(conn, table_name)

        return {
            "name": table_name,
            "columns": columns,
            "indexes": indexes,
            "foreign_keys": foreign_keys,
            "primary_key": primary_key,
            "row_count": row_count,
            "size_bytes": size_bytes,
        }

    async def _estimate_table_size(self, conn: aiosqlite.Connection, table_name: str) -> int:
        """Estimate table size in bytes.

        Args:
            conn: Database connection
            table_name: Name of table

        Returns:
            Estimated size in bytes
        """
        try:
            async with conn.execute(
                "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()"
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    async def get_database_info(self, db_path: str) -> Dict[str, Any]:
        """Get basic database information and statistics.

        Args:
            db_path: Path to database file

        Returns:
            Dictionary with database information:
                {
                    'database_type': str,
                    'file_path': str,
                    'file_size': int,
                    'page_count': int,
                    'page_size': int,
                    'encoding': str,
                    'sqlite_version': str
                }
        """
        db_type = self.detect_database_type(db_path)

        info = {
            "database_type": db_type,
            "file_path": db_path,
            "file_size": Path(db_path).stat().st_size,
        }

        if db_type == "sqlite":
            async with aiosqlite.connect(db_path) as conn:
                # Get SQLite-specific info
                async with conn.execute("PRAGMA page_count()") as cursor:
                    info["page_count"] = (await cursor.fetchone())[0]

                async with conn.execute("PRAGMA page_size()") as cursor:
                    info["page_size"] = (await cursor.fetchone())[0]

                async with conn.execute("PRAGMA encoding()") as cursor:
                    info["encoding"] = (await cursor.fetchone())[0]

                async with conn.execute("SELECT sqlite_version()") as cursor:
                    info["sqlite_version"] = (await cursor.fetchone())[0]

        return info
