import os
import sys
import subprocess
import json
from pathlib import Path

def build_dxt_package():
    # Configuration
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    package_name = "database-operations-mcp"
    output_file = dist_dir / f"{package_name}.dxt"
    
    # Create dist directory if it doesn't exist
    dist_dir.mkdir(exist_ok=True)
    
    print(f"Building DXT package to: {output_file}")
    
    try:
        # Build the package
        cmd = ["dxt", "pack", "--output", str(output_file)]
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("DXT pack command output:")
        print(result.stdout)
        
        if result.stderr:
            print("Error output:")
            print(result.stderr)
        
        # Verify the package was created
        if output_file.exists():
            file_size = output_file.stat().st_size / (1024 * 1024)  # in MB
            print(f"✅ Successfully created DXT package: {output_file} ({file_size:.2f} MB)")
            return True
        else:
            print("❌ Failed to create DXT package: Output file not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ DXT pack command failed with return code {e.returncode}:")
        print(f"Command: {e.cmd}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = build_dxt_package()
    sys.exit(0 if success else 1)
