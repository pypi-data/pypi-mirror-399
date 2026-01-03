"""Tests for Git checkpoint/rollback functionality."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime, timedelta
import subprocess


class TestGitCheckpoint:
    """Tests for GitCheckpoint class."""

    def test_checkpoint_creation(self, tmp_path):
        """Test creating a checkpoint."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        # Initialize a git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

        # Create initial commit
        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)
        tag_name = checkpoint.create_checkpoint("test checkpoint")

        assert tag_name is not None
        assert tag_name.startswith("paircoder-checkpoint-")
        assert tag_name in checkpoint.checkpoints

    def test_checkpoint_with_message(self, tmp_path):
        """Test checkpoint includes custom message."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)
        tag_name = checkpoint.create_checkpoint("before refactoring")

        # Verify tag exists with annotation
        result = subprocess.run(
            ["git", "tag", "-l", tag_name],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )
        assert tag_name in result.stdout

    def test_rollback_to_checkpoint(self, tmp_path):
        """Test rolling back to a checkpoint."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

        # Create initial state
        (tmp_path / "file.txt").write_text("original content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)
        tag_name = checkpoint.create_checkpoint("before changes")

        # Make changes
        (tmp_path / "file.txt").write_text("modified content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "modification"], cwd=tmp_path, capture_output=True)

        # Rollback
        checkpoint.rollback_to(tag_name)

        # Verify content is restored
        assert (tmp_path / "file.txt").read_text() == "original content"

    def test_rollback_preserves_uncommitted_in_stash(self, tmp_path):
        """Test that uncommitted changes are stashed before rollback."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

        (tmp_path / "file.txt").write_text("original")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)
        tag_name = checkpoint.create_checkpoint()

        # Make uncommitted changes
        (tmp_path / "file.txt").write_text("uncommitted changes")

        # Rollback should stash the uncommitted changes
        stash_info = checkpoint.rollback_to(tag_name, stash_uncommitted=True)

        # Verify original content restored
        assert (tmp_path / "file.txt").read_text() == "original"

        # Verify stash exists
        result = subprocess.run(
            ["git", "stash", "list"],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )
        assert "paircoder" in result.stdout.lower() or len(result.stdout) > 0

    def test_list_checkpoints(self, tmp_path):
        """Test listing available checkpoints."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)
        tag1 = checkpoint.create_checkpoint("first")
        tag2 = checkpoint.create_checkpoint("second")

        checkpoints = checkpoint.list_checkpoints()

        assert len(checkpoints) >= 2
        assert any(tag1 in cp["tag"] for cp in checkpoints)
        assert any(tag2 in cp["tag"] for cp in checkpoints)

    def test_preview_rollback(self, tmp_path):
        """Test preview mode shows what would be reverted."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

        (tmp_path / "file.txt").write_text("original")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)
        tag_name = checkpoint.create_checkpoint()

        # Make changes
        (tmp_path / "file.txt").write_text("modified")
        (tmp_path / "new_file.txt").write_text("new file")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "changes"], cwd=tmp_path, capture_output=True)

        # Preview should show what will be reverted
        preview = checkpoint.preview_rollback(tag_name)

        assert "file.txt" in preview["files_changed"]
        assert preview["commits_to_revert"] >= 1

    def test_rollback_last_checkpoint(self, tmp_path):
        """Test rollback to last checkpoint."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

        (tmp_path / "file.txt").write_text("v1")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "v1"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)
        checkpoint.create_checkpoint("first")

        (tmp_path / "file.txt").write_text("v2")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "v2"], cwd=tmp_path, capture_output=True)

        checkpoint.create_checkpoint("second")

        (tmp_path / "file.txt").write_text("v3")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "v3"], cwd=tmp_path, capture_output=True)

        # Rollback to last checkpoint (should be "second")
        checkpoint.rollback_to_last()

        assert (tmp_path / "file.txt").read_text() == "v2"


class TestCheckpointRetention:
    """Tests for checkpoint retention policy."""

    def test_cleanup_old_checkpoints(self, tmp_path):
        """Test cleaning up old checkpoints."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path, max_checkpoints=3)

        # Create 5 checkpoints
        for i in range(5):
            checkpoint.create_checkpoint(f"checkpoint {i}")
            # Small delay to ensure unique timestamps
            import time
            time.sleep(0.01)

        # Should only keep last 3
        checkpoint.cleanup_old_checkpoints()
        remaining = checkpoint.list_checkpoints()

        assert len(remaining) <= 3

    def test_max_checkpoints_setting(self, tmp_path):
        """Test configurable max checkpoints."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path, max_checkpoints=5)
        assert checkpoint.max_checkpoints == 5

    def test_auto_cleanup_on_create(self, tmp_path):
        """Test that cleanup runs automatically when creating new checkpoint."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path, max_checkpoints=2, auto_cleanup=True)

        for i in range(5):
            checkpoint.create_checkpoint(f"cp{i}")
            import time
            time.sleep(0.01)

        # Should automatically keep only max_checkpoints
        remaining = checkpoint.list_checkpoints()
        assert len(remaining) <= 2


class TestDirtyWorkingDirectory:
    """Tests for handling dirty working directory."""

    def test_checkpoint_with_staged_changes(self, tmp_path):
        """Test checkpoint creation with staged but uncommitted changes."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        # Stage changes but don't commit
        (tmp_path / "file.txt").write_text("staged changes")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)
        tag_name = checkpoint.create_checkpoint()

        # Should succeed even with staged changes
        assert tag_name is not None

    def test_checkpoint_with_unstaged_changes(self, tmp_path):
        """Test checkpoint creation with unstaged changes."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        # Unstaged changes
        (tmp_path / "file.txt").write_text("unstaged changes")

        checkpoint = GitCheckpoint(tmp_path)
        tag_name = checkpoint.create_checkpoint()

        # Should succeed even with unstaged changes
        assert tag_name is not None

    def test_is_dirty(self, tmp_path):
        """Test checking if working directory is dirty."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)
        assert checkpoint.is_dirty() is False

        (tmp_path / "file.txt").write_text("dirty")
        assert checkpoint.is_dirty() is True


class TestCheckpointInfo:
    """Tests for checkpoint metadata."""

    def test_checkpoint_has_timestamp(self, tmp_path):
        """Test checkpoint includes timestamp."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)
        tag_name = checkpoint.create_checkpoint()

        checkpoints = checkpoint.list_checkpoints()
        cp = next(c for c in checkpoints if c["tag"] == tag_name)

        assert "timestamp" in cp
        assert cp["timestamp"] is not None

    def test_checkpoint_has_commit_hash(self, tmp_path):
        """Test checkpoint includes commit hash."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)
        tag_name = checkpoint.create_checkpoint()

        checkpoints = checkpoint.list_checkpoints()
        cp = next(c for c in checkpoints if c["tag"] == tag_name)

        assert "commit" in cp
        assert len(cp["commit"]) >= 7  # Short hash at least


class TestCheckpointErrors:
    """Tests for error handling."""

    def test_rollback_nonexistent_checkpoint(self, tmp_path):
        """Test error when rolling back to nonexistent checkpoint."""
        from bpsai_pair.security.checkpoint import GitCheckpoint, CheckpointNotFoundError

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)

        with pytest.raises(CheckpointNotFoundError):
            checkpoint.rollback_to("nonexistent-checkpoint")

    def test_rollback_last_no_checkpoints(self, tmp_path):
        """Test error when rollback_to_last with no checkpoints."""
        from bpsai_pair.security.checkpoint import GitCheckpoint, NoCheckpointsError

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)

        with pytest.raises(NoCheckpointsError):
            checkpoint.rollback_to_last()

    def test_not_a_git_repo(self, tmp_path):
        """Test error when path is not a git repo."""
        from bpsai_pair.security.checkpoint import GitCheckpoint, NotAGitRepoError

        with pytest.raises(NotAGitRepoError):
            GitCheckpoint(tmp_path)


class TestCheckpointCLI:
    """Tests for CLI commands (unit tests with mocks)."""

    def test_cli_list_checkpoints(self):
        """Test CLI list checkpoints command."""
        from bpsai_pair.security.checkpoint import format_checkpoint_list

        checkpoints = [
            {"tag": "paircoder-checkpoint-123", "timestamp": "2024-01-01 12:00:00", "commit": "abc1234", "message": "test"},
            {"tag": "paircoder-checkpoint-456", "timestamp": "2024-01-01 13:00:00", "commit": "def5678", "message": "another"},
        ]

        output = format_checkpoint_list(checkpoints)

        assert "paircoder-checkpoint-123" in output
        assert "paircoder-checkpoint-456" in output
        assert "abc1234" in output

    def test_cli_preview_format(self):
        """Test CLI preview output format."""
        from bpsai_pair.security.checkpoint import format_rollback_preview

        preview = {
            "tag": "paircoder-checkpoint-123",
            "commits_to_revert": 3,
            "files_changed": ["file1.py", "file2.py"],
        }

        output = format_rollback_preview(preview)

        assert "3" in output  # commits to revert
        assert "file1.py" in output
        assert "file2.py" in output
