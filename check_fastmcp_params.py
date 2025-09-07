"""Script to check FastMCP initialization parameters."""
import inspect
import fastmcp

# Get the signature of FastMCP.__init__
sig = inspect.signature(fastmcp.FastMCP.__init__)

print("FastMCP.__init__ parameters:")
for name, param in sig.parameters.items():
    print(f"- {name}: {param.default if param.default != inspect.Parameter.empty else 'required'}")

# Try to create an instance with minimal parameters
try:
    mcp = fastmcp.FastMCP()
    print("\nSuccessfully created FastMCP instance with no parameters")
except Exception as e:
    print(f"\nError creating FastMCP instance: {e}")
