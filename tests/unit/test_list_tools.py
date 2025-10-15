#!/usr/bin/env python3
"""
Test script to list available tools from the MCP server.
"""

import json
import subprocess
import sys


def test_mcp_server():
    # Start the MCP server as a subprocess
    server_process = subprocess.Popen(
        [sys.executable, "-m", "database_operations_mcp.main"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    try:
        # Wait for the server to start
        import time

        time.sleep(2)

        # Create a request to list tools
        request = {"jsonrpc": "2.0", "method": "list_tools", "params": {}, "id": 1}

        # Send the request
        server_process.stdin.write(json.dumps(request) + "\n")
        server_process.stdin.flush()

        # Read the response
        response = server_process.stdout.readline()

        # Print the response
        print("Server response:")
        try:
            response_data = json.loads(response)
            print(json.dumps(response_data, indent=2))

            if "result" in response_data and "tools" in response_data["result"]:
                print("\nAvailable tools:")
                for tool_name in response_data["result"]["tools"].keys():
                    print(f"- {tool_name}")
                return True
            return False

        except json.JSONDecodeError:
            print("Error: Invalid JSON response")
            print(f"Raw response: {response}")
            return False

    finally:
        # Clean up
        server_process.terminate()
        try:
            server_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            server_process.kill()


if __name__ == "__main__":
    print("Testing MCP server...")
    success = test_mcp_server()
    print("\nTest completed successfully!" if success else "\nTest failed!")
    sys.exit(0 if success else 1)
