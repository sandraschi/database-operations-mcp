#!/usr/bin/env python3
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from database_operations_mcp.services.analysis.error_detector import ErrorDetector

async def test_error_detector():
    detector = ErrorDetector()
    db_path = r"L:\Multimedia Files\Written Word\metadata.db"

    try:
        print(f"Testing error detector on: {db_path}")
        result = await detector.check_integrity(db_path)
        print("Error detection successful!")
        print(f"Integrity check result: {result}")
        return True
    except Exception as e:
        print(f"Error detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_error_detector())
    print(f"Test {'PASSED' if success else 'FAILED'}")
