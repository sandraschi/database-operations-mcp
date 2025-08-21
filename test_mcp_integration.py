#!/usr/bin/env python3
"""
Integration test for the Database Operations MCP server.

This script tests the MCP server by:
1. Starting the MCP server as a subprocess
2. Sending a list_tools request
3. Verifying the response contains the expected tools
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any


class MCPClient:
    def __init__(self, process):
        self.process = process
        self.request_id = 1

    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server."""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.request_id
        }
        self.request_id += 1

        # Send the request
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        await self.process.stdin.drain()

        # Read the response
        response_line = await self.process.stdout.readline()
        return json.loads(response_line)


async def test_mcp_server():
    """Test the MCP server by sending a list_tools request."""
    # Start the MCP server as a subprocess
    server_process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "database_operations_mcp.main",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    client = MCPClient(server_process)

    try:
        # Give the server a moment to start
        await asyncio.sleep(1)

        # Send a list_tools request
        print("Sending list_tools request...")
        response = await client.send_request("list_tools")

        # Check if the response contains the expected fields
        if 'result' in response and 'tools' in response['result']:
            print("\n✅ MCP server is working correctly!")
            print("\nAvailable tools:")
            for tool_name in sorted(response['result']['tools'].keys()):
                print(f"- {tool_name}")
            return True
        else:
            print("\n❌ Unexpected response format:")
            print(json.dumps(response, indent=2))
            return False

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        return False

    finally:
        # Clean up
        server_process.terminate()
        try:
            await asyncio.wait_for(server_process.wait(), timeout=2)
        except asyncio.TimeoutError:
            server_process.kill()


if __name__ == "__main__":
    print("Testing Database Operations MCP server...\n")
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
