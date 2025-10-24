"""
Unit tests for the registry tools in registry_tools.py
"""

import winreg
from unittest.mock import MagicMock, patch

import pytest

# Test data
TEST_REGISTRY_PATH = r"HKEY_CURRENT_USER\\Software\\TestKey"
TEST_CALLBACK_URL = "http://example.com/webhook"


@pytest.fixture(autouse=True)
def reset_monitors():
    """Reset the _active_monitors dictionary before each test."""
    from database_operations_mcp.tools.registry_tools import _active_monitors

    _active_monitors.clear()
    yield
    _active_monitors.clear()


@patch("database_operations_mcp.tools.registry_tools.winreg.OpenKey")
@patch("database_operations_mcp.tools.registry_tools.winreg.QueryValueEx")
def test_read_registry_value(mock_query_value, mock_open_key):
    """Test reading a registry value."""
    # Setup
    mock_key = MagicMock()
    mock_open_key.return_value = mock_key
    mock_query_value.return_value = ("test_value", winreg.REG_SZ)

    # Import the function
    from database_operations_mcp.tools.registry_tools import read_registry_value

    if hasattr(read_registry_value, "fn"):
        actual_function = read_registry_value.fn
    else:
        actual_function = read_registry_value

    # Act
    result = actual_function(TEST_REGISTRY_PATH, "test_value")

    # Assert
    assert result["success"] is True
    assert result["value"] == "test_value"
    assert result["type"] == "REG_SZ"


@patch("database_operations_mcp.tools.registry_tools.winreg.OpenKey")
@patch("database_operations_mcp.tools.registry_tools.winreg.SetValueEx")
def test_write_registry_value(mock_set_value, mock_open_key):
    """Test writing a registry value."""
    # Setup
    mock_key = MagicMock()
    mock_open_key.return_value = mock_key

    # Import the function
    from database_operations_mcp.tools.registry_tools import write_registry_value

    if hasattr(write_registry_value, "fn"):
        actual_function = write_registry_value.fn
    else:
        actual_function = write_registry_value

    # Act
    result = actual_function(TEST_REGISTRY_PATH, "test_value", "test_data")

    # Assert
    assert result["success"] is True
    assert "Value written successfully" in result["message"]


@patch("database_operations_mcp.tools.registry_tools.winreg.OpenKey")
@patch("database_operations_mcp.tools.registry_tools.winreg.EnumKey")
def test_list_registry_keys(mock_enum_key, mock_open_key):
    """Test listing registry keys."""
    # Setup
    mock_key = MagicMock()
    mock_open_key.return_value = mock_key
    # Create OSError with winerror attribute
    no_more_data_error = OSError(259, "No more data")
    no_more_data_error.winerror = 259
    mock_enum_key.side_effect = ["key1", "key2", "key3", no_more_data_error]

    # Import the function
    from database_operations_mcp.tools.registry_tools import list_registry_keys

    if hasattr(list_registry_keys, "fn"):
        actual_function = list_registry_keys.fn
    else:
        actual_function = list_registry_keys

    # Act
    result = actual_function(TEST_REGISTRY_PATH)

    # Assert
    assert result["success"] is True
    assert "subkeys" in result
    assert len(result["subkeys"]) == 3


@patch("database_operations_mcp.tools.registry_tools.winreg.OpenKey")
@patch("database_operations_mcp.tools.registry_tools.winreg.EnumValue")
def test_list_registry_values(mock_enum_value, mock_open_key):
    """Test listing registry values."""
    # Setup
    mock_key = MagicMock()
    mock_open_key.return_value = mock_key
    # Create OSError with winerror attribute
    no_more_data_error = OSError(259, "No more data")
    no_more_data_error.winerror = 259
    mock_enum_value.side_effect = [
        ("value1", "data1", winreg.REG_SZ),
        ("value2", "data2", winreg.REG_DWORD),
        no_more_data_error,
    ]

    # Import the function
    from database_operations_mcp.tools.registry_tools import list_registry_values

    if hasattr(list_registry_values, "fn"):
        actual_function = list_registry_values.fn
    else:
        actual_function = list_registry_values

    # Act
    result = actual_function(TEST_REGISTRY_PATH)

    # Assert
    assert result["success"] is True
    assert "values" in result
    assert len(result["values"]) == 2
