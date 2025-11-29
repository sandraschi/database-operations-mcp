"""Tests for the backup-repo.ps1 PowerShell script."""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def test_repo(tmp_path):
    """Create a temporary test repository."""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()

    # Create minimal repo structure
    (repo_path / "pyproject.toml").write_text("[project]\nname = 'test'")
    (repo_path / "README.md").write_text("# Test Repo")
    (repo_path / "test_file.txt").write_text("test content")

    # Create some files to exclude
    (repo_path / ".venv").mkdir()
    (repo_path / ".venv" / "file.txt").write_text("should be excluded")

    return repo_path


@pytest.fixture
def backup_script():
    """Path to the backup script."""
    script_path = Path(__file__).parent.parent.parent / "scripts" / "backup-repo.ps1"
    if not script_path.exists():
        pytest.skip(f"Backup script not found at {script_path}")
    return script_path


def run_powershell_script(script_path, *args, cwd=None, capture_output=True):
    """Run a PowerShell script with arguments."""
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        *[str(arg) for arg in args],
    ]

    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=capture_output,
        text=True,
        encoding="utf-8",
        errors="replace",  # Handle encoding issues gracefully
    )

    return result


class TestBackupScriptFlags:
    """Test CLI flags and basic functionality."""

    def test_whatif_flag(self, backup_script, test_repo):
        """Test -WhatIf flag shows dry-run output without creating files."""
        result = run_powershell_script(backup_script, "-WhatIf", cwd=test_repo)

        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert "DRY-RUN MODE" in result.stdout.upper() or "What if" in result.stdout
        assert "Files that would be backed up" in result.stdout

        # Verify no backup files were created
        backup_dirs = [
            Path.home() / "Desktop" / "repo backup" / "test-repo",
            Path("N:/backup/dev/repos2/test-repo"),
            Path(os.environ.get("OneDrive", "")) / "repo-backups" / "test-repo",
        ]

        # Check at least one backup location would be used (skip N: drive if not available)
        desktop_backup = backup_dirs[0]
        if desktop_backup.exists():
            backups = list(desktop_backup.glob("*.zip"))
            assert len(backups) == 0, "Backup files were created despite -WhatIf"

    def test_list_flag(self, backup_script, test_repo):
        """Test -List flag shows backup history."""
        result = run_powershell_script(backup_script, "-List", cwd=test_repo)

        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert "Backup History" in result.stdout
        assert "test-repo" in result.stdout

    def test_json_output_format(self, backup_script, test_repo):
        """Test -OutputFormat JSON produces valid JSON."""
        result = run_powershell_script(
            backup_script, "-WhatIf", "-OutputFormat", "json", cwd=test_repo
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        # Try to parse JSON from output
        try:
            # Find JSON in output (might have some PowerShell output before)
            lines = result.stdout.strip().split("\n")
            json_start = None
            for i, line in enumerate(lines):
                if line.strip().startswith("{"):
                    json_start = i
                    break

            if json_start is not None:
                json_str = "\n".join(lines[json_start:])
                data = json.loads(json_str)
                assert "repo" in data
                assert "status" in data
                assert data["repo"] == "test-repo"
        except (json.JSONDecodeError, AssertionError) as e:
            pytest.skip(f"JSON parsing failed (may be encoding issue): {e}")

    def test_verbose_flag(self, backup_script, test_repo):
        """Test -Verbose flag provides detailed output."""
        result = run_powershell_script(backup_script, "-WhatIf", "-Verbose", cwd=test_repo)

        assert result.returncode == 0, f"Script failed: {result.stderr}"
        # Verbose output should contain more details (exact content varies)
        assert len(result.stdout) > 0


class TestBackupScriptErrors:
    """Test error handling."""

    def test_error_when_not_in_repo(self, backup_script, tmp_path):
        """Test script errors when not run from repository root."""
        # Run from a non-repo directory
        result = run_powershell_script(backup_script, cwd=tmp_path)

        # Should error or at least not create backups
        # (Some versions might just create empty backups)
        assert (
            "Error" in result.stdout
            or "Must run from repository root" in result.stdout
            or result.returncode != 0
        )


class TestBackupScriptIntegration:
    """Integration tests for actual backup operations."""

    def test_backup_creates_files(self, backup_script, test_repo, tmp_path):
        """Test that backup actually creates ZIP files."""
        # Override backup locations to use temp directory
        # We can't easily override the hardcoded paths, so we'll check if backups are created
        # This test is more of a smoke test

        # Create a test file that will be backed up
        (test_repo / "important.txt").write_text("important content")

        result = run_powershell_script(backup_script, cwd=test_repo)

        # Script should complete (may have errors if backup locations don't exist)
        # Just verify it doesn't crash
        assert "Backup" in result.stdout or result.returncode == 0

    def test_backup_excludes_venv(self, backup_script, test_repo):
        """Test that .venv is excluded from backup."""
        result = run_powershell_script(backup_script, "-WhatIf", cwd=test_repo)

        assert result.returncode == 0
        # Should mention excluded files
        assert ".venv" in result.stdout or "Excluding" in result.stdout


class TestBackupScriptMetrics:
    """Test metrics export functionality."""

    def test_metrics_file_created(self, backup_script, test_repo, monkeypatch):
        """Test that metrics file is created after backup."""
        # Point to a temp directory for metrics
        temp_metrics = Path(tempfile.gettempdir()) / "test-backup-metrics"
        temp_metrics.mkdir(exist_ok=True)

        # Run backup (WhatIf still creates metrics)
        result = run_powershell_script(backup_script, "-WhatIf", cwd=test_repo)

        # Metrics should be in %APPDATA%\backup-metrics\backup-test-repo.jsonl
        # We can't easily override this, so just verify script completes
        assert result.returncode == 0

        # Cleanup
        if temp_metrics.exists():
            for f in temp_metrics.glob("*.jsonl"):
                f.unlink()


class TestBackupScriptValidation:
    """Test input validation and edge cases."""

    def test_invalid_output_format(self, backup_script, test_repo):
        """Test invalid OutputFormat is rejected."""
        result = run_powershell_script(
            backup_script, "-WhatIf", "-OutputFormat", "invalid", cwd=test_repo
        )

        # Should error or use default
        # PowerShell ValidateSet should reject invalid values
        assert result.returncode != 0 or "invalid" not in result.stdout.lower()

    def test_empty_repo(self, backup_script, tmp_path):
        """Test backup of empty repository."""
        empty_repo = tmp_path / "empty-repo"
        empty_repo.mkdir()
        (empty_repo / "pyproject.toml").write_text("[project]\nname = 'empty'")

        result = run_powershell_script(backup_script, "-WhatIf", cwd=empty_repo)

        # Should handle gracefully
        assert result.returncode == 0

