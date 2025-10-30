import pytest

from database_operations_mcp.tools.sync_tools import sync_bookmarks


@pytest.mark.asyncio
async def test_sync_bookmarks_dry_run():
    res = await sync_bookmarks("chrome", "edge", dry_run=True, limit=10)
    assert res["status"] in ("planned", "error", "noop")
    assert "dry_run" in res
