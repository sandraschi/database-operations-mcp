""
Tests for the FastMCP server.

These tests verify the core functionality of the MCP server, including tool registration,
tool execution, and error handling.
"""
import json
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from .test_utils import TestMCPClient, mock_mcp_tool


def test_server_health_check():
    ""Test that the health check endpoint returns a successful response.""
    from mcp_server.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


def test_list_tools(mocker):
    ""Test that the server lists all registered tools.""
    from mcp_server.main import app, mcp
    
    # Mock the MCP instance
    mock_tool = mock_mcp_tool("test_tool")
    mocker.patch.object(mcp, 'tools', {"test_tool": mock_tool})
    
    client = TestClient(app)
    response = client.get("/tools")
    
    assert response.status_code == status.HTTP_200_OK
    tools = response.json()
    assert "test_tool" in tools
    assert tools["test_tool"]["name"] == "test_tool"


@pytest.mark.asyncio
async def test_tool_execution(mocker):
    ""Test that tools can be executed through the API."""
    from mcp_server.main import app, mcp
    
    # Mock the MCP instance and tool
    mock_tool = mock_mcp_tool("test_tool", return_value={"result": "success"})
    mocker.patch.object(mcp, 'tools', {"test_tool": mock_tool})
    
    client = TestClient(app)
    response = client.post(
        "/tools/call",
        json={"name": "test_tool", "args": {"param1": "value1"}}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}
    mock_tool.assert_awaited_once_with(param1="value1")


def test_nonexistent_tool():
    ""Test that calling a non-existent tool returns a 404 error."""
    from mcp_server.main import app
    
    client = TestClient(app)
    response = client.post(
        "/tools/call",
        json={"name": "nonexistent_tool", "args": {}}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_invalid_tool_request():
    ""Test that invalid tool requests return a 422 error."""
    from mcp_server.main import app
    
    client = TestClient(app)
    
    # Missing tool name
    response = client.post("/tools/call", json={"args": {}})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Missing args
    response = client.post("/tools/call", json={"name": "test_tool"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Invalid JSON
    response = client.post(
        "/tools/call",
        content="invalid json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_tool_execution_error(mocker):
    ""Test that tool execution errors are properly handled."""
    from mcp_server.main import app, mcp
    
    # Mock the MCP instance and tool to raise an exception
    mock_tool = mock_mcp_tool("failing_tool", side_effect=ValueError("Test error"))
    mocker.patch.object(mcp, 'tools', {"failing_tool": mock_tool})
    
    client = TestClient(app)
    response = client.post(
        "/tools/call",
        json={"name": "failing_tool", "args": {}}
    )
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_data = response.json()
    assert "error" in error_data
    assert "Test error" in error_data["error"]


def test_openapi_schema():
    ""Test that the OpenAPI schema is generated correctly."""
    from mcp_server.main import app
    
    client = TestClient(app)
    response = client.get("/openapi.json")
    
    assert response.status_code == status.HTTP_200_OK
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
    
    # Verify the tools endpoint is documented
    assert "/tools" in schema["paths"]
    assert "/tools/call" in schema["paths"]
    assert "/health" in schema["paths"]
