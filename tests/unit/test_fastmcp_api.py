#!/usr/bin/env python3
import sys
sys.path.insert(0, "src")

try:
    from fastmcp import FastMCP
    print("FastMCP imported successfully")
    
    # Create instance
    mcp = FastMCP(
        name="test",
        version="0.1.0"
    )
    print("FastMCP instance created")
    
    # Check available methods
    methods = [m for m in dir(mcp) if not m.startswith('_')]
    print(f"Available methods: {methods}")
    
    # Check specifically for run methods
    run_methods = [m for m in methods if 'run' in m.lower()]
    print(f"Run methods: {run_methods}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
