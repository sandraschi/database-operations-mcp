"""Firefox bookmark management tools."""
from pathlib import Path
from typing import Dict, Any, Optional
from fastmcp import tool
from .core import get_firefox_profiles
from .bookmark_manager import list_bookmarks, get_bookmark, add_bookmark, BookmarkManager
from .tag_manager import list_tags, TagManager
from .search_tools import search_bookmarks, BookmarkSearcher
from .bulk_operations import export_bookmarks, batch_update_tags
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
    'list_tags',
    'search_bookmarks',
    'export_bookmarks',
    'batch_update_tags',
    'find_broken_links',
    'find_old_bookmarks',
    'get_bookmark_stats',
    'BookmarkManager',
    'TagManager',  
    'tag_from_folder',
    'batch_tag_from_folder',
    'tag_from_year',
    'batch_tag_from_year',
    'BookmarkSearcher'
]

def register_tools(mcp):
    """Register all Firefox bookmark tools with the MCP server."""
    tools = [
        list_bookmarks,
        get_bookmark,
        add_bookmark,
        list_tags,
        search_bookmarks,
        export_bookmarks,
        batch_update_tags,
        find_broken_links,
        find_old_bookmarks,
        tag_from_folder,
        batch_tag_from_folder,
        tag_from_year,
        batch_tag_from_year,
        get_bookmark_stats
    ]
    
    for tool_func in tools:
        mcp.register_tool(tool_func)
    
    return mcp