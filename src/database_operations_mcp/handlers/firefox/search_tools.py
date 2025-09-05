"""Advanced search functionality for bookmarks."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from . import mcp  # Import the mcp instance from __init__
from .db import FirefoxDB

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

@mcp.tool
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