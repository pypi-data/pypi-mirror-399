"""Tests for automatic task assignment."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from bpsai_pair.planning.auto_assign import (
    get_next_pending_task,
    auto_assign_next,
    AutoAssigner,
)
from bpsai_pair.planning.models import Task, TaskStatus


class TestGetNextPendingTask:
    """Tests for get_next_pending_task function."""

    @patch("bpsai_pair.planning.auto_assign.TaskParser")
    def test_returns_none_when_no_tasks(self, mock_parser_class, tmp_path):
        """Test returns None when no pending tasks."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        mock_parser = MagicMock()
        mock_parser.parse_all.return_value = []
        mock_parser_class.return_value = mock_parser

        result = get_next_pending_task(paircoder_dir)
        assert result is None

    @patch("bpsai_pair.planning.auto_assign.TaskParser")
    def test_returns_highest_priority_task(self, mock_parser_class, tmp_path):
        """Test returns highest priority task first."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        # Create tasks with different priorities
        task_p2 = Task(id="TASK-001", title="P2 task", plan_id="plan-1", priority="P2", status=TaskStatus.PENDING)
        task_p0 = Task(id="TASK-002", title="P0 task", plan_id="plan-1", priority="P0", status=TaskStatus.PENDING)
        task_p1 = Task(id="TASK-003", title="P1 task", plan_id="plan-1", priority="P1", status=TaskStatus.PENDING)

        mock_parser = MagicMock()
        mock_parser.parse_all.return_value = [task_p2, task_p0, task_p1]
        mock_parser_class.return_value = mock_parser

        result = get_next_pending_task(paircoder_dir)
        assert result.id == "TASK-002"
        assert result.priority == "P0"

    @patch("bpsai_pair.planning.auto_assign.TaskParser")
    def test_ignores_in_progress_tasks(self, mock_parser_class, tmp_path):
        """Test ignores tasks that are already in progress."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        task_in_progress = Task(id="TASK-001", title="In progress", plan_id="plan-1", status=TaskStatus.IN_PROGRESS)
        task_pending = Task(id="TASK-002", title="Pending", plan_id="plan-1", status=TaskStatus.PENDING)

        mock_parser = MagicMock()
        mock_parser.parse_all.return_value = [task_in_progress, task_pending]
        mock_parser_class.return_value = mock_parser

        result = get_next_pending_task(paircoder_dir)
        assert result.id == "TASK-002"

    @patch("bpsai_pair.planning.auto_assign.TaskParser")
    def test_sorts_by_complexity_when_same_priority(self, mock_parser_class, tmp_path):
        """Test sorts by complexity when priorities are equal."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        task_high_complexity = Task(id="TASK-001", title="High", plan_id="plan-1", priority="P0", complexity=80, status=TaskStatus.PENDING)
        task_low_complexity = Task(id="TASK-002", title="Low", plan_id="plan-1", priority="P0", complexity=20, status=TaskStatus.PENDING)

        mock_parser = MagicMock()
        mock_parser.parse_all.return_value = [task_high_complexity, task_low_complexity]
        mock_parser_class.return_value = mock_parser

        result = get_next_pending_task(paircoder_dir)
        assert result.id == "TASK-002"
        assert result.complexity == 20


class TestAutoAssignNext:
    """Tests for auto_assign_next function."""

    @patch("bpsai_pair.planning.auto_assign.TaskParser")
    def test_assigns_task_to_in_progress(self, mock_parser_class, tmp_path):
        """Test assigns task and sets to in_progress."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        task = Task(id="TASK-001", title="Test", plan_id="plan-1", status=TaskStatus.PENDING)

        mock_parser = MagicMock()
        mock_parser.parse_all.return_value = [task]
        mock_parser_class.return_value = mock_parser

        result = auto_assign_next(paircoder_dir)

        assert result is not None
        assert result.status == TaskStatus.IN_PROGRESS
        mock_parser.save.assert_called_once()

    @patch("bpsai_pair.planning.auto_assign.TaskParser")
    def test_returns_none_when_no_tasks(self, mock_parser_class, tmp_path):
        """Test returns None when no pending tasks."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        mock_parser = MagicMock()
        mock_parser.parse_all.return_value = []
        mock_parser_class.return_value = mock_parser

        result = auto_assign_next(paircoder_dir)
        assert result is None

    @patch("bpsai_pair.planning.auto_assign.TaskParser")
    def test_calls_trello_callback(self, mock_parser_class, tmp_path):
        """Test calls Trello callback when provided."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        task = Task(id="TASK-001", title="Test", plan_id="plan-1", status=TaskStatus.PENDING)

        mock_parser = MagicMock()
        mock_parser.parse_all.return_value = [task]
        mock_parser_class.return_value = mock_parser

        callback = MagicMock()
        result = auto_assign_next(paircoder_dir, trello_callback=callback)

        callback.assert_called_once()


class TestAutoAssigner:
    """Tests for AutoAssigner class."""

    def test_init(self, tmp_path):
        """Test AutoAssigner initialization."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        assigner = AutoAssigner(paircoder_dir, enabled=True)
        assert assigner.enabled is True
        assert assigner.paircoder_dir == paircoder_dir

    @patch("bpsai_pair.planning.auto_assign.TaskParser")
    def test_disabled_returns_none(self, mock_parser_class, tmp_path):
        """Test disabled assigner returns None."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        assigner = AutoAssigner(paircoder_dir, enabled=False)
        result = assigner.assign_next()
        assert result is None

    @patch("bpsai_pair.planning.auto_assign.TaskParser")
    def test_get_next(self, mock_parser_class, tmp_path):
        """Test get_next finds pending task."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        task = Task(id="TASK-001", title="Test", plan_id="plan-1", status=TaskStatus.PENDING)

        mock_parser = MagicMock()
        mock_parser.parse_all.return_value = [task]
        mock_parser_class.return_value = mock_parser

        assigner = AutoAssigner(paircoder_dir, enabled=True)
        result = assigner.get_next()

        assert result is not None
        assert result.id == "TASK-001"
