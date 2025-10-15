"""Tests for the MCP server template."""

from fastapi.testclient import TestClient
from mcp_server.main import app

client = TestClient(app)


def test_example_tool():
    """Test the example tool execution."""
    # Test with required parameter
    response = client.post("/tools/example_tool", json={"param1": "test"})
    assert response.status_code == 200
    assert response.json()["result"] == "Processed test with 42"

    # Test with optional parameter overridden
    response = client.post("/tools/example_tool", json={"param1": "test", "param2": 100})
    assert response.status_code == 200
    assert response.json()["result"] == "Processed test with 100"

    # Test validation error
    response = client.post(
        "/tools/example_tool",
        json={},  # Missing required param1
    )
    assert response.status_code == 422  # Validation error
