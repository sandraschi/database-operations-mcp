"""Test tool to isolate the SQL syntax error issue."""

from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools._annotations import READ_ONLY


@mcp.tool(annotations=READ_ONLY)
async def test_db_tool(db_file_path: str):
    """Test database tool."""
    return {"success": True, "db_file_path": db_file_path, "tool": "test_db_tool"}
