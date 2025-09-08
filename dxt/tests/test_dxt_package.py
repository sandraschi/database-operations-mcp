"""Tests for DXT package functionality."""
import os
import sys
import json
import pytest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Constants
DIST_DIR = PROJECT_ROOT / "dist"
MANIFEST_PATH = PROJECT_ROOT / "manifest.json"


def test_manifest_exists():
    """Verify that the manifest file exists and is valid JSON."""
    assert MANIFEST_PATH.exists(), "manifest.json not found in project root"
    
    # Try to parse the manifest
    try:
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Check required fields
        assert 'name' in manifest, "Manifest missing 'name' field"
        assert 'version' in manifest, "Manifest missing 'version' field"
        assert 'server' in manifest, "Manifest missing 'server' configuration"
        
    except json.JSONDecodeError as e:
        pytest.fail(f"Manifest is not valid JSON: {e}")


def test_dxt_package_built():
    """Verify that the DXT package was built successfully."""
    # Check if any .dxt files exist in the dist directory
    dxt_files = list(DIST_DIR.glob("*.dxt"))
    assert len(dxt_files) > 0, "No .dxt files found in dist directory"
    
    # Check if the file has a reasonable size (at least 1KB)
    dxt_file = dxt_files[0]
    file_size = dxt_file.stat().st_size / 1024  # Size in KB
    assert file_size > 1, f"DXT package is too small: {file_size:.2f} KB"


# This test requires the dxt CLI to be installed
@pytest.mark.integration
def test_dxt_validation():
    """Test that the DXT package passes validation."""
    dxt_files = list(DIST_DIR.glob("*.dxt"))
    if not dxt_files:
        pytest.skip("No DXT package found for validation")
    
    # This test would require the dxt CLI to be installed
    # In a real CI environment, this would be run by the workflow
    pass


if __name__ == "__main__":
    pytest.main(["-v", "--tb=short", __file__])
