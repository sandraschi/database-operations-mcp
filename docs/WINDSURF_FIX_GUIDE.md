# Database Operations MCP - Windsurf Fix Guide

*Created: 2025-08-21 - Issue: Server disconnected with `py -3.13 -m database_operations_mcp`*

## ❌ Current Problem
```
Command: py -3.13 -m database_operations_mcp
Error: Server disconnected
```

The MCP server is failing to start in Claude Desktop, likely due to module path issues or missing dependencies.

## 🔍 Diagnosis Steps

### Step 1: Check Python Environment
```powershell
# Test if Python 3.13 is available
py -3.13 --version

# Test if module can be found
py -3.13 -c "import database_operations_mcp; print('Module found')"
```

### Step 2: Check Installation
```powershell
# Navigate to project root
Set-Location "D:\Dev\repos\database-operations-mcp"

# Check if installed in development mode
py -3.13 -m pip list | Select-String "database-operations-mcp"

# Check if src structure is correct
Get-ChildItem -Path "src\database_operations_mcp" -Recurse
```

### Step 3: Test FastMCP Installation
```powershell
# Check if FastMCP 2.10.1+ is installed
py -3.13 -c "import fastmcp; print(f'FastMCP version: {fastmcp.__version__}')"
```

### Step 4: Test Manual Execution
```powershell
# Try running directly
Set-Location "D:\Dev\repos\database-operations-mcp"
py -3.13 -m database_operations_mcp
```

## 🛠️ Fix Solutions (Try in Order)

### Fix 1: Reinstall in Development Mode
```powershell
Set-Location "D:\Dev\repos\database-operations-mcp"

# Uninstall if exists
py -3.13 -m pip uninstall database-operations-mcp -y

# Install in development mode
py -3.13 -m pip install -e .

# Test installation
py -3.13 -c "import database_operations_mcp; print('Success')"
```

### Fix 2: Update Claude Config (Recommended)
Update `C:\Users\sandr\AppData\Roaming\Claude\claude_desktop_config.json`:

**Current (Broken):**
```json
"database-operations": {
  "command": "py",
  "args": ["-3.13", "-m", "database_operations_mcp"],
  "cwd": "D:\\Dev\\repos\\database-operations-mcp",
  "env": {
    "SQLITE_DEFAULT_PATH": "L:\\Multimedia Files\\Written Word",
    "PYTHONUNBUFFERED": "1"
  }
}
```

**Fixed Option A (Direct Script):**
```json
"database-operations": {
  "command": "python",
  "args": ["src/database_operations_mcp/__main__.py"],
  "cwd": "D:/Dev/repos/database-operations-mcp",
  "env": {
    "SQLITE_DEFAULT_PATH": "L:/Multimedia Files/Written Word",
    "PYTHONPATH": "D:/Dev/repos/database-operations-mcp/src",
    "PYTHONUNBUFFERED": "1"
  }
}
```

**Fixed Option B (Module with PYTHONPATH):**
```json
"database-operations": {
  "command": "py",
  "args": ["-3.13", "-m", "database_operations_mcp"],
  "cwd": "D:/Dev/repos/database-operations-mcp",
  "env": {
    "SQLITE_DEFAULT_PATH": "L:/Multimedia Files/Written Word",
    "PYTHONPATH": "D:/Dev/repos/database-operations-mcp/src",
    "PYTHONUNBUFFERED": "1"
  }
}
```

### Fix 3: Verify Dependencies
```powershell
Set-Location "D:\Dev\repos\database-operations-mcp"

# Install all dependencies
py -3.13 -m pip install -r requirements.txt

# If no requirements.txt, install known dependencies
py -3.13 -m pip install fastmcp>=2.10.1 sqlite3 psycopg2-binary pymongo chromadb
```

### Fix 4: Test Import Chain
```powershell
# Test each import level
py -3.13 -c "import sys; sys.path.insert(0, 'src'); import database_operations_mcp"
py -3.13 -c "import sys; sys.path.insert(0, 'src'); from database_operations_mcp import main"
py -3.13 -c "import sys; sys.path.insert(0, 'src'); from database_operations_mcp.main import main; main()"
```

### Fix 5: Create Standalone Launcher (Last Resort)
Create `D:\Dev\repos\database-operations-mcp\run_server.py`:
```python
#!/usr/bin/env python3
"""Standalone launcher for Database Operations MCP."""
import sys
import os

# Add src to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from database_operations_mcp.main import main
    main()
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Runtime error: {e}", file=sys.stderr)
    sys.exit(1)
```

Then update Claude config:
```json
"database-operations": {
  "command": "python",
  "args": ["run_server.py"],
  "cwd": "D:/Dev/repos/database-operations-mcp",
  "env": {
    "SQLITE_DEFAULT_PATH": "L:/Multimedia Files/Written Word",
    "PYTHONUNBUFFERED": "1"
  }
}
```

## 🔧 Common Issues & Solutions

### Issue: "Module not found"
- **Cause**: PYTHONPATH not set or module not installed
- **Fix**: Add `PYTHONPATH` to env or use Fix 1

### Issue: "FastMCP not found"
- **Cause**: FastMCP not installed or wrong version
- **Fix**: `py -3.13 -m pip install fastmcp>=2.10.1`

### Issue: "Permission denied"
- **Cause**: File system permissions
- **Fix**: Run PowerShell as Administrator

### Issue: "Server disconnected immediately"
- **Cause**: Python script crashes during import
- **Fix**: Test manual execution (Step 4)

## 📝 Verification Commands

After applying fixes, test with:
```powershell
# 1. Test module import
py -3.13 -c "import database_operations_mcp; print('✅ Module imports')"

# 2. Test server startup (should not exit immediately)
Set-Location "D:\Dev\repos\database-operations-mcp"
py -3.13 -m database_operations_mcp

# 3. Check MCP communication (in separate terminal)
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | py -3.13 -m database_operations_mcp
```

## 🎯 Recommended Fix Path

1. **Start with Fix 2 Option B** (add PYTHONPATH to env)
2. **If fails**: Try Fix 1 (reinstall in dev mode)  
3. **If still fails**: Use Fix 5 (standalone launcher)
4. **Verify**: Use verification commands above

## 📊 Project Status Context

Based on basic memory notes:
- ✅ Database Operations MCP is 85% complete
- ✅ Core SQLite/PostgreSQL/ChromaDB connectors implemented  
- ✅ FastMCP 2.10.1 framework integration ready
- ✅ Missing `__main__.py` entry point was already fixed
- ❌ **Current blocker**: Module loading in Claude Desktop

**Priority**: Fix this startup issue to enable SQLite analysis of Calibre mystery database.

## 🏷️ Tags
["database-operations-mcp", "claude-desktop", "mcp-server", "fix-guide", "windsurf", "critical"]
