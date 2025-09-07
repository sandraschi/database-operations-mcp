"""
Calibre Library Search Tools

Provides specialized search functionality for Calibre ebook libraries,
including full-text search within book content.
"""

import sqlite3
import logging
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, TypeVar, Callable

# Import the global MCP instance
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem
from database_operations_mcp.tools import init_tools as DATABASE_CONNECTIONS

# Type variable for function type
F = TypeVar('F', bound=Callable[..., Any])

logger = logging.getLogger(__name__)

def _get_fts_db_path(library_path: Union[str, Path]) -> Path:
    """Get the path to the full-text search database."""
    lib_path = Path(library_path)
    return lib_path / 'full-text-search.db'

@mcp.tool()
@HelpSystem.register_tool
async def search_calibre_library(
    query: str,
    library_path: str,
    search_fields: Optional[List[str]] = None,
    limit: int = 20,
    offset: int = 0,
) -> Dict[str, Any]:
    """Search a Calibre library for books matching the query.
    
    Args:
        query: Search query string
        library_path: Path to the Calibre library
        search_fields: Optional list of fields to search (title, author, tags, etc.)
        limit: Maximum number of results to return
        offset: Number of results to skip (for pagination)
        
    Returns:
        Dictionary containing search results and metadata
    """
    try:
        # Implementation of search_calibre_library
        # ... existing implementation ...
        return {
            'status': 'success',
            'results': [],  # Replace with actual results
            'total': 0,     # Replace with actual total
            'query': query,
            'library_path': str(library_path)
        }
    except Exception as e:
        logger.error(f"Error searching Calibre library: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': f"Failed to search Calibre library: {str(e)}",
            'error_type': type(e).__name__
        }

@mcp.tool()
@HelpSystem.register_tool
async def get_calibre_book_metadata(
    book_id: int,
    library_path: str
) -> Dict[str, Any]:
    """Get metadata for a specific Calibre book.
    
    Args:
        book_id: ID of the book in the Calibre library
        library_path: Path to the Calibre library
        
    Returns:
        Dictionary containing the book's metadata
    """
    try:
        # Implementation of get_calibre_book_metadata
        # ... existing implementation ...
        return {
            'status': 'success',
            'book_id': book_id,
            'metadata': {}  # Replace with actual metadata
        }
    except Exception as e:
        logger.error(f"Error getting book metadata: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': f"Failed to get book metadata: {str(e)}",
            'error_type': type(e).__name__
        }

@mcp.tool()
@HelpSystem.register_tool
async def search_calibre_fts(
    query: str,
    library_path: str,
    highlight: bool = True,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """Perform a full-text search in a Calibre library.
    
    Args:
        query: Search query string
        library_path: Path to the Calibre library
        highlight: Whether to include highlighted snippets in results
        limit: Maximum number of results to return
        offset: Number of results to skip (for pagination)
        
    Returns:
        Dictionary containing full-text search results and metadata
    """
    try:
        # Implementation of search_calibre_fts
        # ... existing implementation ...
        return {
            'status': 'success',
            'results': [],  # Replace with actual results
            'total': 0,     # Replace with actual total
            'query': query,
            'highlight': highlight
        }
    except Exception as e:
        logger.error(f"Error in Calibre FTS: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': f"Full-text search failed: {str(e)}",
            'error_type': type(e).__name__
        }

# Add other tool functions with @mcp.tool() decorator as needed
