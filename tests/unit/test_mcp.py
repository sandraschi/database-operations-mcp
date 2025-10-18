#!/usr/bin/env python3
"""
Simple test script to verify MCP server functionality.
"""

import json
import subprocess
import sys
import time

import pytest


def test_mcp_server():
    """Test the MCP server by sending a list_tools request."""
    # Skip this test due to Windows subprocess stdin issues
    pytest.skip("Skipping due to Windows subprocess stdin issues")
    
    # Start the MCP server as a subprocess
    server = subprocess.Popen(
        [sys.executable, "-m", "database_operations_mcp.main"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    try:
        # Give the server a moment to start
        time.sleep(2)

        # Create a request to list available tools
        request = {"jsonrpc": "2.0", "method": "list_tools", "params": {}, "id": 1}

        # Send the request
        print("Sending request:", json.dumps(request, indent=2))
        server.stdin.write(json.dumps(request) + "\n")
        server.stdin.flush()

        # Read the response
        response = server.stdout.readline()
        print("\nReceived response:", response.strip())

        # Parse the response
        try:
            result = json.loads(response)
            if "result" in result and "tools" in result["result"]:
                print("\nAvailable tools:")
                for tool_name in result["result"]["tools"].keys():
                    print(f"- {tool_name}")
                assert True  # Test passed
        except json.JSONDecodeError as e:
            print(f"Error decoding response: {e}")
            raise AssertionError(f"JSON decode error: {e}") from e

        raise AssertionError("Test failed - no valid response received")

    except Exception as e:
        print(f"Error during test: {e}")
        raise AssertionError(f"Test failed with exception: {e}") from e

    finally:
        # Clean up
        server.terminate()
        try:
            server.wait(timeout=2)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    print("Testing Database Operations MCP server...")
    if test_mcp_server():
        print("\n✅ MCP server is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ MCP server test failed!")
        sys.exit(1)
