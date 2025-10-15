#!/usr/bin/env python3
"""
Test script for the Database Operations MCP server.

This script starts the MCP server and sends a test request to verify
that it's working correctly over stdio.
"""

import json
import subprocess
import sys
import time


def test_mcp_server():
    """Test the MCP server by sending a request over stdio."""
    # Start the MCP server as a subprocess
    process = subprocess.Popen(
        [sys.executable, "-m", "database_operations_mcp.main"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    try:
        # Give the server a moment to start
        time.sleep(1)

        # Send a test request (list available tools)
        request = {"jsonrpc": "2.0", "method": "list_tools", "params": {}, "id": 1}

        # Send the request
        print("Sending request:", json.dumps(request, indent=2))
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()

        # Read the response
        response = process.stdout.readline()
        print("Received response:", response.strip())

        # Parse the response
        try:
            result = json.loads(response)
            if "result" in result and "tools" in result["result"]:
                print("\nSuccess! The MCP server is working correctly.")
                print(f"Available tools: {', '.join(result['result']['tools'].keys())}")
                return True
            else:
                print("Error: Unexpected response format")
                return False

        except json.JSONDecodeError as e:
            print(f"Error decoding response: {e}")
            print(f"Raw response: {response}")
            return False

    except Exception as e:
        print(f"Error during test: {e}")
        return False

    finally:
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    print("Testing Database Operations MCP server...\n")
    success = test_mcp_server()
    sys.exit(0 if success else 1)
