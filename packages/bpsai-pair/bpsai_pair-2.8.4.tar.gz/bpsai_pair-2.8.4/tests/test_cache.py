"""Tests for context caching."""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta

from bpsai_pair.context.cache import ContextCache, CacheEntry
from bpsai_pair.context.loader import ContextLoader


class TestContextCache:
    """Tests for ContextCache class."""

    def test_cache_set_and_get(self, tmp_path: Path):
        """Test basic set and get operations."""
        cache = ContextCache(tmp_path / "cache")
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test Content")

        # Set cache
        entry = cache.set(test_file, "# Test Content")
        assert entry.path == str(test_file)
        assert entry.size_bytes == 14

        # Get cache
        result = cache.get(test_file)
        assert result is not None
        content, cached_entry = result
        assert content == "# Test Content"
        assert cached_entry.content_hash == entry.content_hash

    def test_cache_miss_on_nonexistent(self, tmp_path: Path):
        """Test cache miss for uncached file."""
        cache = ContextCache(tmp_path / "cache")
        test_file = tmp_path / "missing.md"

        result = cache.get(test_file)
        assert result is None

    def test_cache_invalidation_on_mtime(self, tmp_path: Path):
        """Test cache invalidation when file changes."""
        cache = ContextCache(tmp_path / "cache")
        test_file = tmp_path / "test.md"
        test_file.write_text("# Original")

        # Cache original
        cache.set(test_file, "# Original")

        # Modify file (simulate time passing)
        import time
        time.sleep(0.1)
        test_file.write_text("# Modified")

        # Should be cache miss
        result = cache.get(test_file)
        assert result is None

    def test_cache_invalidate(self, tmp_path: Path):
        """Test manual cache invalidation."""
        cache = ContextCache(tmp_path / "cache")
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        cache.set(test_file, "# Test")
        assert cache.get(test_file) is not None

        result = cache.invalidate(test_file)
        assert result is True
        assert cache.get(test_file) is None

    def test_cache_clear(self, tmp_path: Path):
        """Test clearing entire cache."""
        cache = ContextCache(tmp_path / "cache")

        # Add multiple entries
        for i in range(3):
            f = tmp_path / f"file{i}.md"
            f.write_text(f"Content {i}")
            cache.set(f, f"Content {i}")

        assert cache.stats()["entries"] == 3

        count = cache.clear()
        assert count == 3
        assert cache.stats()["entries"] == 0

    def test_cache_stats(self, tmp_path: Path):
        """Test cache statistics."""
        cache = ContextCache(tmp_path / "cache")

        # Empty stats
        stats = cache.stats()
        assert stats["entries"] == 0
        assert stats["total_bytes"] == 0

        # Add entries
        f1 = tmp_path / "file1.md"
        f1.write_text("Short")
        cache.set(f1, "Short")

        f2 = tmp_path / "file2.md"
        f2.write_text("Longer content here")
        cache.set(f2, "Longer content here")

        stats = cache.stats()
        assert stats["entries"] == 2
        assert stats["total_bytes"] == 5 + 19

    def test_cache_key_uniqueness(self, tmp_path: Path):
        """Test cache keys are unique for different paths."""
        cache = ContextCache(tmp_path / "cache")

        f1 = tmp_path / "dir1" / "file.md"
        f2 = tmp_path / "dir2" / "file.md"
        f1.parent.mkdir()
        f2.parent.mkdir()
        f1.write_text("Content 1")
        f2.write_text("Content 2")

        cache.set(f1, "Content 1")
        cache.set(f2, "Content 2")

        r1 = cache.get(f1)
        r2 = cache.get(f2)

        assert r1 is not None
        assert r2 is not None
        assert r1[0] == "Content 1"
        assert r2[0] == "Content 2"

    def test_cache_persistence(self, tmp_path: Path):
        """Test cache persists across instances."""
        cache_dir = tmp_path / "cache"
        test_file = tmp_path / "test.md"
        test_file.write_text("# Persistent")

        # First instance sets cache
        cache1 = ContextCache(cache_dir)
        cache1.set(test_file, "# Persistent")

        # Second instance should find it
        cache2 = ContextCache(cache_dir)
        result = cache2.get(test_file)
        assert result is not None
        assert result[0] == "# Persistent"


class TestContextLoader:
    """Tests for ContextLoader class."""

    def test_load_cacheable_file(self, tmp_path: Path):
        """Test loading a cacheable file."""
        # Create project structure
        context_dir = tmp_path / ".paircoder" / "context"
        context_dir.mkdir(parents=True)
        project_md = context_dir / "project.md"
        project_md.write_text("# Project Overview")

        loader = ContextLoader(tmp_path)

        # First load - cache miss
        content = loader.load(".paircoder/context/project.md")
        assert content == "# Project Overview"
        assert loader.misses == 1
        assert loader.hits == 0

        # Second load - cache hit
        content = loader.load(".paircoder/context/project.md")
        assert content == "# Project Overview"
        assert loader.misses == 1
        assert loader.hits == 1

    def test_load_non_cacheable_file(self, tmp_path: Path):
        """Test loading a non-cacheable file."""
        context_dir = tmp_path / ".paircoder" / "context"
        context_dir.mkdir(parents=True)
        state_md = context_dir / "state.md"
        state_md.write_text("# Current State")

        loader = ContextLoader(tmp_path)

        # Should not be cached (state.md is dynamic)
        content = loader.load(".paircoder/context/state.md")
        assert content == "# Current State"

        # No cache tracking for non-cacheable
        assert loader.hits == 0
        assert loader.misses == 0

    def test_load_missing_file(self, tmp_path: Path):
        """Test loading a missing file raises error."""
        loader = ContextLoader(tmp_path)

        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent.md")

    def test_load_all_context(self, tmp_path: Path):
        """Test loading all context files."""
        # Create minimal structure
        context_dir = tmp_path / ".paircoder" / "context"
        context_dir.mkdir(parents=True)

        (context_dir / "project.md").write_text("# Project")
        (context_dir / "workflow.md").write_text("# Workflow")

        (tmp_path / "AGENTS.md").write_text("# Agents")

        loader = ContextLoader(tmp_path)
        context = loader.load_all_context()

        assert ".paircoder/context/project.md" in context
        assert ".paircoder/context/workflow.md" in context
        assert "AGENTS.md" in context

    def test_get_stats(self, tmp_path: Path):
        """Test getting loader statistics."""
        context_dir = tmp_path / ".paircoder" / "context"
        context_dir.mkdir(parents=True)
        (context_dir / "project.md").write_text("# Test")

        loader = ContextLoader(tmp_path)

        # Initial stats
        stats = loader.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0

        # After loads
        loader.load(".paircoder/context/project.md")
        loader.load(".paircoder/context/project.md")

        stats = loader.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_reset_stats(self, tmp_path: Path):
        """Test resetting loader statistics."""
        context_dir = tmp_path / ".paircoder" / "context"
        context_dir.mkdir(parents=True)
        (context_dir / "project.md").write_text("# Test")

        loader = ContextLoader(tmp_path)
        loader.load(".paircoder/context/project.md")
        loader.load(".paircoder/context/project.md")

        loader.reset_stats()

        assert loader.hits == 0
        assert loader.misses == 0
