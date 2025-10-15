"""
Unit tests for the monitor_registry function in registry_tools.py
"""

from unittest.mock import ANY, MagicMock, patch

import pytest

# Import the function to test

# Test data
TEST_REGISTRY_PATH = r"HKEY_CURRENT_USER\\Software\\TestKey"
TEST_CALLBACK_URL = "http://example.com/webhook"


@pytest.fixture(autouse=True)
def reset_monitors():
    """Reset the _active_monitors dictionary before each test."""
    _active_monitors.clear()
    yield
    _active_monitors.clear()


@patch("database_operations_mcp.handlers.registry_tools.RegistryMonitor")
def test_start_monitoring(mock_registry_monitor):
    """Test starting registry monitoring."""
    # Setup
    mock_instance = MagicMock()
    mock_registry_monitor.return_value = mock_instance

    # Test
    result = monitor_registry(
        path=TEST_REGISTRY_PATH, action="start", callback_url=TEST_CALLBACK_URL
    )

    # Verify
    assert result["status"] == "success"
    assert result["monitoring"] is True
    assert "monitor_id" in result
    assert TEST_REGISTRY_PATH in _active_monitors
    mock_registry_monitor.assert_called_once_with(
        path=TEST_REGISTRY_PATH,
        callback=ANY,  # We'll verify the callback separately
    )
    mock_instance.start.assert_called_once()


@patch("database_operations_mcp.handlers.registry_tools.RegistryMonitor")
def test_start_monitoring_already_running(mock_registry_monitor):
    """Test starting monitoring when already monitoring the path."""
    # Setup - Add a monitor for the test path
    mock_monitor = MagicMock()
    _active_monitors[TEST_REGISTRY_PATH] = mock_monitor

    # Test
    result = monitor_registry(
        path=TEST_REGISTRY_PATH, action="start", callback_url=TEST_CALLBACK_URL
    )

    # Verify
    assert result["status"] == "error"
    assert "already monitoring" in result["message"].lower()
    assert result["monitoring"] is True
    mock_registry_monitor.assert_not_called()


@patch("database_operations_mcp.handlers.registry_tools.RegistryMonitor")
def test_stop_monitoring(mock_registry_monitor):
    """Test stopping registry monitoring."""
    # Setup - Add a monitor for the test path
    mock_monitor = MagicMock()
    _active_monitors[TEST_REGISTRY_PATH] = mock_monitor

    # Test
    result = monitor_registry(path=TEST_REGISTRY_PATH, action="stop")

    # Verify
    assert result["status"] == "success"
    assert result["monitoring"] is False
    assert TEST_REGISTRY_PATH not in _active_monitors
    mock_monitor.stop.assert_called_once()


@patch("database_operations_mcp.handlers.registry_tools.RegistryMonitor")
def test_stop_monitoring_not_running(mock_registry_monitor):
    """Test stopping monitoring when no monitor exists for the path."""
    # Test
    result = monitor_registry(path=TEST_REGISTRY_PATH, action="stop")

    # Verify
    assert result["status"] == "error"
    assert "no active monitor" in result["message"].lower()
    assert result["monitoring"] is False
    mock_registry_monitor.assert_not_called()


def test_monitor_registry_invalid_action():
    """Test with an invalid action."""
    result = monitor_registry(path=TEST_REGISTRY_PATH, action="invalid_action")

    assert result["status"] == "error"
    assert "invalid action" in result["message"].lower()
    assert result["monitoring"] is False


@patch("database_operations_mcp.handlers.registry_tools.RegistryMonitor")
def test_monitor_registry_callback_error_handling(mock_registry_monitor, caplog):
    """Test error handling in the callback function."""
    # Setup
    mock_instance = MagicMock()
    mock_registry_monitor.return_value = mock_instance

    # Create a mock callback that will raise an exception
    def mock_callback(changes):
        raise Exception("Test error in callback")

    # Replace the callback creation to return our mock
    with patch(
        "database_operations_mcp.handlers.registry_tools.create_callback",
        return_value=mock_callback,
    ):
        # This should not raise an exception
        result = monitor_registry(
            path=TEST_REGISTRY_PATH, action="start", callback_url=TEST_CALLBACK_URL
        )

    # Verify the monitor was still started
    assert result["status"] == "success"
    assert result["monitoring"] is True

    # The error should be logged but not propagated
    assert "Error in registry change callback" in caplog.text


@patch("database_operations_mcp.handlers.registry_tools.RegistryMonitor")
def test_monitor_registry_start_error(mock_registry_monitor):
    """Test error handling when starting the monitor fails."""
    # Setup
    mock_instance = MagicMock()
    mock_instance.start.side_effect = Exception("Failed to start monitoring")
    mock_registry_monitor.return_value = mock_instance

    # Test
    result = monitor_registry(
        path=TEST_REGISTRY_PATH, action="start", callback_url=TEST_CALLBACK_URL
    )

    # Verify
    assert result["status"] == "error"
    assert "failed to start monitoring" in result["message"].lower()
    assert result["monitoring"] is False
    assert TEST_REGISTRY_PATH not in _active_monitors


@patch("database_operations_mcp.handlers.registry_tools.RegistryMonitor")
def test_monitor_registry_stop_error(mock_registry_monitor):
    """Test error handling when stopping the monitor fails."""
    # Setup - Add a monitor that will raise an exception when stopped
    mock_monitor = MagicMock()
    mock_monitor.stop.side_effect = Exception("Failed to stop monitoring")
    _active_monitors[TEST_REGISTRY_PATH] = mock_monitor

    # Test
    result = monitor_registry(path=TEST_REGISTRY_PATH, action="stop")

    # Verify
    assert result["status"] == "error"
    assert "error stopping monitor" in result["message"].lower()
    # The monitor should still be removed from active monitors
    assert TEST_REGISTRY_PATH not in _active_monitors
