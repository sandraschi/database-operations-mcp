"""Simple test script to verify FastMCP initialization."""
from fastmcp import FastMCP

print("Testing FastMCP initialization...")

# Test 1: Minimal initialization
try:
    mcp = FastMCP(name="test-mcp")
    print("✓ Successfully created FastMCP with name")
    print(f"   - Name: {getattr(mcp, 'name', 'Not set')}")
    print(f"   - Available attributes: {[attr for attr in dir(mcp) if not attr.startswith('_')]}")
except Exception as e:
    print(f"✗ Failed to create FastMCP: {e}")
