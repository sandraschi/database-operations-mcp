#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, r"D:\Dev\repos\database-operations-mcp")

try:
    import database_operations_mcp
    print("✅ Module import successful")
    
    from database_operations_mcp.__main__ import main
    print("✅ Main function import successful")
    
    from database_operations_mcp.mcp_server import create_server
    print("✅ Server creation function import successful")
    
    print("🎯 Module structure check complete - all imports working!")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
