"""
Database content analysis service.

This module provides functionality to analyze database contents including
pattern detection, data distributions, value statistics, and content sampling.
"""

import re
from typing import Any

import aiosqlite


class ContentAnalyzer:
    """Analyze database contents and patterns.

    Provides content analysis capabilities including data sampling, pattern
    detection, value distributions, and content statistics.
    """

    def __init__(self):
        """Initialize content analyzer."""
        self.patterns = {
            "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
            "url": re.compile(
                r"^https?://[^\s/$.?#].[^\s]*$",
                re.IGNORECASE,
            ),
            "phone": re.compile(r"^\+?[\d\s\-\(\)]+$"),
            "iso8601_date": re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", re.IGNORECASE),
            "unix_timestamp": re.compile(r"^\d{10,11}$"),
        }

    async def sample_content(
        self, db_path: str, table_name: str, limit: int = 10
    ) -> dict[str, Any]:
        """Get sample data from a table.

        Retrieves a representative sample of rows from the table for analysis
        and preview purposes.

        Args:
            db_path: Path to database file
            table_name: Name of table to sample
            limit: Number of sample rows to return

        Returns:
            Dictionary containing sample data and statistics:
                {
                    'table_name': str,
                    'row_count': int,
                    'sample_rows': List[Dict],
                    'column_statistics': {...}
                }
        """
        async with aiosqlite.connect(db_path) as conn:
            # Get total row count
            async with conn.execute(f'SELECT COUNT(*) FROM "{table_name}"') as cursor:
                row_count = (await cursor.fetchone())[0]

            # Get sample rows
            async with conn.execute(f'SELECT * FROM "{table_name}" LIMIT ?', (limit,)) as cursor:
                column_names = [desc[0] for desc in cursor.description]
                rows = []
                for row in await cursor.fetchall():
                    rows.append(dict(zip(column_names, row, strict=False)))

            # Analyze columns
            column_stats = {}
            if rows:
                for col_name in column_names:
                    values = [row[col_name] for row in rows if row[col_name] is not None]
                    column_stats[col_name] = {
                        "null_count": sum(1 for row in rows if row[col_name] is None),
                        "non_null_count": len(values),
                        "unique_values": len(set(str(v) for v in values)),
                        "sample_values": list(set(str(v) for v in values[:5])),
                    }

            return {
                "table_name": table_name,
                "row_count": row_count,
                "sample_rows": rows,
                "column_statistics": column_stats,
            }

    async def detect_patterns(self, db_path: str, table_name: str) -> dict[str, Any]:
        """Detect data patterns in table columns.

        Analyzes column values to detect common patterns like emails, URLs,
        phone numbers, dates, etc.

        Args:
            db_path: Path to database file
            table_name: Name of table to analyze

        Returns:
            Dictionary containing detected patterns for each column
        """
        sample = await self.sample_content(db_path, table_name, limit=100)
        patterns = {}

        for col_name, stats in sample["column_statistics"].items():
            detected_patterns = []
            sample_values = stats["sample_values"]

            for value in sample_values:
                for pattern_name, pattern_regex in self.patterns.items():
                    if pattern_regex.match(value):
                        detected_patterns.append(pattern_name)
                        break

            if detected_patterns:
                patterns[col_name] = {
                    "detected_patterns": list(set(detected_patterns)),
                    "confidence": len(set(detected_patterns)) / len(sample_values)
                    if sample_values
                    else 0,
                    "sample_values": sample_values,
                }

        return patterns

    async def analyze_distributions(self, db_path: str, table_name: str) -> dict[str, Any]:
        """Analyze value distributions in table.

        Provides statistics about value distributions including unique counts,
        null counts, value ranges, and data types.

        Args:
            db_path: Path to database file
            table_name: Name of table to analyze

        Returns:
            Dictionary containing distribution analysis
        """
        sample = await self.sample_content(db_path, table_name, limit=1000)
        distributions = {}

        for col_name, stats in sample["column_statistics"].items():
            distributions[col_name] = {
                "unique_value_count": stats["unique_values"],
                "null_count": stats["null_count"],
                "non_null_count": stats["non_null_count"],
                "unique_ratio": stats["unique_values"] / stats["non_null_count"]
                if stats["non_null_count"] > 0
                else 0,
                "sample_unique_values": stats["sample_values"][:10],
            }

        return distributions

    async def infer_relationships(self, db_path: str) -> list[dict[str, Any]]:
        """Infer relationships between tables.

        Attempts to detect potential foreign key relationships by analyzing
        column names, value ranges, and naming patterns.

        Args:
            db_path: Path to database file

        Returns:
            List of inferred relationships
        """
        relationships = []

        async with aiosqlite.connect(db_path) as conn:
            # Get all tables
            async with conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ) as cursor:
                tables = [row[0] for row in await cursor.fetchall()]

            # Analyze potential relationships
            for table_name in tables:
                async with conn.execute(f'PRAGMA table_info("{table_name}")') as cursor:
                    columns = await cursor.fetchall()

                    for col in columns:
                        col_name = col[1].lower()

                        # Check for potential foreign key patterns
                        if col_name.endswith("_id") or col_name.endswith("id"):
                            potential_ref_table = col_name.replace("_id", "").replace("id", "")

                            if potential_ref_table in tables:
                                relationships.append(
                                    {
                                        "from_table": table_name,
                                        "from_column": col[1],
                                        "to_table": potential_ref_table,
                                        "to_column": "id",
                                        "relationship_type": "potential_foreign_key",
                                        "confidence": 0.7,
                                    }
                                )

        return relationships
