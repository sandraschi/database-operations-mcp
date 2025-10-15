# Simple FastMCP check
print("Testing FastMCP...")

try:
    from fastmcp import FastMCP

    # Test 1: Basic initialization
    print("\nTest 1: Basic initialization")
    mcp = FastMCP(name="test-mcp")
    print(f"- Success! Name: {getattr(mcp, 'name', 'Not set')}")

    # Test 2: Check available attributes
    print("\nTest 2: Available attributes")
    attrs = [a for a in dir(mcp) if not a.startswith("_")]
    print(f"- Found {len(attrs)} attributes")
    print(f"- First few: {attrs[:5]}")

    print("\nAll tests completed successfully!")

except Exception as e:
    print(f"\nError: {e}")
    import traceback

    traceback.print_exc()
