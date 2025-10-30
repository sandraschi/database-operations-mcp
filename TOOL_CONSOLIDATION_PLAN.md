# Database Operations MCP - Tool Consolidation Plan

## 🎯 **Goal: Reduce 79 tools to ~15 portmanteau tools**

### 📊 **Current Tool Analysis**

**Main Tool Modules:**
- `connection_tools.py` - Database connection management
- `data_tools.py` - Data manipulation operations  
- `query_tools.py` - Query execution and management
- `schema_tools.py` - Database schema operations
- `init_tools.py` - Database initialization and management
- `management_tools.py` - Database management operations
- `fts_tools.py` - Full-text search operations
- `help_tools.py` - Help system
- `calibre_tools.py` - Calibre library operations
- `media_tools.py` - Media database operations
- `plex_tools.py` - Plex media server operations
- `registry_tools.py` - Windows registry operations
- `windows_tools.py` - Windows-specific operations
- `firefox/` - Firefox bookmark management (20+ tools)

### 🏗️ **Proposed 15 Portmanteau Tools**

#### **1. Database Connection Manager** (`db_connection`)
**Consolidates:** `connection_tools.py` (5 tools)
- `list_supported_databases`
- `register_database_connection` 
- `list_database_connections`
- `test_database_connection`
- `test_all_database_connections`

#### **2. Database Operations** (`db_operations`)
**Consolidates:** `data_tools.py` + `query_tools.py` (6 tools)
- `execute_transaction`
- `execute_write`
- `batch_insert`
- `execute_query`
- `quick_data_sample`
- `export_query_results`

#### **3. Database Schema Manager** (`db_schema`)
**Consolidates:** `schema_tools.py` (4 tools)
- `list_databases`
- `list_tables`
- `describe_table`
- `get_schema_diff`

#### **4. Database Management** (`db_management`)
**Consolidates:** `init_tools.py` + `management_tools.py` (8 tools)
- `init_database`
- `list_connections`
- `close_connection`
- `test_connection`
- `get_connection_info`
- `database_health_check`
- `get_database_metrics`
- `vacuum_database`
- `disconnect_database`

#### **5. Full-Text Search** (`db_fts`)
**Consolidates:** `fts_tools.py` (3 tools)
- `fts_search`
- `fts_tables`
- `fts_suggest`

#### **6. Firefox Bookmark Manager** (`firefox_bookmarks`)
**Consolidates:** Firefox bookmark operations (15 tools)
- `list_bookmarks`
- `get_bookmark`
- `add_bookmark`
- `search_bookmarks`
- `find_duplicates`
- `export_bookmarks`
- `batch_update_tags`
- `remove_unused_tags`
- `list_tags`
- `find_similar_tags`
- `merge_tags`
- `clean_up_tags`
- `find_old_bookmarks`
- `get_bookmark_stats`
- `find_broken_links`

#### **7. Firefox Profile Manager** (`firefox_profiles`)
**Consolidates:** Firefox profile operations (8 tools)
- `get_firefox_profiles`
- `create_firefox_profile`
- `delete_firefox_profile`
- `create_loaded_profile`
- `create_portmanteau_profile`
- `suggest_portmanteau_profiles`
- `create_loaded_profile_from_preset`
- `check_firefox_status`

#### **8. Firefox Utilities** (`firefox_utils`)
**Consolidates:** Firefox utility operations (6 tools)
- `get_firefox_platform`
- `get_firefox_profile_directory`
- `get_firefox_places_db_path`
- `is_firefox_running`
- `check_firefox_database_access_safe`
- `test_firefox_database_connection`
- `get_firefox_database_info`

#### **9. Firefox Tagging System** (`firefox_tagging`)
**Consolidates:** Firefox tagging operations (4 tools)
- `tag_from_folder`
- `batch_tag_from_folder`
- `tag_from_year`
- `batch_tag_from_year`

#### **10. Firefox Curated Sources** (`firefox_curated`)
**Consolidates:** Firefox curated sources (3 tools)
- `get_curated_source`
- `list_curated_sources`
- `list_curated_bookmark_sources`

#### **11. AI Bookmark Portmanteau** (`ai_bookmark_portmanteau`)
**Already exists:** AI-powered bookmark operations (1 tool)
- `ai_bookmark_portmanteau` (10 operations)

#### **12. Media Library Manager** (`media_library`)
**Consolidates:** `calibre_tools.py` + `media_tools.py` + `plex_tools.py` (7 tools)
- `search_calibre_library`
- `get_calibre_book_metadata`
- `search_calibre_fts`
- `find_plex_database`
- `optimize_plex_database`
- `export_database_schema`
- `get_plex_library_stats`
- `get_plex_library_sections`

#### **13. Windows System Manager** (`windows_system`)
**Consolidates:** `windows_tools.py` + `registry_tools.py` (8 tools)
- `list_windows_databases`
- `manage_plex_metadata`
- `query_windows_database`
- `clean_windows_database`
- `read_registry_value`
- `write_registry_value`
- `list_registry_keys`
- `list_registry_values`

#### **14. Help System** (`help_system`)
**Consolidates:** `help_tools.py` (2 tools)
- `help`
- `tool_help`

#### **15. Firefox Backup & Auth** (`firefox_backup`)
**Consolidates:** Firefox backup/auth operations (3 tools)
- `backup_firefox_data`
- `restore_firefox_data`
- `create_session`

### 🎯 **Consolidation Strategy**

#### **Phase 1: Core Database Tools (5 portmanteau tools)**
1. `db_connection` - Connection management
2. `db_operations` - Data operations
3. `db_schema` - Schema management
4. `db_management` - Database management
5. `db_fts` - Full-text search

#### **Phase 2: Firefox Tools (6 portmanteau tools)**
6. `firefox_bookmarks` - Bookmark operations
7. `firefox_profiles` - Profile management
8. `firefox_utils` - Utility functions
9. `firefox_tagging` - Tagging system
10. `firefox_curated` - Curated sources
11. `ai_bookmark_portmanteau` - AI operations (already exists)

#### **Phase 3: Media & System Tools (4 portmanteau tools)**
12. `media_library` - Media operations
13. `windows_system` - Windows operations
14. `help_system` - Help system
15. `firefox_backup` - Backup operations

### 🔧 **Implementation Approach**

#### **Portmanteau Tool Pattern**
```python
@mcp.tool()
@HelpSystem.register_tool(category="database")
async def db_connection(
    operation: str,
    # Operation-specific parameters
    connection_name: Optional[str] = None,
    database_type: Optional[str] = None,
    # ... other parameters
) -> Dict[str, Any]:
    """Database connection management portmanteau tool.
    
    Operations:
    - list_supported: List supported database types
    - register: Register new database connection
    - list: List all connections
    - test: Test connection
    - test_all: Test all connections
    
    Args:
        operation: The operation to perform
        connection_name: Name of the connection
        database_type: Type of database
        # ... other parameters
    
    Returns:
        Dictionary with operation results
    """
    if operation == "list_supported":
        return await list_supported_databases()
    elif operation == "register":
        return await register_database_connection(connection_name, database_type, ...)
    # ... other operations
```

### 📈 **Benefits**

1. **Reduced Complexity**: 79 tools → 15 tools (80% reduction)
2. **Better Organization**: Related operations grouped logically
3. **Easier Discovery**: Clear operation categories
4. **Consistent Interface**: Same parameter patterns across tools
5. **Maintainable**: Fewer tools to manage and document

### 🚀 **Next Steps**

1. **Start with Phase 1**: Implement core database portmanteau tools
2. **Test Each Phase**: Verify tools work before moving to next phase
3. **Update Documentation**: Update help system for new tools
4. **Deprecate Old Tools**: Remove individual tools after portmanteau tools are working
5. **Update MCP Config**: Ensure all portmanteau tools are properly registered

### 📋 **Tool Mapping Summary**

| Current Tools | Portmanteau Tool | Operations |
|---------------|------------------|------------|
| 5 connection tools | `db_connection` | 5 operations |
| 6 data/query tools | `db_operations` | 6 operations |
| 4 schema tools | `db_schema` | 4 operations |
| 8 management tools | `db_management` | 8 operations |
| 3 FTS tools | `db_fts` | 3 operations |
| 15 Firefox bookmark tools | `firefox_bookmarks` | 15 operations |
| 8 Firefox profile tools | `firefox_profiles` | 8 operations |
| 6 Firefox utility tools | `firefox_utils` | 6 operations |
| 4 Firefox tagging tools | `firefox_tagging` | 4 operations |
| 3 Firefox curated tools | `firefox_curated` | 3 operations |
| 1 AI portmanteau tool | `ai_bookmark_portmanteau` | 10 operations |
| 7 media tools | `media_library` | 7 operations |
| 8 Windows tools | `windows_system` | 8 operations |
| 2 help tools | `help_system` | 2 operations |
| 3 Firefox backup tools | `firefox_backup` | 3 operations |

**Total: 79 individual tools → 15 portmanteau tools**





