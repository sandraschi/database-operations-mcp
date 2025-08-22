"""
Test script for verifying stdio communication with the Database Operations MCP server.

This script can be used to test the MCP server by sending commands via stdio.
"""
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

def send_command(command, params=None):
    """Send a command to the MCP server via stdio."""
    if params is None:
        params = {}
    
    message = {
        "jsonrpc": "2.0",
        "method": command,
        "params": params,
        "id": 1
    }
    
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
    logger.info("Testing connection to MCP server...")
    response = send_command("test_connection")
    if response and 'result' in response:
        logger.info(f"Connection test successful: {response['result']}")
        return True
    else:
        logger.error(f"Connection test failed: {response}")
        return False

if __name__ == "__main__":
    logger.info("Starting MCP client test...")
    
    # Test connection
    if not test_connection():
        logger.error("Connection test failed, exiting...")
        sys.exit(1)
    
    logger.info("All tests completed successfully")
