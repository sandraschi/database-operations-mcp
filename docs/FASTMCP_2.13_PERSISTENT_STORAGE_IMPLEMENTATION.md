# FastMCP 2.14.3 Persistent Storage Implementation

**Date**: 2026-01-16
**Status**: ✅ COMPLETE
**FastMCP Version**: 2.14.3+  
**Priority**: HIGH - Essential for user experience

---

## 📋 Overview

Implemented FastMCP 2.13+ persistent storage pattern for database-operations-mcp, enabling data to persist across Claude Desktop restarts and OS reboots.

## 🎯 What Data is Persisted

### 1. **Database Connections** ✅
- Connection configurations (name, type, params)
- **Security**: Passwords are NOT saved (must re-authenticate)
- Survives server restarts
- Location: `CONNECTIONS_KEY = "dbops:connections"`

### 2. **Active/Default Connection** ✅
- Currently active connection preference
- Restored on server startup
- Location: `ACTIVE_CONNECTION_KEY = "dbops:active_connection"`

### 3. **User Preferences** ✅
- Query limits, page sizes
- Display preferences
- Sort orders
- Any custom settings
- Location: `USER_PREFS_KEY = "dbops:user_preferences"`

### 4. **Search History** ✅
- Recent database queries
- Filter combinations
- Timestamped entries
- Configurable limit (default: 50)
- Location: `SEARCH_HISTORY_KEY = "dbops:search_history"`

### 5. **Bookmark Sync State** ✅
- Last sync times between browsers
- Sync preferences
- Browser pair configurations
- Location: `BOOKMARK_SYNC_STATE_KEY = "dbops:bookmark_sync_state"`

### 6. **Windows App Database Paths** ✅
- Remembered paths to Windows app databases
- Last used timestamps
- Location: `WINDOWS_DB_PATHS_KEY = "dbops:windows_db_paths"`

### 7. **Query Templates** ✅
- Saved query templates/favorites
- Descriptions and metadata
- Location: `QUERY_TEMPLATES_KEY = "dbops:query_templates"`

### 8. **Backup Locations** ✅
- Recent backup directory paths
- Backup metadata
- Location: `BACKUP_LOCATIONS_KEY = "dbops:backup_locations"`

### 9. **Schema Cache** ✅
- Cached database schema information
- TTL-based expiration (default: 1 hour)
- Per-connection and per-database
- Location: `SCHEMA_CACHE_PREFIX = "dbops:schema_cache:"`

---

## 📁 Storage Location

Storage automatically uses platform-appropriate directories:

| Platform | Storage Directory | Persists Across |
|----------|------------------|-----------------|
| **Windows** | `%APPDATA%\database-operations-mcp` | ✅ Claude restarts, ✅ Windows reboots |
| **macOS** | `~/Library/Application Support/database-operations-mcp` | ✅ Claude restarts, ✅ macOS reboots |
| **Linux** | `~/.local/share/database-operations-mcp` | ✅ Claude restarts, ✅ Linux reboots |

### Example Windows Location
```
C:\Users\username\AppData\Roaming\database-operations-mcp
```

---

## 🏗️ Architecture

### Components

1. **`storage/persistence.py`** - Core storage wrapper class
   - `DatabaseOperationsStorage` - Main storage class
   - DiskStore integration for persistence
   - Platform-aware directory setup
   - Graceful degradation if storage unavailable

2. **`config/mcp_config.py`** - FastMCP configuration
   - Added `server_lifespan` function
   - Storage initialization on startup
   - State restoration from persistent storage

3. **`tools/init_tools.py`** - Database connection tools
   - Automatic saving of connections to storage
   - New tools for preferences management
   - Active connection management

### Storage Initialization Flow

```
Server Startup
    ↓
FastMCP lifespan called
    ↓
DatabaseOperationsStorage.initialize()
    ↓
DiskStore created (persistent file storage)
    ↓
Restore saved connections/config
    ↓
Server ready with persistent storage
```

---

## 🛠️ Implementation Details

### Dependencies Added

```toml
dependencies = [
    "py-key-value-aio[disk]>=1.0.0",  # DiskStore backend
]
```

### Storage Class Methods

#### Connection Management
- `save_connection()` - Save connection config (no passwords)
- `get_all_connections()` - Get all saved connections
- `delete_connection()` - Remove connection from storage
- `set_active_connection()` - Set active connection preference
- `get_active_connection()` - Get active connection name

#### Preferences
- `get_user_preferences()` - Get all preferences
- `set_user_preferences()` - Save preferences (merges with existing)
- `get_preference()` - Get single preference
- `set_preference()` - Set single preference

#### Search History
- `add_search_to_history()` - Add query to history
- `get_search_history()` - Get recent searches
- `clear_search_history()` - Clear all history

#### Bookmark Sync
- `get_bookmark_sync_state()` - Get sync state
- `set_bookmark_sync_state()` - Save sync state
- `update_sync_time()` - Update last sync time for browser pair

#### Windows DB Paths
- `add_windows_db_path()` - Remember a path
- `get_windows_db_paths()` - Get all remembered paths

#### Query Templates
- `save_query_template()` - Save template
- `get_query_templates()` - Get all templates
- `delete_query_template()` - Remove template

#### Backup Locations
- `add_backup_location()` - Add backup location
- `get_backup_locations()` - Get all backup locations

#### Schema Cache
- `cache_schema()` - Cache schema with TTL
- `get_cached_schema()` - Get cached schema if valid

---

## 🆕 New Tools

### Database Connection Tools
- `restore_saved_connections()` - List saved connections from storage
- `set_active_connection()` - Set active connection preference
- `get_active_connection()` - Get active connection name

### Preferences Tools
- `get_user_preferences()` - Get all user preferences
- `set_user_preferences()` - Set user preferences

---

## 📝 Usage Examples

### Save Connection (Automatic)
```python
# When you create a connection, it's automatically saved
result = await init_database(
    db_type="sqlite",
    connection_params={"database": "C:/data/app.db"},
    connection_name="local_db"
)
# Connection config saved to persistent storage (password excluded)
```

### Restore Saved Connections
```python
# After server restart, get saved connections
result = await restore_saved_connections()
# Returns: {
#     'status': 'success',
#     'saved_connections': {
#         'local_db': {
#             'name': 'local_db',
#             'type': 'sqlite',
#             'params': {'database': 'C:/data/app.db'},
#             'last_used': 1234567890.0
#         }
#     }
# }
```

### Set Active Connection
```python
# Set which connection is active (persists across restarts)
await set_active_connection("prod_db")
```

### User Preferences
```python
# Set preferences
await set_user_preferences({
    "default_query_limit": 50,
    "default_page_size": 20,
    "show_metadata": True
})

# Get preferences
result = await get_user_preferences()
# Returns saved preferences
```

### Search History
```python
# Add to history (automatic in search tools)
storage = get_storage()
if storage:
    await storage.add_search_to_history(
        query="SELECT * FROM users",
        filters={"limit": 50}
    )

# Get history
history = await storage.get_search_history(limit=10)
```

---

## 🔒 Security Considerations

### Password Handling
- **Passwords are NEVER saved** to persistent storage
- Connections must be re-authenticated after restart
- Only connection parameters (host, port, database, etc.) are saved

### Storage Location
- Uses platform-appropriate secure directories
- Windows: `%APPDATA%` (user-specific, protected)
- macOS/Linux: Standard application support directories

### Key Prefixing
- All keys use `"dbops:"` prefix to prevent collisions
- Organized by data type for easy management

---

## ✅ Testing

### Verify Persistence

1. **Start server** → Create connection:
   ```python
   await init_database("sqlite", {"database": "test.db"}, "test_conn")
   ```

2. **Restart Claude Desktop** → Check connection:
   ```python
   result = await restore_saved_connections()
   assert "test_conn" in result["saved_connections"]
   ```

3. **Restart Windows/OS** → Check again:
   ```python
   result = await restore_saved_connections()
   assert "test_conn" in result["saved_connections"]  # ✅ Still persists!
   ```

### Check Storage Location

```python
import os
from pathlib import Path

# Windows
appdata = os.getenv("APPDATA")
storage_path = Path(appdata) / "database-operations-mcp"
print(f"Storage location: {storage_path}")
```

---

## 🚨 Troubleshooting

### Storage Not Initializing

**Symptoms**: `storage` is `None`, preferences not saving

**Solutions**:
1. Check `py-key-value-aio[disk]` is installed:
   ```bash
   pip install py-key-value-aio[disk]
   ```
2. Check logs for initialization errors
3. Verify directory permissions (should auto-create)

### Connections Not Restoring

**Note**: Connection **configs** are restored, but **connections must be re-established** using `init_database()`.

**Workflow**:
1. Get saved configs: `restore_saved_connections()`
2. Reconnect: `init_database()` with saved params (add password)

### Storage Directory Not Found

**Windows**: Check `%APPDATA%` environment variable
**macOS/Linux**: Ensure `~` resolves correctly (`Path.home()`)

---

## 📊 Benefits

✅ **Cross-session persistence** - Data survives Claude Desktop restarts  
✅ **Cross-OS persistence** - Data survives Windows/OS reboots  
✅ **Better UX** - Users don't lose connection configs or preferences  
✅ **Performance** - Schema caching reduces repeated queries  
✅ **Productivity** - Saved queries, templates, search history  
✅ **Security** - Passwords never persisted, must re-authenticate  

---

## 🔮 Future Enhancements

### Potential Additions
- [ ] Connection password encryption (if user opts in)
- [ ] Backup/restore storage data
- [ ] Storage analytics (usage stats)
- [ ] Storage cleanup tools (remove old entries)
- [ ] Migration tools for storage format changes

---

## 📚 References

- **FastMCP 2.13 Pattern**: `D:\Dev\repos\mcp-central-docs\docs\patterns\FASTMCP_2.13_PERSISTENT_STORAGE_PATTERN.md`
- **FastMCP Documentation**: https://fastmcp.wiki/
- **py-key-value-aio**: https://pypi.org/project/py-key-value-aio/

---

**Implementation Complete**: ✅  
**All TODOs Completed**: ✅  
**Linter Clean**: ✅  
**Ready for Use**: ✅

