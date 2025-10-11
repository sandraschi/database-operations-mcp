#!/usr/bin/env python3
'''Convert tool docstrings from """ to single quotes.'''

import os
import re
from pathlib import Path

def convert_file_docstrings(filepath):
    '''Convert all docstrings in a file from triple double to single quotes.'''
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace docstrings after function definitions
    # Pattern: function def followed by """..."""
    pattern = r'(async def |def )([^:]+:\s*->\s*[^:]+:)\s*"""(.*?)"""'
    
    def replace_docstring(match):
        prefix = match.group(1)
        func_sig = match.group(2)
        docstring_content = match.group(3)
        return f"{prefix}{func_sig}\n    '''{docstring_content}'''"
    
    new_content = re.sub(pattern, replace_docstring, content, flags=re.DOTALL)
    
    # Count changes
    old_count = content.count('"""')
    new_count = new_content.count('"""')
    changes = (old_count - new_count) // 2
    
    if changes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return changes
    return 0

def main():
    '''Convert all tool files.'''
    tools_dir = Path('src/database_operations_mcp/tools')
    total_changes = 0
    
    for py_file in tools_dir.rglob('*.py'):
        if py_file.name.startswith('_'):
            continue
        
        changes = convert_file_docstrings(py_file)
        if changes > 0:
            print(f"✅ {py_file.relative_to('src')}: {changes} docstrings converted")
            total_changes += changes
    
    print(f"\n📊 Total: {total_changes} docstrings converted to single quotes")

if __name__ == '__main__':
    main()


