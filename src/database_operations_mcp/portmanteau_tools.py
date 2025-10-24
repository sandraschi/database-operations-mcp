"""
Portmanteau Tools Only - Import Module

This module imports only the portmanteau tools and help system
to avoid tool explosion in Claude Desktop.
"""

# Import only portmanteau tools and help system
from .tools import (  # noqa: F401
    # Portmanteau tools (consolidated interfaces)
    db_connection,
    db_operations,
    db_schema,
    db_management,
    db_fts,
    firefox_bookmarks,
    firefox_profiles,
    firefox_utils,
    firefox_tagging,
    firefox_curated,
    firefox_backup,
    media_library,
    windows_system,
    help_system,
    system_init,
    # Help tools (always needed)
    help_tools,
)
