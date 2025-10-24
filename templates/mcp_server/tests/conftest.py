"""Pytest configuration and fixtures for MCP server tests."""

import asyncio

# Add the project root to the Python path
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.main import app, mcp


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session.
    This is required for async tests.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def test_client() -> Generator[TestClient, None, None]:
    """Create a FastAPI test client.

    Yields:
        TestClient: A test client for the FastAPI application.
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
async def reset_mcp() -> AsyncGenerator[None, None]:
    """Reset the MCP instance before each test.
    This ensures tests don't interfere with each other.
    """
    # Save any existing tools
    original_tools = mcp.tools.copy()

    # Clear all tools before test
    mcp.tools.clear()

    yield  # Run the test

    # Restore original tools after test
    mcp.tools.clear()
    mcp.tools.update(original_tools)


@pytest.fixture
def mock_tool():
    """Fixture to create a mock tool for testing.

    Returns:
        A function to create mock tools with specified behavior.
    """

    def _mock_tool(name: str, return_value=None, side_effect=None):
        """Create a mock tool with the given name and behavior."""

        async def tool_func(*args, **kwargs):
            if side_effect is not None:
                if isinstance(side_effect, Exception):
                    raise side_effect
                return side_effect(*args, **kwargs)
            return return_value

        # Add tool to MCP
        mcp.tools[name] = tool_func
        return tool_func

    return _mock_tool


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Get the path to the test data directory.

    Returns:
        Path: Path to the test data directory.
    """
    return Path(__file__).parent / "data"


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # Set a temporary directory for test outputs
    test_dir = Path(__file__).parent / "tmp"
    test_dir.mkdir(exist_ok=True)
    monkeypatch.setenv("TEMP_DIR", str(test_dir.absolute()))

    yield

    # Clean up test directory
    for file in test_dir.glob("*"):
        if file.is_file():
            file.unlink()
    test_dir.rmdir()
