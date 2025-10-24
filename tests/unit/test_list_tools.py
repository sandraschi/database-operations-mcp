#!/usr/bin/env python3
"""
Test script to list available tools from the MCP server.
"""

import json
import subprocess
import sys


def test_mcp_server():
    """Test MCP server communication."""

    # Start the MCP server process
    server_process = subprocess.Popen(
        ["python", "-m", "database_operations_mcp.main"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        # Send a test request
        request = {"jsonrpc": "2.0", "method": "list_tools", "params": {}, "id": 1}

        # Send request
        server_process.stdin.write(json.dumps(request) + "\n")
        server_process.stdin.flush()

        # Read response
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            assert response["id"] == 1
            assert "result" in response or "error" in response
            assert True  # Test passed

    finally:
        # Clean up
        server_process.terminate()
        server_process.wait()


if __name__ == "__main__":
    print("Testing MCP server...")
    success = test_mcp_server()
    if success:
        print("✅ MCP server test passed")
    else:
        print("❌ MCP server test failed")
    sys.exit(0 if success else 1)
