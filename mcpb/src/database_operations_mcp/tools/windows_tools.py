"""
Windows-Specific Database Tools

DEPRECATED: This module is deprecated. Use windows_system portmanteau tool instead.

All operations have been consolidated into windows_system():
- list_windows_databases() → windows_system(operation='list_windows_databases')
- manage_plex_metadata() → windows_system(operation='manage_plex_metadata')
- query_windows_database() → windows_system(operation='query_windows_database')
- clean_windows_database() → windows_system(operation='clean_windows_database')

This module is kept for backwards compatibility but tools are no longer registered.
"""

import logging
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from fastmcp import FastMCP
from ..tools.firefox.status import FirefoxStatusChecker
from .help_tools import HelpSystem

# Common Windows database locations
WINDOWS_DB_PATHS = {
    "chrome_history": [
        os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\History"),
        os.path.expandvars(
            r"%USERPROFILE%\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"
        ),
    ],
    "firefox_history": [
        os.path.expandvars(r"%APPDATA%\\Mozilla\\Firefox\\Profiles"),
    ],
    "edge_history": [
        os.path.expandvars(r"%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Default\\History"),
        os.path.expandvars(
            r"%USERPROFILE%\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History"
        ),
    ],
    "brave_history": [
        os.path.expandvars(
            r"%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\User Data\\Default\\History"
        ),
        os.path.expandvars(
            r"%USERPROFILE%\\AppData\\Local\\BraveSoftware\\Brave-Browser\\"
            r"User Data\\Default\\History"
        ),
    ],
    "outlook": [
        os.path.expandvars(r"%LOCALAPPDATA%\\Microsoft\\Outlook"),
        os.path.expandvars(r"%USERPROFILE%\\AppData\\Local\\Microsoft\\Outlook"),
    ],
    "windows_thumbnails": [os.path.expandvars(r"%LOCALAPPDATA%\\Microsoft\\Windows\\Explorer")],
}

# Plex-specific paths
PLEX_PATHS = {
    "metadata": [
        os.path.expandvars(r"%LOCALAPPDATA%\\Plex Media Server\\Metadata"),
        r"C:\\Plex\\Plex Media Server\\Metadata",
        os.path.expandvars(
            r"%LOCALAPPDATA%\\Plex Media Server\\Plug-in Support\\"
            r"Databases\\com.plexapp.plugins.library.db"
        ),
    ],
    "cache": [
        os.path.expandvars(r"%LOCALAPPDATA%\\Plex Media Server\\Cache"),
        r"C:\\Plex\\Plex Media Server\\Cache",
    ],
    "logs": [
        os.path.expandvars(r"%LOCALAPPDATA%\\Plex Media Server\\Logs"),
        r"C:\\Plex\\Plex Media Server\\Logs",
    ],
}


def _find_windows_db(db_type: str) -> Path | None:
    """Find a Windows database file by type."""
    for path in WINDOWS_DB_PATHS.get(db_type, []):
        try:
            if db_type == "firefox_history":
                # Special handling for Firefox profiles directory
                profiles_path = Path(path)
                if profiles_path.exists() and profiles_path.is_dir():
                    # Look for profile directories and find places.sqlite
                    profile_candidates = []
                    for profile_dir in profiles_path.iterdir():
                        if profile_dir.is_dir():
                            places_db = profile_dir / "places.sqlite"
                            if places_db.exists():
                                # Prioritize default-release, then default, then others
                                priority = 0
                                if profile_dir.name.endswith(".default-release"):
                                    priority = 2
                                elif profile_dir.name.endswith(".default"):
                                    priority = 1
                                profile_candidates.append((priority, places_db))

                    if profile_candidates:
                        # Return the highest priority profile
                        profile_candidates.sort(key=lambda x: x[0], reverse=True)
                        return profile_candidates[0][1]
            else:
                db_path = Path(path)
                if db_path.exists():
                    return db_path
        except (PermissionError, OSError) as e:
            # Skip paths we can't access due to permissions
            logger.debug(f"Skipping {db_type} path {path} due to permission error: {e}")
            continue
    return None


def register_tools(mcp: "FastMCP") -> None:
    """Register all Windows tools with the MCP server.

    Args:
    mcp: The FastMCP instance to register tools with
    """


# DEPRECATED: Use windows_system portmanteau instead
@HelpSystem.register_tool
async def list_windows_databases(bruteforce_firefox: bool = False) -> dict[str, Any]:
    """List all discoverable Windows databases with their locations and sizes.

    Args:
        bruteforce_firefox: If True, attempt to access Firefox database even when locked
                           using dirty tricks (file copying, SQLite URI tricks, etc.)

    Returns:
    Dictionary containing database information
    """
    result = {}
    for db_type, paths in WINDOWS_DB_PATHS.items():
        try:
            # Special handling for Firefox - check if it's running
            if db_type == "firefox_history":
                firefox_status = FirefoxStatusChecker.is_firefox_running()
                if firefox_status["is_running"] and not bruteforce_firefox:
                    result[db_type] = {
                        "path": paths[0] if isinstance(paths, (list, tuple)) else paths,
                        "exists": False,
                        "error": "Firefox is running - database is locked",
                        "firefox_status": firefox_status,
                        "solution": (
                            "Close Firefox completely and try again, or set bruteforce_firefox=True"
                        ),
                    }
                    continue
                elif firefox_status["is_running"] and bruteforce_firefox:
                    # Try brute force access
                    from ..firefox.core import FirefoxDatabaseUnlocker

                    db_path = _find_windows_db(db_type)
                    if db_path:
                        conn, method = FirefoxDatabaseUnlocker.get_database_connection_bruteforce(
                            db_path
                        )
                        if conn:
                            try:
                                # Get database size
                                size_mb = os.path.getsize(db_path) / (1024 * 1024)
                                # Get some stats
                                cursor = conn.cursor()
                                cursor.execute("SELECT COUNT(*) FROM moz_places")
                                places_count = cursor.fetchone()[0]
                                cursor.close()

                                result[db_type] = {
                                    "path": str(db_path),
                                    "size_mb": round(size_mb, 2),
                                    "exists": True,
                                    "bruteforce_access": True,
                                    "access_method": method,
                                    "firefox_running": True,
                                    "places_count": places_count,
                                }
                            finally:
                                # Clean up
                                if hasattr(conn, "temp_db_path"):
                                    try:
                                        conn.temp_db_path.unlink(missing_ok=True)
                                    except Exception:
                                        pass
                                conn.close()
                        else:
                            result[db_type] = {
                                "path": str(db_path),
                                "exists": False,
                                "error": f"Brute force access failed: {method}",
                                "firefox_running": True,
                                "bruteforce_attempted": True,
                            }
                    continue

            db_path = _find_windows_db(db_type)
            if db_path and os.path.exists(db_path):
                try:
                    size_mb = os.path.getsize(db_path) / (1024 * 1024)
                    result[db_type] = {
                        "path": str(db_path),
                        "size_mb": round(size_mb, 2),
                        "exists": True,
                    }
                except (PermissionError, OSError) as e:
                    logger.warning(f"Permission error accessing {db_type}: {e}")
                    result[db_type] = {
                        "path": str(db_path),
                        "error": "Permission denied",
                        "exists": False,
                    }
            else:
                result[db_type] = {
                    "path": paths[0] if isinstance(paths, (list, tuple)) else paths,
                    "exists": False,
                }
        except Exception as e:
            logger.error(f"Error processing {db_type}: {e}")
            result[db_type] = {
                "path": paths[0] if isinstance(paths, (list, tuple)) else paths,
                "exists": False,
                "error": str(e),
            }

    return {"status": "success", "databases": result}


# DEPRECATED: Use windows_system portmanteau instead
@HelpSystem.register_tool
async def manage_plex_metadata(
    action: str = "analyze",
    library_section: str | None = None,
    item_id: int | None = None,
    refresh: bool = False,
) -> dict[str, Any]:
    """Manage Plex metadata for media items.

    Args:
        action: Action to perform (analyze, refresh, delete, export)
        library_section: Optional library section ID or name
        item_id: Optional specific item ID
        refresh: Whether to refresh metadata from online sources

    Returns:
        Dictionary with operation results
    """
    plex_path = _find_windows_db("plex")
    if not plex_path or not os.path.exists(plex_path):
        return {"status": "error", "message": "Plex database not found"}

    try:
        conn = sqlite3.connect(f"file:{plex_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

        if action == "analyze":
            # Analyze database and return statistics
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as total_items,
                       (SELECT COUNT(*) FROM metadata_items WHERE metadata_type = 1) as movies,
                       (SELECT COUNT(*) FROM metadata_items WHERE metadata_type = 2) as shows,
                       (SELECT COUNT(*) FROM metadata_items WHERE metadata_type = 4) as seasons,
                       (SELECT COUNT(*) FROM metadata_items 
                        WHERE metadata_type = 4 AND parent_id IS NULL) as orphaned_seasons,
                       (SELECT COUNT(*) FROM metadata_items 
                        WHERE metadata_type = 4 AND parent_id IS NOT NULL) as valid_seasons,
                       (SELECT COUNT(*) FROM metadata_items 
                        WHERE metadata_type = 4 AND parent_id NOT IN 
                        (SELECT id FROM metadata_items WHERE metadata_type = 2)) as invalid_seasons,
                       (SELECT COUNT(*) FROM metadata_items 
                        WHERE metadata_type = 4 AND parent_id IS NULL) as orphaned_episodes,
                       (SELECT COUNT(*) FROM metadata_items 
                        WHERE metadata_type = 4 AND parent_id IS NOT NULL) as valid_episodes,
                       (SELECT COUNT(*) FROM metadata_items 
                        WHERE metadata_type = 4 AND parent_id NOT IN 
                        (SELECT id FROM metadata_items WHERE metadata_type = 4)) as invalid_episodes
                FROM metadata_items
            """)
            stats = dict(cursor.fetchone())

            # Add library section information
            cursor.execute("""
                SELECT id, section_name, section_type, 
                       (SELECT COUNT(*) FROM metadata_items 
                        WHERE library_section_id = library_sections.id) as item_count
                FROM library_sections
                ORDER BY section_name
            """)
            sections = [dict(row) for row in cursor.fetchall()]

            return {
                "status": "success",
                "database": str(plex_path),
                "stats": stats,
                "sections": sections,
            }

        elif action == "export":
            # Export metadata to a JSON file
            cursor = conn.cursor()
            query = """
                SELECT mi.*, ls.section_name 
                FROM metadata_items mi
                LEFT JOIN library_sections ls ON mi.library_section_id = ls.id
            """

            if item_id:
                query += " WHERE mi.id = ?"
                cursor.execute(query, (item_id,))
            elif library_section:
                query += " WHERE ls.section_name = ? OR ls.id = ?"
                cursor.execute(query, (library_section, library_section))
            else:
                cursor.execute(query)

            items = [dict(row) for row in cursor.fetchall()]
            return {"status": "success", "count": len(items), "items": items}

        else:
            return {"status": "error", "message": f"Unsupported action: {action}"}

    except Exception as e:
        logger.exception("Error managing Plex metadata")
        return {"status": "error", "message": str(e)}

    finally:
        if "conn" in locals():
            conn.close()


# DEPRECATED: Use windows_system portmanteau instead
@HelpSystem.register_tool
async def query_windows_database(
    db_type: str,
    query: str,
    params: dict | None = None,
    limit: int = 100,
    bruteforce_firefox: bool = False,
) -> dict[str, Any]:
    """Execute a query against a Windows database.

    Args:
        db_type: Type of database (chrome_history, firefox_history, etc.)
        query: SQL query to execute
        params: Optional query parameters
        limit: Maximum number of results to return
        bruteforce_firefox: If True, attempt to access Firefox database even when locked

    Returns:
        Query results and metadata
    """
    # Check Firefox status for Firefox databases
    if db_type == "firefox_history":
        firefox_status = FirefoxStatusChecker.is_firefox_running()
        if firefox_status["is_running"] and not bruteforce_firefox:
            return {
                "status": "error",
                "message": "Firefox is running - database is locked",
                "firefox_status": firefox_status,
                "solution": (  # noqa: E501
                    "Close Firefox completely and try again, or set bruteforce_firefox=True"
                ),
            }

    db_path = _find_windows_db(db_type)
    if not db_path or not os.path.exists(db_path):
        return {"status": "error", "message": f"Database not found: {db_type}"}

    if params is None:
        params = {}

    try:
        # Add limit to query if not already present
        if "LIMIT" not in query.upper() and limit > 0:
            query = query.rstrip(";") + f" LIMIT {limit}"

        # Use brute force connection for Firefox when requested
        if db_type == "firefox_history" and bruteforce_firefox:
            from ..firefox.core import FirefoxDatabaseUnlocker

            conn, method = FirefoxDatabaseUnlocker.get_database_connection_bruteforce(db_path)
            if not conn:
                return {
                    "status": "error",
                    "message": f"Brute force access failed: {method}",
                    "db_type": db_type,
                    "bruteforce_attempted": True,
                }
            # Store method info for response
            bruteforce_method_used = method
        else:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(query, params)

        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        # Fetch results with limit
        rows = cursor.fetchmany(limit) if limit > 0 else cursor.fetchall()

        # Convert rows to dictionaries
        results = []
        for row in rows:
            if isinstance(row, sqlite3.Row):
                results.append(dict(zip(columns, row, strict=False)))
            else:
                results.append(row)

        response = {
            "status": "success",
            "database": db_type,
            "path": str(db_path),
            "query": query,
            "params": params,
            "columns": columns,
            "count": len(results),
            "results": results,
        }

        # Add brute force info if used
        if (
            db_type == "firefox_history"
            and bruteforce_firefox
            and "bruteforce_method_used" in locals()
        ):
            response["bruteforce_access"] = True
            response["access_method"] = bruteforce_method_used

        return response

    except Exception as e:
        logger.exception(f"Error querying {db_type} database")
        return {"status": "error", "database": db_type, "query": query, "error": str(e)}

    finally:
        if "conn" in locals():
            conn.close()


# DEPRECATED: Use windows_system portmanteau instead
@HelpSystem.register_tool
async def clean_windows_database(
    db_type: str, action: str = "vacuum", backup: bool = True, bruteforce_firefox: bool = False
) -> dict[str, Any]:
    """Clean and optimize a Windows database.

    Args:
        db_type: Type of database to clean
        action: Action to perform (vacuum, reindex, analyze)
        backup: Whether to create a backup before cleaning
        bruteforce_firefox: If True, attempt to access Firefox database
        even when locked (dangerous!)

    Returns:
        Dictionary with cleaning results
    """
    # Check Firefox status for Firefox databases
    if db_type == "firefox_history":
        firefox_status = FirefoxStatusChecker.is_firefox_running()
        if firefox_status["is_running"] and not bruteforce_firefox:
            return {
                "status": "error",
                "message": "Firefox is running - database is locked",
                "firefox_status": firefox_status,
                "solution": "Close Firefox completely, or use bruteforce_firefox=True (dangerous!)",
            }

    db_path = _find_windows_db(db_type)
    if not db_path or not os.path.exists(db_path):
        return {"status": "error", "message": f"Database not found: {db_type}"}

    if action not in ["vacuum", "reindex", "analyze"]:
        return {"status": "error", "message": f"Invalid action: {action}"}

    backup_path = None
    if backup:
        backup_dir = os.path.join(os.path.dirname(db_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{db_type}_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        try:
            shutil.copy2(db_path, backup_path)
        except Exception as e:
            logger.exception(f"Failed to create backup of {db_type}")
            return {"status": "error", "message": f"Backup failed: {str(e)}"}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if action == "vacuum":
            cursor.execute("VACUUM")
            message = "Database vacuum completed"
        elif action == "reindex":
            cursor.execute("REINDEX")
            message = "Database reindexing completed"
        elif action == "analyze":
            cursor.execute("ANALYZE")
            message = "Database analysis completed"

        conn.commit()

        # Get database stats after operation
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()

        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]

        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]

        return {
            "status": "success",
            "action": action,
            "database": db_type,
            "path": str(db_path),
            "backup_created": bool(backup_path),
            "backup_path": str(backup_path) if backup_path else None,
            "integrity_check": integrity[0] if integrity else "unknown",
            "size_mb": (page_count * page_size) / (1024 * 1024),
        }

    except Exception as e:
        logger.exception(f"Error during database {action}")
        return {"status": "error", "database": db_type, "action": action, "error": str(e)}

    finally:
        if "conn" in locals():
            conn.close()


# Set up logging
logger = logging.getLogger(__name__)
