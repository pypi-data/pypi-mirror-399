"""Git checkpoint and rollback functionality.

This module provides:
- GitCheckpoint: Create and manage checkpoints
- Rollback: Restore to previous states
- Retention: Automatic cleanup of old checkpoints
"""

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


class CheckpointError(Exception):
    """Base exception for checkpoint errors."""
    pass


class NotAGitRepoError(CheckpointError):
    """Raised when path is not a git repository."""
    pass


class CheckpointNotFoundError(CheckpointError):
    """Raised when checkpoint tag doesn't exist."""
    pass


class NoCheckpointsError(CheckpointError):
    """Raised when no checkpoints exist."""
    pass


CHECKPOINT_PREFIX = "paircoder-checkpoint-"


@dataclass
class CheckpointInfo:
    """Information about a checkpoint."""
    tag: str
    commit: str
    timestamp: str
    message: str = ""


class GitCheckpoint:
    """Manages git checkpoints for rollback capability.

    Attributes:
        repo_path: Path to the git repository
        max_checkpoints: Maximum checkpoints to retain
        auto_cleanup: Whether to auto-cleanup on create
        checkpoints: List of checkpoint tags created in this session
    """

    def __init__(
        self,
        repo_path: Path,
        max_checkpoints: int = 10,
        auto_cleanup: bool = False
    ):
        """Initialize GitCheckpoint.

        Args:
            repo_path: Path to git repository
            max_checkpoints: Maximum checkpoints to keep
            auto_cleanup: Auto-cleanup old checkpoints on create

        Raises:
            NotAGitRepoError: If path is not a git repository
        """
        self.repo_path = Path(repo_path)
        self.max_checkpoints = max_checkpoints
        self.auto_cleanup = auto_cleanup
        self.checkpoints: list[str] = []

        # Verify it's a git repo
        if not self._is_git_repo():
            raise NotAGitRepoError(f"{repo_path} is not a git repository")

    def _run_git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command.

        Args:
            *args: Git command arguments
            check: Whether to raise on non-zero exit

        Returns:
            CompletedProcess result
        """
        return subprocess.run(
            ["git"] + list(args),
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=check
        )

    def _is_git_repo(self) -> bool:
        """Check if path is a git repository."""
        result = self._run_git("rev-parse", "--git-dir", check=False)
        return result.returncode == 0

    def _get_current_commit(self) -> str:
        """Get current HEAD commit hash."""
        result = self._run_git("rev-parse", "HEAD")
        return result.stdout.strip()

    def _generate_tag_name(self) -> str:
        """Generate unique checkpoint tag name."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        return f"{CHECKPOINT_PREFIX}{timestamp}"

    def is_dirty(self) -> bool:
        """Check if working directory has uncommitted changes.

        Returns:
            True if there are staged or unstaged changes
        """
        # Check for any changes (staged or unstaged)
        result = self._run_git("status", "--porcelain")
        return len(result.stdout.strip()) > 0

    def create_checkpoint(self, message: str = "") -> str:
        """Create a checkpoint at current HEAD.

        Args:
            message: Optional message describing the checkpoint

        Returns:
            Tag name of the created checkpoint
        """
        tag_name = self._generate_tag_name()
        commit = self._get_current_commit()

        # Create lightweight tag
        tag_message = message or f"Checkpoint at {datetime.now().isoformat()}"
        self._run_git("tag", "-a", tag_name, "-m", tag_message)

        self.checkpoints.append(tag_name)

        # Auto-cleanup if enabled
        if self.auto_cleanup:
            self.cleanup_old_checkpoints()

        return tag_name

    def rollback_to(
        self,
        checkpoint: str,
        stash_uncommitted: bool = True
    ) -> Optional[str]:
        """Rollback to a checkpoint.

        Args:
            checkpoint: Tag name of checkpoint to rollback to
            stash_uncommitted: Whether to stash uncommitted changes

        Returns:
            Stash reference if changes were stashed, None otherwise

        Raises:
            CheckpointNotFoundError: If checkpoint doesn't exist
        """
        # Verify checkpoint exists
        result = self._run_git("tag", "-l", checkpoint, check=False)
        if checkpoint not in result.stdout:
            raise CheckpointNotFoundError(f"Checkpoint '{checkpoint}' not found")

        stash_ref = None

        # Stash uncommitted changes if requested and dirty
        if stash_uncommitted and self.is_dirty():
            stash_message = f"paircoder-rollback-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            self._run_git("stash", "push", "-m", stash_message)
            stash_ref = stash_message

        # Reset to checkpoint
        self._run_git("reset", "--hard", checkpoint)

        return stash_ref

    def rollback_to_last(self, stash_uncommitted: bool = True) -> Optional[str]:
        """Rollback to the most recent checkpoint.

        Args:
            stash_uncommitted: Whether to stash uncommitted changes

        Returns:
            Stash reference if changes were stashed

        Raises:
            NoCheckpointsError: If no checkpoints exist
        """
        checkpoints = self.list_checkpoints()
        if not checkpoints:
            raise NoCheckpointsError("No checkpoints available")

        # Get the most recent checkpoint (sorted by timestamp)
        latest = sorted(checkpoints, key=lambda c: c["timestamp"], reverse=True)[0]
        return self.rollback_to(latest["tag"], stash_uncommitted)

    def list_checkpoints(self) -> list[dict]:
        """List all paircoder checkpoints.

        Returns:
            List of checkpoint info dicts with tag, commit, timestamp, message
        """
        # Get all paircoder checkpoint tags
        result = self._run_git("tag", "-l", f"{CHECKPOINT_PREFIX}*")
        tags = result.stdout.strip().split("\n")
        tags = [t for t in tags if t]  # Filter empty

        checkpoints = []
        for tag in tags:
            # Get tag info
            try:
                # Get commit hash
                commit_result = self._run_git("rev-list", "-n", "1", tag)
                commit = commit_result.stdout.strip()[:7]

                # Get tag message
                msg_result = self._run_git("tag", "-l", "-n1", tag)
                # Format: "tag_name    message"
                parts = msg_result.stdout.strip().split(None, 1)
                message = parts[1] if len(parts) > 1 else ""

                # Parse timestamp from tag name
                timestamp_part = tag.replace(CHECKPOINT_PREFIX, "")
                try:
                    # Parse YYYYMMDD-HHMMSS-ffffff format (with microseconds)
                    dt = datetime.strptime(timestamp_part, "%Y%m%d-%H%M%S-%f")
                    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    try:
                        # Fallback to without microseconds
                        dt = datetime.strptime(timestamp_part[:15], "%Y%m%d-%H%M%S")
                        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        timestamp = timestamp_part

                checkpoints.append({
                    "tag": tag,
                    "commit": commit,
                    "timestamp": timestamp,
                    "message": message
                })
            except subprocess.CalledProcessError:
                continue

        return checkpoints

    def preview_rollback(self, checkpoint: str) -> dict:
        """Preview what would be reverted by rolling back.

        Args:
            checkpoint: Tag name of checkpoint

        Returns:
            Dict with files_changed, commits_to_revert

        Raises:
            CheckpointNotFoundError: If checkpoint doesn't exist
        """
        # Verify checkpoint exists
        result = self._run_git("tag", "-l", checkpoint, check=False)
        if checkpoint not in result.stdout:
            raise CheckpointNotFoundError(f"Checkpoint '{checkpoint}' not found")

        # Get files changed between checkpoint and HEAD
        diff_result = self._run_git(
            "diff", "--name-only", checkpoint, "HEAD",
            check=False
        )
        files = [f for f in diff_result.stdout.strip().split("\n") if f]

        # Get number of commits between checkpoint and HEAD
        log_result = self._run_git(
            "rev-list", "--count", f"{checkpoint}..HEAD",
            check=False
        )
        try:
            commits = int(log_result.stdout.strip())
        except ValueError:
            commits = 0

        return {
            "tag": checkpoint,
            "files_changed": files,
            "commits_to_revert": commits
        }

    def cleanup_old_checkpoints(self) -> list[str]:
        """Remove old checkpoints beyond max_checkpoints.

        Returns:
            List of removed tag names
        """
        checkpoints = self.list_checkpoints()

        if len(checkpoints) <= self.max_checkpoints:
            return []

        # Sort by timestamp (oldest first)
        sorted_checkpoints = sorted(checkpoints, key=lambda c: c["timestamp"])

        # Remove oldest until we're at max
        to_remove = sorted_checkpoints[:-self.max_checkpoints]
        removed = []

        for cp in to_remove:
            try:
                self._run_git("tag", "-d", cp["tag"])
                removed.append(cp["tag"])
            except subprocess.CalledProcessError:
                pass

        return removed

    def delete_checkpoint(self, checkpoint: str) -> None:
        """Delete a specific checkpoint.

        Args:
            checkpoint: Tag name to delete

        Raises:
            CheckpointNotFoundError: If checkpoint doesn't exist
        """
        result = self._run_git("tag", "-l", checkpoint, check=False)
        if checkpoint not in result.stdout:
            raise CheckpointNotFoundError(f"Checkpoint '{checkpoint}' not found")

        self._run_git("tag", "-d", checkpoint)


def format_checkpoint_list(checkpoints: list[dict]) -> str:
    """Format checkpoint list for CLI display.

    Args:
        checkpoints: List of checkpoint info dicts

    Returns:
        Formatted string for display
    """
    if not checkpoints:
        return "No checkpoints found."

    lines = ["Checkpoints:", ""]
    for cp in sorted(checkpoints, key=lambda c: c["timestamp"], reverse=True):
        lines.append(f"  {cp['tag']}")
        lines.append(f"    Commit:  {cp['commit']}")
        lines.append(f"    Time:    {cp['timestamp']}")
        if cp.get("message"):
            lines.append(f"    Message: {cp['message']}")
        lines.append("")

    return "\n".join(lines)


def format_rollback_preview(preview: dict) -> str:
    """Format rollback preview for CLI display.

    Args:
        preview: Preview dict from preview_rollback()

    Returns:
        Formatted string for display
    """
    lines = [
        f"Rollback Preview: {preview['tag']}",
        "",
        f"Commits to revert: {preview['commits_to_revert']}",
        "",
        "Files that will be changed:"
    ]

    for f in preview["files_changed"]:
        lines.append(f"  - {f}")

    if not preview["files_changed"]:
        lines.append("  (no files changed)")

    return "\n".join(lines)
