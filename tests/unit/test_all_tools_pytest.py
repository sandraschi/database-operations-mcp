"""
Pytest test suite for all database operation tools.

This module provides comprehensive testing for all available tools,
working around import/structure issues to provide meaningful test results.
"""

import importlib
import inspect
import sys
from pathlib import Path

import pytest


def setup_python_path():
    """Set up Python path to handle imports properly."""
    project_root = Path(__file__).parent.parent.parent.absolute()
    src_dir = project_root / "src"

    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


def get_all_tool_modules():
    """Get all tool modules to test."""
    setup_python_path()
    
    tool_modules = []
    tools_dir = Path(__file__).parent.parent.parent / "src" / "database_operations_mcp" / "tools"
    
    for py_file in tools_dir.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue
            
        relative_path = py_file.relative_to(tools_dir).with_suffix('').as_posix().replace('/', '.')
        module_name = f"database_operations_mcp.tools.{relative_path}"
        tool_modules.append(module_name)
    
    return tool_modules


def test_tool_module_imports():
    """Test that all tool modules can be imported."""
    tool_modules = get_all_tool_modules()
    import_results = []
    
    for module_name in tool_modules:
        try:
            module = importlib.import_module(module_name)
            import_results.append({
                'module': module_name,
                'status': 'success',
                'functions': len([name for name, obj in inspect.getmembers(module) 
                                if inspect.isfunction(obj) and not name.startswith('_')])
            })
        except Exception as e:
            import_results.append({
                'module': module_name,
                'status': 'failed',
                'error': str(e)
            })
    
    failed_imports = [r for r in import_results if r['status'] == 'failed']
    if failed_imports:
        pytest.fail(f"Failed to import {len(failed_imports)} modules: {failed_imports}")
    
    # Log successful imports
    successful_imports = [r for r in import_results if r['status'] == 'success']
    print(f"Successfully imported {len(successful_imports)} tool modules")


def test_tool_functions_exist():
    """Test that tool modules contain functions."""
    tool_modules = get_all_tool_modules()
    modules_without_functions = []
    
    for module_name in tool_modules:
        try:
            module = importlib.import_module(module_name)
            functions = [name for name, obj in inspect.getmembers(module) 
                        if inspect.isfunction(obj) and not name.startswith('_')]
            
            if not functions:
                modules_without_functions.append(module_name)
                
        except Exception:
            continue  # Skip modules that couldn't be imported
    
    if modules_without_functions:
        pytest.fail(f"Modules without functions: {modules_without_functions}")


def test_tool_functions_have_docstrings():
    """Test that tool functions have docstrings."""
    tool_modules = get_all_tool_modules()
    functions_without_docstrings = []
    
    for module_name in tool_modules:
        try:
            module = importlib.import_module(module_name)
            functions = inspect.getmembers(module, inspect.isfunction)
            
            for name, func in functions:
                if name.startswith('_'):
                    continue
                if not func.__doc__ or not func.__doc__.strip():
                    functions_without_docstrings.append(f"{module_name}.{name}")
                    
        except Exception:
            continue
    
    if functions_without_docstrings:
        pytest.fail(f"Functions without docstrings: {functions_without_docstrings}")


def test_tool_functions_have_type_hints():
    """Test that tool functions have type hints."""
    tool_modules = get_all_tool_modules()
    functions_without_type_hints = []
    
    for module_name in tool_modules:
        try:
            module = importlib.import_module(module_name)
            functions = inspect.getmembers(module, inspect.isfunction)
            
            for name, func in functions:
                if name.startswith('_'):
                    continue
                if not func.__annotations__:
                    functions_without_type_hints.append(f"{module_name}.{name}")
                    
        except Exception:
            continue
    
    if functions_without_type_hints:
        pytest.fail(f"Functions without type hints: {functions_without_type_hints}")


def test_database_connectors_exist():
    """Test that database connector modules exist and are importable."""
    connector_modules = [
        'database_operations_mcp.services.database.connectors.sqlite_connector',
        'database_operations_mcp.services.database.connectors.postgresql_connector',
        'database_operations_mcp.services.database.connectors.mongodb_connector',
        'database_operations_mcp.services.database.connectors.chromadb_connector',
    ]
    
    failed_connectors = []
    
    for module_name in connector_modules:
        try:
            importlib.import_module(module_name)
        except Exception as e:
            failed_connectors.append({
                'module': module_name,
                'error': str(e)
            })
    
    if failed_connectors:
        pytest.fail(f"Failed to import connector modules: {failed_connectors}")


def test_core_modules_exist():
    """Test that core modules exist and are importable."""
    core_modules = [
        'database_operations_mcp.main',
        'database_operations_mcp.database_manager',
        'database_operations_mcp.config.mcp_config',
    ]
    
    failed_core_modules = []
    
    for module_name in core_modules:
        try:
            importlib.import_module(module_name)
        except Exception as e:
            failed_core_modules.append({
                'module': module_name,
                'error': str(e)
            })
    
    if failed_core_modules:
        pytest.fail(f"Failed to import core modules: {failed_core_modules}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
