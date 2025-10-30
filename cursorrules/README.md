# Cursor Rules Templates

This directory contains standardized `.cursorrules` templates for different types of MCP repositories.

## Available Templates

### 1. MCP Server Template
**File**: `.cursorrules-mcp-server.template`  
**Use for**: MCP servers without frontend  
**Includes**:
- FastMCP 2.13 standards
- Python/async best practices
- Testing requirements
- Basic file structure

**How to use**:
```bash
# Copy to your MCP server repo
cp cursorrules/.cursorrules-mcp-server.template .cursorrules

# Edit and adapt repository-specific sections
# - Change [REPO_NAME] to your repo name
# - Add repository-specific file structure
# - Customize tools and features
```

### 2. Full-Stack Template
**File**: `.cursorrules-full-stack.template`  
**Use for**: Full-stack apps with MCP + React frontend  
**Includes**:
- Everything from MCP Server template
- React + TypeScript standards
- Chakra UI guidelines
- FastAPI backend patterns
- Docker support
- Database standards
- Authentication patterns

**How to use**:
```bash
# Copy to your full-stack repo
cp cursorrules/.cursorrules-full-stack.template .cursorrules

# Edit and adapt repository-specific sections
# - Change [REPO_NAME] to your repo name
# - Add specific frontend structure
# - Customize API endpoints
# - Add project-specific features
```

## Template Sections

Both templates include:

### Required Sections
- **Repository Purpose**: What the repo does
- **Critical Headers**: PowerShell syntax, "hi!" test output
- **Code Standards**: Python stack, commands
- **FastMCP 2.13**: Tool decorators, docstring requirements

### Conditional Sections
- **Frontend Standards**: Full-stack template only
- **Backend Standards**: Full-stack template only
- **Docker Support**: Both (optional)
- **Testing**: Both
- **Development Workflow**: Both

## Migration Guide

### From Old .cursorrules to Template

1. **Choose template**:
   - MCP Server → `.cursorrules-mcp-server.template`
   - Full-Stack → `.cursorrules-full-stack.template`

2. **Copy template**:
   ```bash
   cp cursorrules/.cursorrules-full-stack.template .cursorrules
   ```

3. **Replace placeholders**:
   - `[REPO_NAME]` → Your actual repo name
   - `[DESCRIPTION]` → Your repo description
   - Add specific file structure
   - Add specific features

4. **Add repository-specific sections**:
   - Domain-specific tools
   - Project-specific file structure
   - Custom development workflows

## Best Practices

### What to Keep From Templates
- ✅ PowerShell syntax rules
- ✅ FastMCP 2.13 standards
- ✅ Python stack standards
- ✅ Testing requirements
- ✅ Commit message format
- ✅ File structure patterns

### What to Customize
- 🔧 Repository purpose description
- 🔧 Specific file structure
- 🔧 Domain-specific tools
- 🔧 Project-specific patterns
- 🔧 Custom development workflows

### What NOT to Remove
- 🚫 Central docs reference
- 🚫 PowerShell syntax warnings
- 🚫 FastMCP 2.13 standards
- 🚫 Testing coverage requirements

## Examples

### Example 1: Simple MCP Server
```bash
# Your repo: firefox-profiles-mcp
cp cursorrules/.cursorrules-mcp-server.template .cursorrules

# Edit .cursorrules
# Search for [REPO_NAME] and replace
[REPO_NAME] → firefox-profiles-mcp
[DESCRIPTION] → Firefox profile management via MCP

# Add specific file structure
src/firefox_profiles_mcp/
├── mcp_server.py
└── profile_tools.py
```

### Example 2: Full-Stack Application
```bash
# Your repo: browser-bookmarks-app
cp cursorrules/.cursorrules-full-stack.template .cursorrules

# Edit .cursorrules
# Search for [REPO_NAME] and replace
[REPO_NAME] → browser-bookmarks-app
[DESCRIPTION] → Browser bookmark management with AI

# Add specific frontend structure
frontend/src/components/bookmarks/
├── BookmarkList.tsx
├── BookmarkEditor.tsx
└── BookmarkTree.tsx

# Add specific backend APIs
src/api/
├── bookmarks.py
├── sync.py
└── ai.py
```

## Maintenance

### When to Update Templates
- FastMCP version changes (e.g., 2.13 → 2.14)
- New common patterns emerge
- Community feedback on standards
- Major tooling updates

### How to Update Templates
1. Edit template files in `cursorrules/`
2. Update version in template
3. Document changes in this README
4. Notify maintainers of repos using templates

## Contributing

Found an issue or improvement?
1. Edit template in `cursorrules/`
2. Test with your repo
3. Submit PR to central docs

## Related Documentation

- [Main Cursor Rules](../.cursorrules) - Central docs standards
- [Standards](../STANDARDS.md) - General documentation standards
- [Templates](../templates/) - Other documentation templates

**Last Updated**: 2025-10-26  
**Maintained by**: MCP Central Docs Team

