"""Tests for pyutils module."""
import pytest
from pathlib import Path

from bpsai_pair.core.utils import project_files


class TestProjectFiles:
    """Tests for project_files function."""

    def test_empty_directory(self, tmp_path):
        """Test with empty directory."""
        files = project_files(tmp_path)
        assert files == []

    def test_single_file(self, tmp_path):
        """Test with single file."""
        (tmp_path / "test.txt").write_text("content")
        files = project_files(tmp_path)
        assert len(files) == 1
        assert Path("test.txt") in files

    def test_multiple_files(self, tmp_path):
        """Test with multiple files."""
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        (tmp_path / "c.txt").write_text("c")
        files = project_files(tmp_path)
        assert len(files) == 3

    def test_nested_files(self, tmp_path):
        """Test with nested directories."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("nested")
        (tmp_path / "root.txt").write_text("root")
        files = project_files(tmp_path)
        assert len(files) == 2
        assert Path("root.txt") in files
        assert Path("subdir/nested.txt") in files

    def test_excludes_single(self, tmp_path):
        """Test excluding single directory."""
        subdir = tmp_path / ".git"
        subdir.mkdir()
        (subdir / "config").write_text("git config")
        (tmp_path / "main.py").write_text("code")
        files = project_files(tmp_path, excludes=[".git/"])
        assert len(files) == 1
        assert Path("main.py") in files

    def test_excludes_multiple(self, tmp_path):
        """Test excluding multiple directories."""
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("git")
        (tmp_path / ".venv").mkdir()
        (tmp_path / ".venv" / "lib.py").write_text("lib")
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "cache.pyc").write_text("cache")
        (tmp_path / "main.py").write_text("code")

        files = project_files(tmp_path, excludes=[".git/", ".venv/", "__pycache__/"])
        assert len(files) == 1
        assert Path("main.py") in files

    def test_excludes_none(self, tmp_path):
        """Test with excludes=None."""
        (tmp_path / "test.txt").write_text("test")
        files = project_files(tmp_path, excludes=None)
        assert len(files) == 1

    def test_excludes_empty_list(self, tmp_path):
        """Test with empty excludes list."""
        (tmp_path / "test.txt").write_text("test")
        files = project_files(tmp_path, excludes=[])
        assert len(files) == 1

    def test_excludes_partial_match(self, tmp_path):
        """Test excludes with partial directory names."""
        (tmp_path / "gitignore").write_text("patterns")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("git config")

        files = project_files(tmp_path, excludes=[".git/"])
        assert len(files) == 1
        assert Path("gitignore") in files

    def test_returns_relative_paths(self, tmp_path):
        """Test that returned paths are relative."""
        (tmp_path / "test.txt").write_text("test")
        files = project_files(tmp_path)
        for f in files:
            assert not f.is_absolute()

    def test_directories_not_included(self, tmp_path):
        """Test that directories themselves are not included."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        # No files, just directory
        files = project_files(tmp_path)
        assert len(files) == 0

    def test_deeply_nested(self, tmp_path):
        """Test deeply nested structure."""
        deep = tmp_path / "a" / "b" / "c" / "d"
        deep.mkdir(parents=True)
        (deep / "deep.txt").write_text("deep content")
        files = project_files(tmp_path)
        assert len(files) == 1
        assert Path("a/b/c/d/deep.txt") in files


class TestProjectFilesExcludesBehavior:
    """Tests for specific exclude behavior."""

    def test_exclude_without_trailing_slash(self, tmp_path):
        """Test exclude pattern without trailing slash."""
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("git")
        (tmp_path / "main.py").write_text("code")

        # Without trailing slash should still work
        files = project_files(tmp_path, excludes=[".git"])
        assert len(files) == 1
        assert Path("main.py") in files

    def test_nested_exclude_directory(self, tmp_path):
        """Test excluding nested directory."""
        nested = tmp_path / "src" / "node_modules"
        nested.mkdir(parents=True)
        (nested / "package.json").write_text("{}")
        (tmp_path / "src" / "main.py").write_text("code")

        files = project_files(tmp_path, excludes=["src/node_modules/"])
        assert len(files) == 1
        assert Path("src/main.py") in files
