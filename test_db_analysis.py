#!/usr/bin/env python3
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from database_operations_mcp.services.analysis.structure_analyzer import StructureAnalyzer
from database_operations_mcp.services.analysis.content_analyzer import ContentAnalyzer
from database_operations_mcp.services.analysis.health_checker import HealthChecker

async def test_db_analysis():
    structure_analyzer = StructureAnalyzer()
    content_analyzer = ContentAnalyzer()
    health_checker = HealthChecker()

    db_path = r"L:\Multimedia Files\Written Word\metadata.db"

    try:
        print(f"Testing full db_analysis on: {db_path}")

        # Mimic what db_analysis does for operation="analyze"
        print("Step 1: Analyze schema...")
        structure = await structure_analyzer.analyze_schema(db_path)
        print(f"Found {len(structure.get('tables', []))} tables")

        print("Step 2: Check health...")
        health = await health_checker.check_health(db_path)
        print(f"Health check: {health.get('overall_score', 'unknown')}")

        print("Step 3: Sample content from first table...")
        if structure.get('tables'):
            first_table = structure['tables'][0]['name']
            print(f"Sampling from table: {first_table}")
            content = await content_analyzer.sample_content(db_path, first_table, limit=10)
            print(f"Sampled {len(content)} rows")
        else:
            print("No tables found")

        print("All steps completed successfully!")
        return True

    except Exception as e:
        print(f"db_analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_db_analysis())
    print(f"Test {'PASSED' if success else 'FAILED'}")
