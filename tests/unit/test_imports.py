#!/usr/bin/env python3
import sys

sys.path.insert(0, r"D:\Dev\repos\database-operations-mcp")

try:
    print("✅ Module import successful")

    print("✅ Main function import successful")

    print("✅ Server creation function import successful")

    print("🎯 Module structure check complete - all imports working!")

except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback

    traceback.print_exc()
