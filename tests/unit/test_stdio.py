"""
Test script for verifying stdio communication with the Database Operations MCP server.

This script can be used to test the MCP server by sending commands via stdio.
"""

import json
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def send_command(command, params=None):
    """Send a command to the MCP server via stdio."""
    if params is None:
        params = {}

    message = {"jsonrpc": "2.0", "method": command, "params": params, "id": 1}

    # Send the message
    print(json.dumps(message), flush=True)

    # Wait for response
    response = sys.stdin.readline()
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse response: {e}")
        return None


def test_connection():
    """Test basic connection to the MCP server."""
    import subprocess
    import json
    
    # Start the MCP server process
    server_process = subprocess.Popen(
        ["python", "-m", "database_operations_mcp.main"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Send a test request
        request = {
            "jsonrpc": "2.0",
            "method": "test_connection",
            "params": {},
            "id": 1
        }
        
        # Send request
        server_process.stdin.write(json.dumps(request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            assert response["id"] == 1
            assert "result" in response or "error" in response
            return True
        return False
        
    finally:
        # Clean up
        server_process.terminate()
        server_process.wait()


if __name__ == "__main__":
    logger.info("Starting MCP client test...")

    # Test connection
    if not test_connection():
        logger.error("Connection test failed, exiting...")
        sys.exit(1)

    logger.info("All tests completed successfully")
