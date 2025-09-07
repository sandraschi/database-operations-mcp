"""Advanced search functionality for bookmarks."""
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from collections import defaultdict

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from .db import FirefoxDB
from ..help_tools import HelpSystem

class BookmarkSearcher:
    """Handles bookmark search operations."""
    
    def __init__(self, profile_path: Optional[Path] = None):
        self.db = FirefoxDB(profile_path)
        
    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search bookmarks by title or URL."""
        search_term = f"%{query}%"
        query_sql = """
            SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified, b.parent
            FROM moz_bookmarks b
            JOIN moz_places p ON b.fk = p.id
            WHERE b.type = 1
            AND (b.title LIKE ? OR p.url LIKE ?)
            LIMIT ?
        """
        cursor = self.db.execute(query_sql, (search_term, search_term, limit))
        return [dict(row) for row in cursor.fetchall()]

@mcp.tool()
@HelpSystem.register_tool(category='firefox')
async def search_bookmarks(
    query: str,
    profile_path: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """Search bookmarks by title or URL."""
    try:
        searcher = BookmarkSearcher(Path(profile_path) if profile_path else None)
        results = searcher.search(query, limit)
        return {
            "status": "success",
            "query": query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool()
@HelpSystem.register_tool(category='firefox')
async def find_duplicates(
    by: str = 'url',  # 'url' or 'title'
    profile_path: Optional[Union[str, Path]] = None,
    min_duplicates: int = 2
) -> Dict[str, Any]:
    """Find duplicate bookmarks based on URL or title.
    
    Args:
        by: Field to check for duplicates ('url' or 'title')
        profile_path: Path to the Firefox profile directory
        min_duplicates: Minimum number of duplicates to report
        
    Returns:
        Dictionary with duplicate bookmarks grouped by the specified field
    """
    if by not in ('url', 'title'):
        return {
            "status": "error",
            "message": "'by' parameter must be either 'url' or 'title'"
        }
    
    try:
        db = FirefoxDB(Path(profile_path) if profile_path else None)
        
        # Query to find duplicates
        query = f"""
            SELECT p.{by}, GROUP_CONCAT(b.id) as ids, COUNT(*) as count
            FROM moz_bookmarks b
            JOIN moz_places p ON b.fk = p.id
            WHERE b.type = 1  -- Bookmarks
            GROUP BY p.{by}
            HAVING COUNT(*) >= ?
            ORDER BY count DESC, p.{by}
        """
        
        cursor = db.execute(query, (min_duplicates,))
        results = []
        
        for row in cursor.fetchall():
            item = dict(row)
            item['ids'] = [int(id_str) for id_str in item['ids'].split(',')]
            results.append(item)
        
        return {
            "status": "success",
            "by": by,
            "min_duplicates": min_duplicates,
            "count": len(results),
            "duplicates": results
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error finding duplicates: {str(e)}"
        }
    finally:
        if 'db' in locals():
            db.close()