"""Test utilities for FastMCP server."""

import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient


def mock_mcp_tool(name: str, return_value: Any = None, side_effect: Any = None):
    """Create a mock MCP tool.

    Args:
        name: Name of the tool
        return_value: Value to return when the tool is called
        side_effect: Side effect when the tool is called

    Returns:
        Mock tool function
    """

    async def mock_tool(*args, **kwargs):
        if side_effect is not None:
            if callable(side_effect):
                return side_effect(*args, **kwargs)
            raise side_effect
        return return_value

    mock = AsyncMock(side_effect=mock_tool)
    mock.name = name
    return mock


class AsyncContextManager:
    """Async context manager for testing."""

    def __init__(self, result=None, exception=None):
        self.result = result
        self.exception = exception

    async def __aenter__(self):
        if self.exception:
            raise self.exception
        return self.result

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def assert_dict_contains_subset(subset: Dict, dictionary: Dict) -> None:
    """Assert that a dictionary contains all key-value pairs from a subset.

    Args:
        subset: Dictionary containing the expected key-value pairs
        dictionary: Dictionary to check against

    Raises:
        AssertionError: If any key-value pair in subset is not in dictionary
    """
    for key, value in subset.items():
        assert key in dictionary, f"Key '{key}' not found in dictionary"
        assert dictionary[key] == value, (
            f"Value for key '{key}' does not match. Expected {value}, got {dictionary[key]}"
        )


class TestMCPClient:
    """Test client for MCP server."""

    def __init__(self, client: TestClient):
        """Initialize with a FastAPI test client."""
        self.client = client

    async def call_tool(self, tool_name: str, **kwargs) -> Dict:
        """Call a tool on the MCP server."""
        response = self.client.post("/tools/call", json={"name": tool_name, "args": kwargs})
        assert response.status_code == 200, f"Tool call failed: {response.text}"
        return response.json()

    async def list_tools(self) -> Dict:
        """List all available tools."""
        response = self.client.get("/tools")
        assert response.status_code == 200, f"Failed to list tools: {response.text}"
        return response.json()


@pytest.fixture
def mcp_client():
    """Create a test MCP client."""
    from mcp_server.main import app

    with TestClient(app) as client:
        yield TestMCPClient(client)


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
