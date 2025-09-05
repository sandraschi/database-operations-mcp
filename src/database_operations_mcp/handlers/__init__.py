"""
Tools package for Database Operations MCP.

Organized tool modules:
- connection_tools: Database connection management (create, list, test, remove connections)
- query_tools: Query execution and data operations (execute, explain, analyze queries)
- schema_tools: Schema inspection and metadata (tables, columns, constraints, indexes)
- data_tools: Data manipulation (import, export, transform data)
- fts_tools: Full-text search functionality (search, index management)
- management_tools: Database administration (backup, restore, maintenance)
- registry_tools: Windows registry operations (read, write, query registry)
- windows_tools: Windows-specific operations (services, processes, filesystem)
- calibre_tools: Calibre library management (books, metadata, conversions)
- media_tools: Media file operations (images, audio, video processing)
- firefox: Firefox bookmark management and analysis tools
- help_tools: Documentation and help system (list tools, get help)
- init_tools: Initialization and setup (configuration, first-time setup)
- maintenance_tools: Database maintenance tasks (vacuum, reindex, optimize)
"""

from typing import List, Optional, Dict, Any
from fastmcp import FastMCP

# Import all handler modules
from . import connection_tools
from . import query_tools
from . import schema_tools
from . import data_tools
from . import fts_tools
from . import management_tools
from . import registry_tools
from . import windows_tools
from . import calibre_tools
from . import media_tools
from . import firefox
from . import help_tools
from . import init_tools
from . import maintenance_tools
from . import plex_tools

def register_all_tools(mcp: FastMCP) -> None:
    """Register all tools with the FastMCP instance.
    
    This function should be called during FastMCP initialization to register
    all available tools from all handler modules.
    
    Args:
        mcp: The FastMCP instance to register tools with
    """
    # Import and register all tools from each module
    modules = [
        connection_tools,
        query_tools,
        schema_tools,
        data_tools,
        fts_tools,
        management_tools,
        registry_tools,
        windows_tools,
        calibre_tools,
        media_tools,
        firefox,  # Add Firefox tools
        help_tools,
        init_tools,
        maintenance_tools,
        plex_tools
    ]
    
    for module in modules:
        if hasattr(module, 'register_tools'):
            module.register_tools(mcp)

__all__ = [
    "connection_tools",
    "query_tools", 
    "schema_tools",
    "data_tools",
    "fts_tools",
    "management_tools",
    "registry_tools",
    "windows_tools",
    "calibre_tools",
    "media_tools",
    "firefox",  # Add Firefox tools to __all__
    "help_tools",
    "init_tools",
    "maintenance_tools",
    "plex_tools",
    "register_all_tools"
]
