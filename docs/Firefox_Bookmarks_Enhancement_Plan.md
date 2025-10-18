# Firefox Bookmarks Enhancement Plan for Database Operations MCP

> **⚠️ OUTDATED**: This document contains references to DXT packaging which has been replaced by MCPB packaging.

**Date:** 2025-09-05  
**Status:** Planning Phase  
**Priority:** Medium  
**Estimated Implementation:** 2-3 days  

## Overview

> **⚠️ OUTDATED**: This plan references DXT packaging which has been replaced by MCPB packaging.

## Current State Assessment

### Existing Infrastructure ✅
- ✅ SQLite database support via database-operations-mcp
- ✅ FastMCP 2.10.1+ framework
- ✅ Handler-based tool organization
- ✅ Windows profile detection capabilities
- ✅ DXT packaging pipeline ready

### Missing Components ❌
- ❌ Firefox profile auto-detection
- ❌ Firefox-specific bookmark schema knowledge
- ❌ Bookmark hierarchy traversal tools
- ❌ Bookmark safety validation (Firefox must be closed)
- ❌ Bookmark-specific analysis tools

## Technical Implementation Plan

### Phase 1: Core Firefox Integration (Day 1)

#### 1.1 Create Firefox Handler Module
**File:** `src/database_operations_mcp/handlers/firefox_tools.py`

**Core Tools to Implement:**
```python
@mcp.tool()
async def find_firefox_profiles() -> Dict[str, Any]:
    """Auto-detect Firefox profile locations and validate places.sqlite."""
    
@mcp.tool()  
async def connect_firefox_bookmarks(profile_name: Optional[str] = None) -> Dict[str, Any]:
    """Connect to Firefox places.sqlite database safely."""
    
@mcp.tool()
async def list_firefox_bookmarks(profile_name: Optional[str] = None, folder_id: Optional[int] = None) -> Dict[str, Any]:
    """List bookmarks with folder hierarchy and metadata."""
    
@mcp.tool()
async def analyze_bookmark_structure(profile_name: Optional[str] = None) -> Dict[str, Any]:
    """Analyze folder/tag hierarchy and statistics."""
```

#### 1.2 Safety Validations
- Firefox process detection (must be closed)
- Database lock checking
- Automatic backup creation before operations
- Schema version compatibility checking

#### 1.3 Update Handler Registration
**File:** `src/database_operations_mcp/handlers/__init__.py`
- Add `firefox_tools` import
- Register in `register_all_tools()` function

### Phase 2: Advanced Bookmark Analysis (Day 2)

#### 2.1 Duplicate Detection Tools
```python
@mcp.tool()
async def find_duplicate_bookmarks(profile_name: Optional[str] = None) -> Dict[str, Any]:
    """Find bookmarks with duplicate URLs across folders."""
    
@mcp.tool()
async def find_similar_bookmarks(similarity_threshold: float = 0.8) -> Dict[str, Any]:
    """Find bookmarks with similar titles or URLs using fuzzy matching."""
```

#### 2.2 Cleanup Analysis Tools
```python
@mcp.tool()
async def find_unused_tags(profile_name: Optional[str] = None) -> Dict[str, Any]:
    """Find tags with no associated bookmarks."""
    
@mcp.tool()
async def find_empty_folders(profile_name: Optional[str] = None) -> Dict[str, Any]:
    """Find bookmark folders with no children."""
    
@mcp.tool()
async def analyze_bookmark_health(profile_name: Optional[str] = None) -> Dict[str, Any]:
    """Comprehensive bookmark health check and cleanup recommendations."""
```

### Phase 3: Data Management Tools (Day 3)

#### 3.1 Export/Import Tools
```python
@mcp.tool()
async def export_bookmarks_by_tag(tag_name: str, format: str = "json") -> Dict[str, Any]:
    """Export bookmarks with specific tag to file."""
    
@mcp.tool()
async def export_bookmark_folder(folder_id: int, format: str = "json") -> Dict[str, Any]:
    """Export entire folder structure to file."""
    
@mcp.tool()
async def backup_firefox_bookmarks(profile_name: Optional[str] = None) -> Dict[str, Any]:
    """Create timestamped backup of places.sqlite."""
```

#### 3.2 Cleanup Operations
```python
@mcp.tool()
async def remove_duplicate_bookmarks(dry_run: bool = True) -> Dict[str, Any]:
    """Remove duplicate bookmarks (keeps first occurrence)."""
    
@mcp.tool()
async def cleanup_unused_tags(dry_run: bool = True) -> Dict[str, Any]:
    """Remove tags with no associated bookmarks."""
    
@mcp.tool()
async def remove_empty_folders(dry_run: bool = True) -> Dict[str, Any]:
    """Remove bookmark folders with no children."""
```

## Database Schema Integration

### Key Tables to Leverage
```sql
-- Core bookmark data
moz_bookmarks: id, type, fk, parent, position, title, dateAdded, lastModified
moz_places: id, url, title, visit_count, last_visit_date
moz_favicons: id, url, data, mime_type

-- Tagging system
moz_bookmarks WHERE type=2 AND parent=4  -- Tags
```

### Safe Query Patterns
- Always use READ-ONLY transactions for analysis
- Implement proper foreign key validation
- Respect Firefox's bookmark hierarchy constraints
- Handle schema version differences gracefully

## Integration with Existing Tools

### Leverage Current Database Operations
- Use existing SQLite connection management
- Utilize query execution framework
- Apply existing export/import patterns
- Reuse error handling and logging

### Enhanced List Tools Fix
**Current Issue:** `database:list_tools` has serialization error
**Solution:** Fix in Phase 1 during firefox_tools integration

```python
# Fix the list_tools serialization issue
def get_tool_categories() -> Dict[str, List[str]]:
    return {
        "database": ["connection", "query", "schema", "maintenance"],
        "firefox": ["profile", "bookmarks", "analysis", "cleanup"],  # NEW
        "calibre": ["search", "metadata", "export"],
        "registry": ["read", "monitor", "backup"],
        "help": ["tools", "quick_start", "docs"]
    }
```

## Testing Strategy

### Unit Tests
- Firefox profile detection across Windows versions
- Database schema validation
- Bookmark hierarchy parsing
- Safety checks (Firefox process detection)

### Integration Tests
- End-to-end bookmark analysis workflow
- Export/import round-trip validation
- Cleanup operation safety (dry-run vs actual)

### Test Data
- Mock Firefox profile with realistic bookmark structure
- Test cases for edge cases (empty folders, circular references)
- Schema evolution test cases

## Risk Mitigation

### Data Safety
- ✅ **Automatic backups** before any modification
- ✅ **Firefox process detection** to prevent corruption
- ✅ **Dry-run mode** for all destructive operations
- ✅ **Read-only mode by default** for analysis tools

### Error Handling
- ✅ **Schema version validation**
- ✅ **Database corruption detection**
- ✅ **Graceful degradation** if profile not found
- ✅ **Comprehensive logging** for troubleshooting

## Performance Considerations

### Query Optimization
- Use proper indexes on frequently queried columns
- Implement pagination for large bookmark collections
- Cache profile detection results
- Use prepared statements for safety

### Memory Management
- Stream large result sets instead of loading everything
- Implement result limiting for analysis tools
- Clean up temporary data structures

## Future Enhancements (Post-Implementation)

### Advanced Features
- Dead link detection (HTTP status checking)
- Bookmark recommendation based on usage patterns
- Tag hierarchy optimization suggestions
- Bookmark organization AI assistance

### Cross-Browser Support
- Chrome bookmarks integration
- Edge bookmarks support
- Safari bookmarks (macOS future)

## Success Criteria

### Must Have ✅
- ✅ Safe Firefox profile detection
- ✅ Read-only bookmark analysis
- ✅ Duplicate bookmark detection
- ✅ Export functionality
- ✅ Fixed list_tools command

### Should Have 🎯
- 🎯 Cleanup operations with dry-run
- 🎯 Tag analysis and cleanup
- 🎯 Folder structure optimization
- 🎯 Comprehensive documentation

### Nice to Have ⭐
- ⭐ Bookmark health scoring
- ⭐ Usage pattern analysis
- ⭐ Automated cleanup recommendations
- ⭐ Visual bookmark hierarchy display

## Implementation Notes for Windsurf

### FastMCP 2.10.1+ Compatibility
```python
# Use modern FastMCP pattern
from fastmcp import FastMCP

@mcp.tool()
async def tool_name(param: Type = DefaultValue) -> Dict[str, Any]:
    """Tool description with proper typing."""
    return {"success": True, "data": result}
```

### Error Handling Pattern
```python
try:
    # Tool implementation
    return {"success": True, "data": result}
except Exception as e:
    logger.error(f"Tool failed: {e}", exc_info=True)
    return {"success": False, "error": str(e)}
```

### Database Connection Pattern
```python
# Reuse existing database infrastructure
conn_name = f"firefox_profile_{profile_name}"
db_path = profile_path / "places.sqlite"

# Register connection if not exists
await register_database_connection(
    connection_name=conn_name,
    database_type="sqlite",
    connection_config={"database": str(db_path)},
    test_connection=True
)
```

---

**Next Steps:**
1. 🚀 Start with Phase 1 implementation in Windsurf
2. 📝 Update basic memory with progress tracking
3. 🧪 Create test Firefox profile for validation
4. 📦 Prepare for DXT packaging after completion
