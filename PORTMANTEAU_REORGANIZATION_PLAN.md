# Portmanteau Tool Reorganization Plan

## Overview
Reorganize all individual tools into portmanteau tools following FastMCP 2.13+ standards and cursor rules. This reduces tool count, improves maintainability, and provides consistent interfaces.

## Current State Analysis

### Existing Portmanteau Tools (Keep)
- ✅ `db_connection` - Database connection management
- ✅ `db_operations` - Database data operations  
- ✅ `db_schema` - Database schema operations
- ✅ `db_management` - Database administration
- ✅ `db_fts` - Full-text search operations
- ✅ `db_analyzer` - Database analysis (renamed from db_analysis)
- ✅ `browser_bookmarks` - Universal browser bookmarks
- ✅ `chrome_bookmarks` - Chrome-specific bookmarks
- ✅ `chrome_profiles` - Chrome profile management
- ✅ `firefox_bookmarks` - Firefox bookmarks
- ✅ `firefox_profiles` - Firefox profiles
- ✅ `help_system` - Help and documentation
- ✅ `media_library` - Media library operations
- ✅ `windows_system` - Windows system operations
- ✅ `system_init` - System initialization

### Individual Tools to Consolidate

#### Database Operations Group
1. **query_tools.py** → Merge into `db_operations`
   - `execute_query` → `db_operations(operation='execute_query')`
   - `quick_data_sample` → Already exists in `db_operations`

2. **data_tools.py** → Merge into `db_operations`
   - `execute_transaction` → Already exists in `db_operations`
   - Check for other operations

#### Database Connection Group
3. **connection_tools.py** → Merge into `db_connection`
   - `list_supported_databases` → Already exists
   - `register_database_connection` → Already exists as `register`
   - Check for other operations

4. **init_tools.py** → Merge into `db_connection`
   - `init_database` → `db_connection(operation='init')`
   - `list_connections` → Already exists
   - `close_connection` → `db_connection(operation='close')`
   - `test_connection` → Already exists
   - `get_connection_info` → `db_connection(operation='get_info')`
   - `restore_saved_connections` → `db_connection(operation='restore')`
   - `set_active_connection` → `db_connection(operation='set_active')`
   - `get_active_connection` → `db_connection(operation='get_active')`
   - `get_user_preferences` → `db_connection(operation='get_preferences')`
   - `set_user_preferences` → `db_connection(operation='set_preferences')`

#### Database Schema Group
5. **schema_tools.py** → Merge into `db_schema`
   - `list_databases` → Already exists
   - `list_tables` → Already exists
   - `describe_table` → Already exists
   - Check for other operations

#### Full-Text Search Group
6. **fts_tools.py** → Merge into `db_fts`
   - `fts_search` → Check if exists
   - Check for other operations

#### Database Management Group
7. **management_tools.py** → Merge into `db_management`
   - Check what operations exist

#### Help Group
8. **help_tools.py** → Merge into `help_system`
   - `help` function → Check if exists
   - `tool_help` → Add to `help_system`
   - HelpSystem class → Keep in `help_system`

#### Media Group
9. **calibre_tools.py** → Convert to `calibre_library` portmanteau
   - All operations → `calibre_library(operation='...')`

10. **plex_tools.py** → Merge into `media_library`
    - `get_plex_library_sections` → Already exists
    - Other operations → Add to `media_library`

11. **media_tools.py** → Merge into `media_library`
    - Check what operations exist

#### Windows Group
12. **registry_tools.py** → Merge into `windows_system`
    - All registry operations → `windows_system(operation='registry_...')`

13. **windows_tools.py** → Merge into `windows_system`
    - Check what operations exist

## Implementation Plan

### Phase 1: Database Tools Consolidation
1. ✅ Create plan document
2. Merge `query_tools.py` into `db_operations`
3. Merge `data_tools.py` into `db_operations`
4. Merge `init_tools.py` into `db_connection`
5. Merge `connection_tools.py` into `db_connection`
6. Merge `schema_tools.py` into `db_schema`
7. Merge `fts_tools.py` into `db_fts`
8. Merge `management_tools.py` into `db_management`

### Phase 2: Support Tools Consolidation
9. Merge `help_tools.py` into `help_system`
10. Convert `calibre_tools.py` to `calibre_library` portmanteau
11. Merge `plex_tools.py` into `media_library`
12. Merge `media_tools.py` into `media_library`

### Phase 3: Windows Tools Consolidation
13. Merge `registry_tools.py` into `windows_system`
14. Merge `windows_tools.py` into `windows_system`

### Phase 4: Cleanup
15. Update `__init__.py` imports
16. Remove deprecated tool files
17. Update documentation
18. Run ruff check and format
19. Test all portmanteau tools

## Migration Strategy

For each consolidation:
1. Read source tool file to understand operations
2. Add operations to target portmanteau using proper operation parameter
3. Update docstrings following cursor rules standards
4. Ensure AI-friendly error messages
5. Test operation
6. Mark source file for deletion
7. Update imports in `__init__.py`

## Success Criteria
- All individual tools consolidated into portmanteaus
- Zero ruff errors
- All operations accessible via portmanteau tools
- Comprehensive docstrings for all portmanteaus
- AI-friendly error messages throughout
- No breaking changes to existing functionality

