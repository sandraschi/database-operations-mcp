#!/usr/bin/env python3
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from database_operations_mcp.services.analysis.content_analyzer import ContentAnalyzer

async def test_content_analyzer():
    analyzer = ContentAnalyzer()
    db_path = r"L:\Multimedia Files\Written Word\metadata.db"

    try:
        print(f"Testing content analyzer on: {db_path}")
        result = await analyzer.sample_content(db_path, "books", limit=5)
        print("Content analysis successful!")
        print(f"Sampled {len(result)} rows from books table")
        return True
    except Exception as e:
        print(f"Content analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_content_analyzer())
    print(f"Test {'PASSED' if success else 'FAILED'}")
