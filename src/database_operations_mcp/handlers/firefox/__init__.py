"""Firefox bookmark management tools."""
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from fastmcp import FastMCP

# Create a FastMCP instance for tool registration
mcp = FastMCP("firefox_tools")

# Import core functionality
from .core import get_firefox_profiles

# Import bookmark management
from .bookmark_manager import list_bookmarks as bm_list_bookmarks, get_bookmark as bm_get_bookmark, add_bookmark, BookmarkManager

# Import tag management
from .tag_manager import list_tags, TagManager, find_similar_tags, merge_tags, clean_up_tags

# Import search functionality
from .search_tools import search_bookmarks, BookmarkSearcher, find_duplicates

# Import bulk operations
from .bulk_operations import export_bookmarks, batch_update_tags

# Import other tools
from .link_checker import find_broken_links
from .age_analyzer import find_old_bookmarks, get_bookmark_stats
from .folder_based_tagging import tag_from_folder, batch_tag_from_folder
from .year_based_tagging import tag_from_year, batch_tag_from_year
from .links import list_bookmarks, get_bookmark

# Category constant for help system
TOOL_CATEGORY = 'firefox'

# List of all tool functions to register
TOOLS = [
    bm_list_bookmarks,  # From bookmark_manager
    bm_get_bookmark,    # From bookmark_manager
    add_bookmark,
    list_tags,
    search_bookmarks,
    find_duplicates,
    export_bookmarks,
    batch_update_tags,
    find_broken_links,
    find_old_bookmarks,
    get_bookmark_stats,
    tag_from_folder,
    batch_tag_from_folder,
    tag_from_year,
    batch_tag_from_year,
    find_similar_tags,
    merge_tags,
    clean_up_tags,
    list_bookmarks,     # From links
    get_bookmark        # From links
]

def register_tools(mcp_instance: FastMCP):
    """Register all Firefox bookmark tools with the MCP server."""
    # Register all tools with the provided MCP instance
    for tool in TOOLS:
        if not hasattr(tool, '_mcp_registered'):
            mcp_instance.tool(tool)
            tool._mcp_registered = True

# Export all tools
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
    'batch_tag_from_year',
    'find_similar_tags',
    'merge_tags',
    'clean_up_tags',
    'find_duplicates',
    'mcp'  # Export the mcp instance
]