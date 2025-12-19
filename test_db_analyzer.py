#!/usr/bin/env python3
import asyncio
from src.database_operations_mcp.tools.db_analyzer import db_analyzer

async def test():
    try:
        result = await db_analyzer(r'L:\Multimedia Files\Written Word\metadata.db', 'analyze')
        print(f'Success! Result keys: {list(result.keys())}')
        print(f'Database type: {result.get("database_type")}')
        print(f'Tables: {len(result.get("structure", {}).get("tables", []))}')
        print(f'Health score: {result.get("health", {}).get("overall_score")}')
    except Exception as e:
        print(f'Error calling db_analyzer: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
