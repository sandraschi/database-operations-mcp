"""
Database Operations MCP - Tools Package

This package contains all the tool modules for the Database Operations MCP,
organized into logical modules for better maintainability.

Modules:
    - calibre_tools: Tools for working with Calibre libraries
    - connection_tools: Database connection management
    - data_tools: Data manipulation and query execution
    - firefox: Firefox bookmark management and analysis tools
    - fts_tools: Full-text search functionality
    - help_tools: Help and documentation system
    - init_tools: Initialization and setup
    - management_tools: Database administration and maintenance
    - media_tools: Media file operations
    - plex_tools: Plex Media Server integration
    - query_tools: SQL query building and execution
    - registry_tools: Windows Registry operations
    - schema_tools: Database schema inspection
    - windows_tools: Windows-specific operations
"""

# Import tool modules to make them available when importing the package
from . import (
    # Phase 1-3 new tools
    browser_bookmarks,
    calibre_tools,
    chrome_bookmarks,
    chrome_profiles,
    connection_tools,
    data_tools,
    db_analysis,
    # New portmanteau tools
    db_connection,
    db_fts,
    db_management,
    db_operations,
    db_operations_extended,
    db_schema,
    firefox,
    firefox_backup,
    firefox_bookmarks,
    firefox_curated,
    firefox_profiles,
    firefox_tagging,
    firefox_utils,
    fts_tools,
    help_system,
    help_tools,
    init_tools,
    management_tools,
    media_library,
    media_tools,
    plex_tools,
    query_tools,
    registry_tools,
    schema_tools,
    system_init,
    windows_system,
    windows_tools,
)

# Export the main tool modules
__all__ = [
    "calibre_tools",
    "connection_tools",
    "data_tools",
    "firefox",
    "fts_tools",
    "help_tools",
    "init_tools",
    "management_tools",
    "media_tools",
    "plex_tools",
    "query_tools",
    "registry_tools",
    "schema_tools",
    "windows_tools",
    # New portmanteau tools
    "db_connection",
    "db_operations",
    "db_schema",
    "db_management",
    "db_fts",
    "firefox_bookmarks",
    "firefox_profiles",
    "firefox_utils",
    "firefox_tagging",
    "firefox_curated",
    "firefox_backup",
    "media_library",
    "windows_system",
    "help_system",
    "system_init",
    # Phase 1-3 new tools
    "browser_bookmarks",
    "chrome_bookmarks",
    "chrome_profiles",
    "db_analysis",
    "db_operations_extended",
]
