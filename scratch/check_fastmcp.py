import fastmcp
import inspect
print(f"FastMCP version: {getattr(fastmcp, '__version__', 'unknown')}")
print(f"FastMCP path: {fastmcp.__file__}")

from fastmcp import FastMCP
mcp = FastMCP("test")
print("FastMCP attributes:")
for attr in dir(mcp):
    if not attr.startswith("__"):
        print(f"  {attr}")
