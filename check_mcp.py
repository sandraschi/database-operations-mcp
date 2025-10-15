# Simple FastMCP check
try:
    from fastmcp import FastMCP

    mcp = FastMCP()
    print(f"FastMCP initialized successfully. Name: {getattr(mcp, 'name', 'Not set')}")
    print(f"Available attributes: {[a for a in dir(mcp) if not a.startswith('_')]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
