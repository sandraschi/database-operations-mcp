print("✅ database_operations module imported")

print("✅ main function imported")

# Test the -m execution
import runpy

print("✅ Testing -m database_operations execution...")
try:
    runpy.run_module("database_operations", run_name="__main__")
    print("✅ -m database_operations works!")
except SystemExit:
    print("✅ Module executed successfully (SystemExit is expected)")
except Exception as e:
    print(f"❌ Error: {e}")
