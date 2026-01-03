"""Tests for utils module."""
import pytest
from pathlib import Path
import stat

from bpsai_pair.core.utils import repo_root, ensure_executable


class TestRepoRoot:
    """Tests for repo_root function."""

    def test_finds_repo_root(self, tmp_path, monkeypatch):
        """Test finding repo root when .git exists."""
        (tmp_path / ".git").mkdir()
        monkeypatch.chdir(tmp_path)
        result = repo_root()
        assert result == tmp_path

    def test_raises_when_not_in_repo(self, tmp_path, monkeypatch):
        """Test raises SystemExit when not in repo."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            repo_root()
        assert "Run from repo root" in str(exc_info.value)


class TestEnsureExecutable:
    """Tests for ensure_executable function."""

    def test_makes_executable(self, tmp_path):
        """Test making file executable."""
        test_file = tmp_path / "script.sh"
        test_file.write_text("#!/bin/bash\necho hello")
        # Remove all execute bits
        test_file.chmod(0o644)

        ensure_executable(test_file)

        mode = test_file.stat().st_mode
        # Check that execute bits are set
        assert mode & stat.S_IXUSR  # Owner can execute
        assert mode & stat.S_IXGRP  # Group can execute
        assert mode & stat.S_IXOTH  # Others can execute

    def test_preserves_read_write(self, tmp_path):
        """Test that read/write permissions are preserved."""
        test_file = tmp_path / "script.sh"
        test_file.write_text("#!/bin/bash")
        test_file.chmod(0o640)  # rw-r-----

        ensure_executable(test_file)

        mode = test_file.stat().st_mode
        # Check read permissions preserved
        assert mode & stat.S_IRUSR
        assert mode & stat.S_IRGRP
        # Check write permissions preserved
        assert mode & stat.S_IWUSR

    def test_already_executable(self, tmp_path):
        """Test file that's already executable."""
        test_file = tmp_path / "script.sh"
        test_file.write_text("#!/bin/bash")
        test_file.chmod(0o755)  # Already executable

        ensure_executable(test_file)

        mode = test_file.stat().st_mode
        # Still executable
        assert mode & stat.S_IXUSR
