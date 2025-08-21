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
- help_tools: Documentation and help system (list tools, get help)
- init_tools: Initialization and setup (configuration, first-time setup)
- maintenance_tools: Database maintenance tasks (vacuum, reindex, optimize)
"""

__all__ = [
    "connection_tools",
    "query_tools", 
    "schema_tools",
    "management_tools",
    "data_tools",
    "fts_tools",
    "help_tools",
    "init_tools",
    "maintenance_tools",
    "media_tools",
    "registry_tools",
    "windows_tools",
    "calibre_tools"
]

