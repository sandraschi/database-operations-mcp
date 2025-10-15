"""Test script to verify FastMCP initialization."""


def safe_print(*args, **kwargs):
    """Print function that works reliably on Windows."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback for Windows console with limited encoding
        text = " ".join(str(arg) for arg in args)
        print(text.encode("ascii", "replace").decode("ascii"), **kwargs)


def test_fastmcp_init():
    safe_print("Testing FastMCP initialization...")

    try:
        from fastmcp import FastMCP
    except ImportError as e:
        safe_print(f"[ERROR] Failed to import FastMCP: {e}")
        return

    # Test 1: Minimal initialization
    try:
        mcp1 = FastMCP()
        safe_print("[PASS] Test 1: Successfully created FastMCP with no parameters")
        safe_print(f"   - Name: {getattr(mcp1, 'name', 'Not set')}")
    except Exception as e:
        safe_print(f"[FAIL] Test 1: Failed to create FastMCP with no parameters: {e}")

    # Test 2: With name and version only
    try:
        mcp2 = FastMCP(name="test-mcp", version="1.0.0")
        safe_print("\n[PASS] Test 2: Successfully created FastMCP with name and version")
        safe_print(f"   - Name: {getattr(mcp2, 'name', 'Not set')}")
        safe_print(f"   - Version: {getattr(mcp2, 'version', 'Not set')}")
    except Exception as e:
        safe_print(f"\n[FAIL] Test 2: Failed to create FastMCP with name and version: {e}")

    # Test 3: Check available attributes
    try:
        mcp3 = FastMCP()
        safe_print("\n[PASS] Test 3: Checking available attributes")
        attrs = [attr for attr in dir(mcp3) if not attr.startswith("_")]
        safe_print(f"   - Found {len(attrs)} public attributes")
        safe_print(f"   - First 5: {', '.join(attrs[:5])}")
    except Exception as e:
        safe_print(f"\n[FAIL] Test 3: Failed to check available attributes: {e}")


if __name__ == "__main__":
    test_fastmcp_init()
    safe_print("\nTest completed. Check output above for results.")
