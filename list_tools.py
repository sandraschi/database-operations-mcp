#!/usr/bin/env python3
"""
List all available tools in the MCP server.
"""
import sys
import json

def main():
    # Create a simple JSON-RPC request to list tools
    request = {
        "jsonrpc": "2.0",
        "method": "list_tools",
        "params": {},
        "id": 1
    }
    
    # Print the request to stdout (will be read by the MCP server)
    print(json.dumps(request))
    
    # Read the response from stdin
    response = sys.stdin.readline()
    try:
        result = json.loads(response)
        print("\nAvailable tools:")
        for tool_name, tool_info in result['result']['tools'].items():
            print(f"\n{tool_name}:")
            print(f"  Description: {tool_info.get('description', 'No description')}")
            print(f"  Parameters: {json.dumps(tool_info.get('parameters', {}), indent=4)}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error: {e}")
        print(f"Raw response: {response}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
