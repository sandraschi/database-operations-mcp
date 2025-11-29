"""
Media Server Tools

DEPRECATED: This module is deprecated. Use media_library portmanteau tool instead.

All operations have been consolidated into media_library():
- find_plex_database() → media_library(operation='find_plex_database')
- optimize_plex_database() → media_library(operation='optimize_plex_database')
- export_database_schema() → media_library(operation='export_database_schema')
- get_plex_library_stats() → media_library(operation='get_plex_library_stats')

This module is kept for backwards compatibility but tools are no longer registered.
"""

import csv
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

# NOTE: @mcp.tool decorators removed - functionality moved to media_library portmanteau

logger = logging.getLogger(__name__)


def register_tools(mcp):
    """Register all media tools with the MCP server."""
    pass  # Tools are registered via decorators


# DEPRECATED: Use media_library(operation='find_plex_database') instead
async def find_plex_database(custom_path: str | None = None) -> dict[str, Any]:
    """Locate the Plex Media Server database file.

    Args:
        custom_path: Optional custom path to check first

    Returns:
        Dictionary with database path and metadata if found
    """
    import os
    import platform
    from pathlib import Path

    # Check custom path first if provided
    if custom_path:
        custom_path = Path(os.path.expandvars(os.path.expanduser(custom_path)))
        if custom_path.exists():
            return {
                "status": "success",
                "path": str(custom_path.absolute()),
                "source": "custom_path",
                "size_mb": custom_path.stat().st_size / (1024 * 1024),
            }

    # Determine OS and check common locations
    system = platform.system().lower()
    if "windows" in system:
        paths = PLEX_DB_PATHS["windows"]
    elif "linux" in system:
        paths = PLEX_DB_PATHS["linux"]
    elif "darwin" in system:
        paths = PLEX_DB_PATHS["macos"]
    else:
        return {"status": "error", "message": "Unsupported operating system"}

    # Check each potential path
    for path in paths:
        expanded_path = Path(os.path.expandvars(os.path.expanduser(path)))
        if expanded_path.exists():
            return {
                "status": "success",
                "path": str(expanded_path.absolute()),
                "source": "auto_detected",
                "size_mb": expanded_path.stat().st_size / (1024 * 1024),
            }

        return {"status": "not_found", "message": "Plex database not found in common locations"}


# DEPRECATED: Use media_library portmanteau instead
async def optimize_plex_database(
    db_path: str = None, vacuum: bool = True, analyze: bool = True, backup: bool = True
) -> dict[str, Any]:
    """Optimize the Plex Media Server database.

    Args:
        db_path: Path to the Plex database (auto-detected if not provided)
        vacuum: Whether to run VACUUM to rebuild the database
        analyze: Whether to update query planner statistics
        backup: Whether to create a backup before optimization

    Returns:
        Dictionary with optimization results
    """
    # Find the database if path not provided
    if not db_path:
        db_info = await find_plex_database()
        if db_info["status"] != "success":
            return db_info
        db_path = db_info["path"]

    # Create backup if requested
    backup_path = None
    if backup:
        backup_path = f"{db_path}.{int(datetime.now().timestamp())}.bak"
        import shutil

        shutil.copy2(db_path, backup_path)

    try:
        # Connect to the database
        conn = sqlite3.connect(f"file:{db_path}?mode=rw", uri=True)
        cursor = conn.cursor()

        # Get current size
        original_size = Path(db_path).stat().st_size

        # Run optimization commands
        if vacuum:
            cursor.execute("VACUUM")

        if analyze:
            cursor.execute("ANALYZE")

        # Get new size
        new_size = Path(db_path).stat().st_size

        return {
            "status": "success",
            "original_size_mb": original_size / (1024 * 1024),
            "new_size_mb": new_size / (1024 * 1024),
            "space_saved_mb": (original_size - new_size) / (1024 * 1024),
            "backup_created": backup_path is not None,
            "backup_path": backup_path,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "backup_created": backup_path is not None,
            "backup_path": backup_path,
        }

    finally:
        if "conn" in locals():
            conn.close()


# DEPRECATED: Use media_library portmanteau instead
async def export_database_schema(
    db_path: str,
    output_format: str = "sql",
    output_file: str | None = None,
    include_data: bool = False,
    tables: list[str] | None = None,
) -> dict[str, Any]:
    """Export database schema and optionally data to a file.

    Args:
        db_path: Path to the database file
        output_format: Output format (sql, json, csv)
        output_file: Output file path (defaults to [db_name]_schema.[format])
        include_data: Whether to include table data
        tables: List of tables to export (all if None)

    Returns:
        Dictionary with export results
    """
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        all_tables = [row[0] for row in cursor.fetchall()]

        # Filter tables if specified
        if tables:
            tables = [t for t in tables if t in all_tables]
        else:
            tables = all_tables

        # Generate output filename if not provided
        if not output_file:
            db_name = Path(db_path).stem
            output_file = f"{db_name}_schema.{output_format}"

        # Export based on format
        if output_format == "sql":
            _export_to_sql(cursor, tables, output_file, include_data)
        elif output_format == "json":
            _export_to_json(cursor, tables, output_file, include_data)
        elif output_format == "csv":
            _export_to_csv(cursor, tables, output_file, include_data)
        else:
            return {"status": "error", "message": f"Unsupported format: {output_format}"}

        return {
            "status": "success",
            "output_file": output_file,
            "tables_exported": len(tables),
            "format": output_format,
            "include_data": include_data,
            "file_size_mb": Path(output_file).stat().st_size / (1024 * 1024),
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        if "conn" in locals():
            conn.close()


# DEPRECATED: Use media_library portmanteau instead
async def get_plex_library_stats(
    db_path: str | None = None, detailed: bool = False
) -> dict[str, Any]:
    """Get statistics about the Plex library.

    Args:
        db_path: Path to the Plex database (auto-detected if not provided)
        detailed: Whether to include detailed statistics

    Returns:
        Dictionary with library statistics
    """
    # Find the database if path not provided
    if not db_path:
        db_info = await find_plex_database()
        if db_info["status"] != "success":
            return db_info
        db_path = db_info["path"]

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        stats = {}

        # Basic library stats
        cursor.execute("SELECT COUNT(*) FROM metadata_items WHERE library_section_id IS NOT NULL")
        stats["total_items"] = cursor.fetchone()[0]

        cursor.execute("""
            SELECT library_section_id, COUNT(*) as count
            FROM metadata_items
            WHERE library_section_id IS NOT NULL
            GROUP BY library_section_id
        """)
        stats["items_by_section"] = dict(cursor.fetchall())

        if detailed:
            # Detailed media stats
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN bitrate > 0 THEN 1 ELSE 0 END) as has_bitrate,
                    SUM(CASE WHEN duration > 0 THEN 1 ELSE 0 END) as has_duration,
                    SUM(CASE WHEN width > 0 THEN 1 ELSE 0 END) as has_dimensions
                FROM media_parts
                JOIN media_items ON media_items.id = media_parts.media_item_id
            """)

            media_stats = cursor.fetchone()
            stats["media"] = {
                "total_media_files": media_stats[0],
                "with_bitrate": media_stats[1],
                "with_duration": media_stats[2],
                "with_dimensions": media_stats[3],
            }

            # Recently added items
            cursor.execute("""
                SELECT title, added_at
                FROM metadata_items
                WHERE library_section_id IS NOT NULL
                ORDER BY added_at DESC
                LIMIT 10
            """)
            stats["recently_added"] = [
                {"title": row[0], "added_at": row[1]} for row in cursor.fetchall()
            ]

        return {"status": "success", "stats": stats, "database": db_path}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        if "conn" in locals():
            conn.close()


# Common Plex database locations for different OS
PLEX_DB_PATHS = {
    "windows": [
        r"%LOCALAPPDATA%\\Plex Media Server\\Plug-in Support\\"
        r"Databases\\com.plexapp.plugins.library.db",
        r"C:\\Plex\\Plex Media Server\\Plug-in Support\\Databases\\com.plexapp.plugins.library.db",
    ],
    "linux": [
        "/var/lib/plexmediaserver/Library/Application Support/"
        "Plex Media Server/Plug-in Support/Databases/"
        "com.plexapp.plugins.library.db",
        "~/Library/Application Support/Plex Media Server/"
        "Plug-in Support/Databases/com.plexapp.plugins.library.db",
    ],
    "macos": [
        "~/Library/Application Support/Plex Media Server/"
        "Plug-in Support/Databases/com.plexapp.plugins.library.db"
    ],
}


def _export_to_sql(cursor, tables, output_file, include_data):
    """Export database schema and data to SQL format.

    Args:
        cursor: Database cursor
        tables: List of tables to export
        output_file: Output file path
        include_data: Whether to include table data
    """
    with open(output_file, "w", encoding="utf-8") as f:
        for table in tables:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,))
            schema = cursor.fetchone()[0]
            f.write(f"{schema};\n\n")

            if include_data:
                cursor.execute(f"SELECT * FROM {table}")
                columns = [desc[0] for desc in cursor.description]

                for row in cursor:
                    values = []
                    for value in row:
                        if value is None:
                            values.append("NULL")
                        elif isinstance(value, (int, float)):
                            values.append(str(value))
                        else:
                            # Escape single quotes by doubling them for SQL
                            escaped_value = str(value).replace("'", "''")
                            values.append(f"'{escaped_value}'")

                    f.write(
                        f"INSERT INTO {table} ({', '.join(columns)}) "
                        f"VALUES ({', '.join(values)});\n"
                    )

                f.write("\n")


def _export_to_json(cursor, tables, output_file, include_data):
    """Export database schema and data to JSON format.

    Args:
        cursor: Database cursor
        tables: List of tables to export
        output_file: Output file path
        include_data: Whether to include table data
    """
    result = {}
    for table in tables:
        cursor.execute(f"SELECT * FROM {table} LIMIT 0")
        columns = [desc[0] for desc in cursor.description]

        if include_data:
            cursor.execute(f"SELECT * FROM {table}")
            result[table] = [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]
        else:
            result[table] = {
                "columns": columns,
                "row_count": cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0],
            }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


def _export_to_csv(cursor, tables, output_file, include_data):
    """Export database schema and data to CSV format.

    Args:
        cursor: Database cursor
        tables: List of tables to export
        output_file: Output file path
        include_data: Whether to include table data
    """
    from pathlib import Path

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    for table in tables:
        cursor.execute(f"SELECT * FROM {table} LIMIT 0")
        columns = [desc[0] for desc in cursor.description]

        with open(
            Path(output_file).parent / f"{table}.csv", "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow(columns)

            if include_data:
                cursor.execute(f"SELECT * FROM {table}")
                writer.writerows(cursor)
