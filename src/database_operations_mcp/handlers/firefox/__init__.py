"""Firefox bookmark management tools."""
from pathlib import Path
from typing import Dict, Any, Optional
from fastmcp import FastMCP

# Import core functionality
from .core import get_firefox_profiles

# Import bookmark management
from .bookmark_manager import list_bookmarks, get_bookmark, add_bookmark, BookmarkManager

# Import tag management
from .tag_manager import list_tags, TagManager

# Import search functionality
from .search_tools import search_bookmarks, BookmarkSearcher

# Import bulk operations
from .bulk_operations import export_bookmarks, batch_update_tags

# Import other tools
from .link_checker import find_broken_links
from .age_analyzer import find_old_bookmarks, get_bookmark_stats
from .folder_based_tagging import tag_from_folder, batch_tag_from_folder
from .year_based_tagging import tag_from_year, batch_tag_from_year

# Category constant for help system
TOOL_CATEGORY = 'firefox'

__all__ = [
    'get_firefox_profiles',
    'list_bookmarks',
    'get_bookmark',
    'add_bookmark',
    'BookmarkManager',
    'list_tags',
    'TagManager',
    'search_bookmarks',
    'BookmarkSearcher',
    'export_bookmarks',
    'batch_update_tags',
    'find_broken_links',
    'find_old_bookmarks',
    'get_bookmark_stats',
    'tag_from_folder',
    'batch_tag_from_folder',
    'tag_from_year',
    'batch_tag_from_year'
]

def register_tools(mcp: FastMCP):
    """Register all Firefox bookmark tools with the MCP server."""
    # The actual registration is handled by the @mcp.tool decorator
    # on each individual function
    pass