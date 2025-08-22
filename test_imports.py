import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from database_operations_mcp.handlers.connection_tools import register_tools
    print("Successfully imported register_tools from connection_tools.py")
    
    # Test creating a mock MCP instance
    class MockMCP:
        def __init__(self):
            self.tools = []
            
        def tool(self):
            def decorator(func):
                self.tools.append(func.__name__)
                return func
            return decorator
    
    # Test registering tools
    mcp = MockMCP()
    register_tools(mcp)
    print(f"Registered tools: {mcp.tools}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
