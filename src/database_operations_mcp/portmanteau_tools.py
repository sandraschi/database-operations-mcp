"""
Portmanteau Tools Only - Import Module

This module imports only the portmanteau tools and help system
to avoid tool explosion in Claude Desktop.
"""

# Import only portmanteau tools and help system
from .tools import (  # noqa: F401
    # Portmanteau tools (consolidated interfaces)
    db_connection,
    db_fts,
    db_management,
    db_operations,
    db_schema,
    firefox_backup,
    firefox_bookmarks,
    firefox_curated,
    firefox_profiles,
    firefox_tagging,
    firefox_utils,
    help_system,
    # Help tools (always needed)
    help_tools,
    media_library,
    system_init,
    windows_system,
)
