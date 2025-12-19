#!/usr/bin/env python3
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from database_operations_mcp.services.analysis.structure_analyzer import StructureAnalyzer

async def test_structure_analyzer():
    analyzer = StructureAnalyzer()
    db_path = r"L:\Multimedia Files\Written Word\metadata.db"

    try:
        print(f"Testing structure analyzer on: {db_path}")
        result = await analyzer.analyze_schema(db_path)
        print("Structure analysis successful!")
        print(f"Found {len(result.get('tables', []))} tables")
        for table in result.get('tables', [])[:3]:  # Show first 3 tables
            print(f"  - {table.get('name')}: {len(table.get('columns', []))} columns")
        return True
    except Exception as e:
        print(f"Structure analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_structure_analyzer())
    print(f"Test {'PASSED' if success else 'FAILED'}")
