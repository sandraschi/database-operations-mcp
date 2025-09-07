"""
Script to update imports after renaming 'handlers' to 'tools'.
"""

import os
import re
from pathlib import Path

def update_imports_in_file(file_path: str):
    """Update imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update imports from database_operations_mcp.handlers
        updated_content = re.sub(
            r'from\s+database_operations_mcp\.handlers\.',
            'from database_operations_mcp.tools.',
            content
        )
        
        # Update relative imports from .handlers
        updated_content = re.sub(
            r'from\s+\.handlers\.',
            'from .',
            updated_content
        )
        
        # Update imports with absolute paths
        updated_content = re.sub(
            r'from\s+\"\.\.handlers\.',
            'from "..',
            updated_content
        )
        
        # Only write if changes were made
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"Updated imports in {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def main():
    """Update imports in all Python files."""
    root_dir = Path('d:/Dev/repos/database-operations-mcp/src')
    
    # Process all Python files in the project
    for py_file in root_dir.rglob('*.py'):
        # Skip files in __pycache__ directories
        if '__pycache__' in str(py_file):
            continue
            
        update_imports_in_file(str(py_file))
    
    print("Import updates complete!")

if __name__ == "__main__":
    main()
