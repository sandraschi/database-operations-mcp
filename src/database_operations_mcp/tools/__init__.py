"""
Database Operations MCP - Tools Package

This package contains all the tool modules for the Database Operations MCP,
organized into logical modules for better maintainability.

PORTMANTEAU TOOLS (Active):
    - db_connection: Database connection management (consolidates connection_tools, init_tools)
    - db_operations: Data manipulation and query execution (consolidates query_tools, data_tools)
    - db_schema: Database schema inspection (consolidates schema_tools)
    - db_fts: Full-text search functionality (consolidates fts_tools)
    - db_management: Database administration (consolidates management_tools)
    - help_system: Help and documentation (consolidates help_tools)
    - media_library: Media operations (consolidates calibre_tools, plex_tools, media_tools)
    - windows_system: Windows-specific operations (consolidates registry_tools, windows_tools)
    - browser_bookmarks: Universal browser bookmark management
    - firefox_bookmarks, chrome_bookmarks: Browser-specific bookmark tools

DEPRECATED MODULES (kept for backwards compatibility, tools no longer registered):
    - calibre_tools → use media_library(operation='...')
    - connection_tools → use db_connection(operation='...')
    - data_tools → use db_operations(operation='...')
    - fts_tools → use db_fts(operation='...')
    - help_tools → use help_system(operation='...')
    - init_tools → use db_connection(operation='...')
    - management_tools → use db_management(operation='...')
    - media_tools → use media_library(operation='...')
    - plex_tools → use media_library(operation='...')
    - query_tools → use db_operations(operation='...')
    - registry_tools → use windows_system(operation='...')
    - schema_tools → use db_schema(operation='...')
    - windows_tools → use windows_system(operation='...')
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
