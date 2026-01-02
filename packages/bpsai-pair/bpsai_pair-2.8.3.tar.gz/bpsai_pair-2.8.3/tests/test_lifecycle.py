"""Tests for task lifecycle management."""

import gzip
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from bpsai_pair.tasks.lifecycle import (
    TaskLifecycle,
    TaskMetadata,
    TaskState,
    TaskTransition,
    VALID_TRANSITIONS,
)
from bpsai_pair.tasks.archiver import (
    TaskArchiver,
    ArchivedTask,
    ArchiveManifest,
    ArchiveResult,
)
from bpsai_pair.tasks.changelog import (
    ChangelogGenerator,
    TAG_CATEGORY_MAP,
)


class TestTaskState:
    """Tests for TaskState enum."""

    def test_all_states_defined(self):
        """Verify all expected states exist."""
        assert TaskState.PENDING.value == "pending"
        assert TaskState.IN_PROGRESS.value == "in-progress"
        assert TaskState.REVIEW.value == "review"
        assert TaskState.COMPLETED.value == "completed"
        assert TaskState.BLOCKED.value == "blocked"
        assert TaskState.CANCELLED.value == "cancelled"
        assert TaskState.ARCHIVED.value == "archived"

    def test_valid_transitions(self):
        """Verify transition rules."""
        # Pending can go to in-progress or cancelled
        assert TaskState.IN_PROGRESS in VALID_TRANSITIONS[TaskState.PENDING]
        assert TaskState.CANCELLED in VALID_TRANSITIONS[TaskState.PENDING]

        # Completed can only go to archived
        assert TaskState.ARCHIVED in VALID_TRANSITIONS[TaskState.COMPLETED]
        assert len(VALID_TRANSITIONS[TaskState.COMPLETED]) == 1

        # Archived is terminal
        assert len(VALID_TRANSITIONS[TaskState.ARCHIVED]) == 0


class TestTaskLifecycle:
    """Tests for TaskLifecycle class."""

    def test_can_transition_valid(self):
        """Test valid transition check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lifecycle = TaskLifecycle(Path(tmpdir))

            assert lifecycle.can_transition(TaskState.PENDING, TaskState.IN_PROGRESS)
            assert lifecycle.can_transition(TaskState.COMPLETED, TaskState.ARCHIVED)

    def test_can_transition_invalid(self):
        """Test invalid transition check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lifecycle = TaskLifecycle(Path(tmpdir))

            assert not lifecycle.can_transition(TaskState.PENDING, TaskState.COMPLETED)
            assert not lifecycle.can_transition(TaskState.ARCHIVED, TaskState.PENDING)

    def test_transition_success(self):
        """Test successful state transition."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lifecycle = TaskLifecycle(Path(tmpdir))

            task = TaskMetadata(
                id="TASK-001",
                title="Test Task",
                status=TaskState.PENDING,
            )

            updated = lifecycle.transition(task, TaskState.IN_PROGRESS, "Starting work")

            assert updated.status == TaskState.IN_PROGRESS
            assert len(updated.transitions) == 1
            assert updated.transitions[0].from_state == TaskState.PENDING
            assert updated.transitions[0].to_state == TaskState.IN_PROGRESS
            assert updated.transitions[0].reason == "Starting work"

    def test_transition_to_completed_sets_timestamp(self):
        """Test that transitioning to completed sets completed_at."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lifecycle = TaskLifecycle(Path(tmpdir))

            task = TaskMetadata(
                id="TASK-001",
                title="Test Task",
                status=TaskState.IN_PROGRESS,
            )

            updated = lifecycle.transition(task, TaskState.COMPLETED)

            assert updated.completed_at is not None

    def test_transition_invalid_raises(self):
        """Test that invalid transition raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lifecycle = TaskLifecycle(Path(tmpdir))

            task = TaskMetadata(
                id="TASK-001",
                title="Test Task",
                status=TaskState.PENDING,
            )

            with pytest.raises(ValueError, match="Invalid transition"):
                lifecycle.transition(task, TaskState.COMPLETED)

    def test_load_task(self):
        """Test loading task from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tasks_dir = Path(tmpdir)
            lifecycle = TaskLifecycle(tasks_dir)

            # Create a task file
            task_file = tasks_dir / "TASK-001.task.md"
            task_file.write_text("""# TASK-001: Test Task

## Metadata
- **ID**: TASK-001
- **Plan**: test-plan
- **Sprint**: sprint-1
- **Priority**: P1
- **Complexity**: 50
- **Status**: done
- **Created**: 2025-01-15
- **Tags**: feature, infrastructure

## Description

This is a test task.
""")

            task = lifecycle.load_task(task_file)

            assert task.id == "TASK-001"
            assert task.status == TaskState.COMPLETED
            assert task.sprint == "sprint-1"
            assert task.priority == "P1"
            assert task.complexity == "50"  # String from parsing
            assert "feature" in task.tags


class TestTaskArchiver:
    """Tests for TaskArchiver class."""

    def test_archive_task_compressed(self):
        """Test archiving a task with compression."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paircoder_dir = root / ".paircoder"
            tasks_dir = paircoder_dir / "tasks" / "test-plan"
            tasks_dir.mkdir(parents=True)

            # Create task file
            task_file = tasks_dir / "TASK-001.task.md"
            task_content = "# TASK-001: Test Task\n\n## Description\nTest content."
            task_file.write_text(task_content)

            archiver = TaskArchiver(root, compress=True)

            task = TaskMetadata(
                id="TASK-001",
                title="Test Task",
                status=TaskState.COMPLETED,
                sprint="sprint-1",
            )

            archived = archiver.archive_task(task, "test-plan")

            # Original should be deleted
            assert not task_file.exists()

            # Archive should exist
            archive_path = paircoder_dir / "history" / "archived-tasks" / "test-plan" / "TASK-001.task.md.gz"
            assert archive_path.exists()

            # Verify content
            with gzip.open(archive_path, 'rt') as f:
                assert f.read() == task_content

            # Verify archived task record
            assert archived.id == "TASK-001"
            assert archived.title == "Test Task"

    def test_archive_batch(self):
        """Test batch archival."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paircoder_dir = root / ".paircoder"
            tasks_dir = paircoder_dir / "tasks" / "test-plan"
            tasks_dir.mkdir(parents=True)

            # Create multiple task files
            for i in range(3):
                task_file = tasks_dir / f"TASK-00{i+1}.task.md"
                task_file.write_text(f"# TASK-00{i+1}: Task {i+1}")

            archiver = TaskArchiver(root)

            tasks = [
                TaskMetadata(id="TASK-001", title="Task 1", status=TaskState.COMPLETED),
                TaskMetadata(id="TASK-002", title="Task 2", status=TaskState.COMPLETED),
                TaskMetadata(id="TASK-003", title="Task 3", status=TaskState.PENDING),  # Should be skipped
            ]

            result = archiver.archive_batch(tasks, "test-plan", "v1.0.0")

            assert len(result.archived) == 2
            assert len(result.skipped) == 1
            assert "TASK-003" in result.skipped[0]

    def test_manifest_created(self):
        """Test that manifest is created on archive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paircoder_dir = root / ".paircoder"
            tasks_dir = paircoder_dir / "tasks" / "test-plan"
            tasks_dir.mkdir(parents=True)

            task_file = tasks_dir / "TASK-001.task.md"
            task_file.write_text("# TASK-001: Test")

            archiver = TaskArchiver(root)

            task = TaskMetadata(
                id="TASK-001",
                title="Test Task",
                status=TaskState.COMPLETED,
            )

            archiver.archive_task(task, "test-plan")

            manifest_path = paircoder_dir / "history" / "archived-tasks" / "test-plan" / "manifest.json"
            assert manifest_path.exists()

            with open(manifest_path) as f:
                data = json.load(f)

            assert data["plan"] == "test-plan"
            assert len(data["tasks"]) == 1
            assert data["tasks"][0]["id"] == "TASK-001"

    def test_restore_task(self):
        """Test restoring a task from archive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paircoder_dir = root / ".paircoder"
            tasks_dir = paircoder_dir / "tasks" / "test-plan"
            tasks_dir.mkdir(parents=True)

            # Create and archive task
            task_file = tasks_dir / "TASK-001.task.md"
            task_content = "# TASK-001: Test Task"
            task_file.write_text(task_content)

            archiver = TaskArchiver(root)
            task = TaskMetadata(id="TASK-001", title="Test", status=TaskState.COMPLETED)
            archiver.archive_task(task, "test-plan")

            assert not task_file.exists()

            # Restore
            restored_path = archiver.restore_task("TASK-001", "test-plan")

            assert restored_path.exists()
            assert restored_path.read_text() == task_content

    def test_list_archived(self):
        """Test listing archived tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paircoder_dir = root / ".paircoder"
            tasks_dir = paircoder_dir / "tasks" / "test-plan"
            tasks_dir.mkdir(parents=True)

            # Create and archive tasks
            for i in range(2):
                task_file = tasks_dir / f"TASK-00{i+1}.task.md"
                task_file.write_text(f"# TASK-00{i+1}")

            archiver = TaskArchiver(root)
            for i in range(2):
                task = TaskMetadata(
                    id=f"TASK-00{i+1}",
                    title=f"Task {i+1}",
                    status=TaskState.COMPLETED,
                )
                archiver.archive_task(task, "test-plan")

            archived = archiver.list_archived("test-plan")

            assert len(archived) == 2
            ids = [t.id for t in archived]
            assert "TASK-001" in ids
            assert "TASK-002" in ids


class TestChangelogGenerator:
    """Tests for ChangelogGenerator class."""

    def test_generate_entry(self):
        """Test generating changelog entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            changelog_path = Path(tmpdir) / "CHANGELOG.md"
            generator = ChangelogGenerator(changelog_path)

            tasks = [
                ArchivedTask(
                    id="TASK-001",
                    title="Add new feature",
                    sprint="sprint-1",
                    status="completed",
                    completed_at=None,
                    archived_at="2025-01-15",
                    tags=["feature"],
                ),
                ArchivedTask(
                    id="TASK-002",
                    title="Fix bug",
                    sprint="sprint-1",
                    status="completed",
                    completed_at=None,
                    archived_at="2025-01-15",
                    tags=["bugfix"],
                ),
            ]

            entry = generator.generate_entry(tasks, "v1.0.0")

            assert "## [v1.0.0]" in entry
            assert "### Added" in entry
            assert "### Fixed" in entry
            assert "TASK-001" in entry
            assert "TASK-002" in entry

    def test_categorize_by_tags(self):
        """Test task categorization by tags."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ChangelogGenerator(Path(tmpdir) / "CHANGELOG.md")

            tasks = [
                ArchivedTask(id="T1", title="A", sprint=None, status="done",
                            completed_at=None, archived_at="", tags=["feature"]),
                ArchivedTask(id="T2", title="B", sprint=None, status="done",
                            completed_at=None, archived_at="", tags=["enhancement"]),
                ArchivedTask(id="T3", title="C", sprint=None, status="done",
                            completed_at=None, archived_at="", tags=["fix"]),
                ArchivedTask(id="T4", title="D", sprint=None, status="done",
                            completed_at=None, archived_at="", tags=["docs"]),
            ]

            categorized = generator._categorize_tasks(tasks)

            assert "Added" in categorized
            assert "Changed" in categorized
            assert "Fixed" in categorized
            assert "Documentation" in categorized

    def test_update_changelog(self):
        """Test updating existing changelog."""
        with tempfile.TemporaryDirectory() as tmpdir:
            changelog_path = Path(tmpdir) / "CHANGELOG.md"

            # Create existing changelog
            changelog_path.write_text("# Changelog\n\n## [v0.9.0] - 2025-01-01\n\n### Added\n- Initial release\n")

            generator = ChangelogGenerator(changelog_path)

            tasks = [
                ArchivedTask(
                    id="TASK-001",
                    title="New feature",
                    sprint=None,
                    status="done",
                    completed_at=None,
                    archived_at="",
                    tags=["feature"],
                ),
            ]

            generator.update_changelog(tasks, "v1.0.0")

            content = changelog_path.read_text()

            # New version should be at top
            assert content.index("[v1.0.0]") < content.index("[v0.9.0]")

    def test_increment_version(self):
        """Test version incrementing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ChangelogGenerator(Path(tmpdir) / "CHANGELOG.md")

            assert generator.increment_version("v1.2.3", "patch") == "v1.2.4"
            assert generator.increment_version("v1.2.3", "minor") == "v1.3.0"
            assert generator.increment_version("v1.2.3", "major") == "v2.0.0"
            assert generator.increment_version("1.2.3", "patch") == "1.2.4"

    def test_custom_changelog_entry(self):
        """Test using custom changelog_entry field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ChangelogGenerator(Path(tmpdir) / "CHANGELOG.md")

            tasks = [
                ArchivedTask(
                    id="TASK-001",
                    title="Technical task title",
                    sprint=None,
                    status="done",
                    completed_at=None,
                    archived_at="",
                    tags=["feature"],
                    changelog_entry="User-friendly description of the feature",
                ),
            ]

            entry = generator.generate_entry(tasks, "v1.0.0")

            assert "User-friendly description" in entry
            assert "Technical task title" not in entry
