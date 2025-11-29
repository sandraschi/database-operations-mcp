"""
Browser bookmark management services.

This package provides browser-specific bookmark management implementations
for various browsers including Firefox, Chrome, Edge, Brave, and Safari.
"""

from database_operations_mcp.services.browser.base_browser import (
    BaseBrowserManager,
)
from database_operations_mcp.services.browser.chrome_core import ChromeManager

__all__ = ["BaseBrowserManager", "ChromeManager"]
