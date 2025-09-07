"""Firefox bookmark management tools."""
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp

# Import core functionality
from .core import get_firefox_profiles

# Import bookmark management
from .links import list_bookmarks as bm_list_bookmarks, get_bookmark as bm_get_bookmark, add_bookmark

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

# Category constant for help system
TOOL_CATEGORY = 'firefox'


# Tools are registered using the @mcp.tool() decorator in their respective modules
# The mcp instance is imported from the central config

# Export all tools
__all__ = [
    'get_firefox_profiles',
    'list_bookmarks',
    'get_bookmark',
    'add_bookmark',
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