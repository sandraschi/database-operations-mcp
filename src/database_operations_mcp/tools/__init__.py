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
from . import calibre_tools
from . import connection_tools
from . import data_tools
from . import firefox
from . import fts_tools
from . import help_tools
from . import init_tools
from . import management_tools
from . import media_tools
from . import plex_tools
from . import query_tools
from . import registry_tools
from . import schema_tools
from . import windows_tools

# Export the main tool modules
__all__ = [
    'calibre_tools',
    'connection_tools',
    'data_tools',
    'firefox',
    'fts_tools',
    'help_tools',
    'init_tools',
    'management_tools',
    'media_tools',
    'plex_tools',
    'query_tools',
    'registry_tools',
    'schema_tools',
    'windows_tools',
]
