"""Core bookmark management functionality."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from .db import FirefoxDB
from fastmcp import tool

class BookmarkManager:
    """Handles bookmark operations."""
    
    def __init__(self, profile_path: Optional[Path] = None):
        self.db = FirefoxDB(profile_path)
        
    def get_bookmarks(self, folder_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve bookmarks, optionally filtered by folder."""
        query = """
            SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified, b.parent
            FROM moz_bookmarks b
            JOIN moz_places p ON b.fk = p.id
            WHERE b.type = 1
        """
        params = ()
        
        if folder_id is not None:
            query += " AND b.parent = ?"
            params = (folder_id,)
            
        cursor = self.db.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

@tool()
async def list_bookmarks(
    profile_path: Optional[str] = None,
    folder_id: Optional[int] = None
) -> Dict[str, Any]:
    """List bookmarks with optional folder filtering."""
    try:
        manager = BookmarkManager(Path(profile_path) if profile_path else None)
        bookmarks = manager.get_bookmarks(folder_id)
        return {
            "status": "success",
            "count": len(bookmarks),
            "bookmarks": bookmarks
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }