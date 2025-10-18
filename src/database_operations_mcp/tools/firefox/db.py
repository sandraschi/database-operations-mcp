"""Database connection management for Firefox bookmarks."""

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

from database_operations_mcp.config.mcp_config import mcp


class FirefoxDB:
    """Manages SQLite connections to Firefox bookmarks database."""

    def __init__(self, profile_path: Optional[Path] = None):
        self.profile_path = profile_path
        self.conn = None
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """Establish a read-only connection to the database."""
        try:
            if not self.profile_path or not self.profile_path.exists():
                return False

            db_path = self.profile_path / "places.sqlite"
            if not db_path.exists():
                return False

            self.conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            self.conn.row_factory = sqlite3.Row
            return True

        except sqlite3.Error as e:
            self.logger.error(f"Database connection failed: {e}")
            return False

    def execute(self, query: str, params: tuple = ()) -> Any:
        """Execute a read-only query."""
        if not self.conn:
            if not self.connect():
                raise ConnectionError("Failed to connect to database")

        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor
        except sqlite3.Error as e:
            self.logger.error(f"Query failed: {e}")
            raise

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None


@mcp.tool()
def test_firefox_database_connection(profile_path: str) -> Dict[str, Any]:
    """
    Test connection to Firefox bookmark database.
    
    Args:
        profile_path: Path to Firefox profile directory
        
    Returns:
        Dict containing connection test results
    """
    try:
        profile_path_obj = Path(profile_path)
        db = FirefoxDB(profile_path_obj)
        
        if db.connect():
            db.close()
            return {
                "success": True,
                "message": f"Successfully connected to Firefox database at {profile_path}",
                "database_path": str(profile_path_obj / "places.sqlite")
            }
        else:
            return {
                "success": False,
                "message": f"Failed to connect to Firefox database at {profile_path}",
                "database_path": str(profile_path_obj / "places.sqlite")
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error testing Firefox database connection: {e}"
        }


@mcp.tool()
def get_firefox_database_info(profile_path: str) -> Dict[str, Any]:
    """
    Get information about Firefox bookmark database.
    
    Args:
        profile_path: Path to Firefox profile directory
        
    Returns:
        Dict containing database information
    """
    try:
        profile_path_obj = Path(profile_path)
        db = FirefoxDB(profile_path_obj)
        
        if not db.connect():
            return {
                "success": False,
                "message": f"Cannot connect to Firefox database at {profile_path}"
            }
        
        # Get database schema info
        cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get bookmark count
        cursor = db.execute("SELECT COUNT(*) as count FROM moz_bookmarks")
        bookmark_count = cursor.fetchone()[0]
        
        # Get URL count
        cursor = db.execute("SELECT COUNT(*) as count FROM moz_places")
        url_count = cursor.fetchone()[0]
        
        db.close()
        
        return {
            "success": True,
            "profile_path": str(profile_path_obj),
            "database_path": str(profile_path_obj / "places.sqlite"),
            "tables": tables,
            "bookmark_count": bookmark_count,
            "url_count": url_count,
            "message": f"Database contains {bookmark_count} bookmarks and {url_count} URLs"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error getting Firefox database info: {e}"
        }
