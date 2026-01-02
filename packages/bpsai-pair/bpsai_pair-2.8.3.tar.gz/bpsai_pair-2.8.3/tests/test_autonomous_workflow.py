"""Tests for autonomous workflow orchestration."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from bpsai_pair.orchestration.autonomous import (
    WorkflowPhase,
    WorkflowEvent,
    WorkflowState,
    WorkflowConfig,
    AutonomousWorkflow,
    WorkflowSequencer,
)


class TestWorkflowState:
    """Tests for WorkflowState."""

    def test_initial_state(self):
        """Test initial state values."""
        state = WorkflowState()
        assert state.phase == WorkflowPhase.IDLE
        assert state.current_task_id is None
        assert state.events == []

    def test_record_event(self):
        """Test recording an event."""
        state = WorkflowState()
        state.record_event(WorkflowEvent.TASK_SELECTED, {"task_id": "TASK-001"})

        assert len(state.events) == 1
        assert state.events[0]["event"] == "task_selected"
        assert state.events[0]["data"]["task_id"] == "TASK-001"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        state = WorkflowState()
        state.phase = WorkflowPhase.IMPLEMENTING
        state.current_task_id = "TASK-001"

        result = state.to_dict()

        assert result["phase"] == "implementing"
        assert result["current_task_id"] == "TASK-001"


class TestWorkflowConfig:
    """Tests for WorkflowConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = WorkflowConfig()

        assert config.auto_select_tasks is True
        assert config.auto_create_pr is True
        assert config.max_tasks_per_session == 5

    def test_custom_values(self):
        """Test custom configuration values."""
        config = WorkflowConfig(
            auto_select_tasks=False,
            max_tasks_per_session=10,
        )

        assert config.auto_select_tasks is False
        assert config.max_tasks_per_session == 10

    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "auto_create_pr": False,
            "run_tests_before_pr": False,
        }

        config = WorkflowConfig.from_dict(data)

        assert config.auto_create_pr is False
        assert config.run_tests_before_pr is False


class TestAutonomousWorkflow:
    """Tests for AutonomousWorkflow."""

    @pytest.fixture
    def workflow(self, tmp_path):
        """Create a workflow instance for testing."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()
        return AutonomousWorkflow(paircoder_dir)

    def test_initial_state(self, workflow):
        """Test workflow initializes with correct state."""
        assert workflow.state.phase == WorkflowPhase.IDLE
        assert workflow.state.current_task_id is None

    @patch("bpsai_pair.planning.auto_assign.get_next_pending_task")
    def test_select_next_task(self, mock_get_next, workflow):
        """Test task selection."""
        mock_task = MagicMock()
        mock_task.id = "TASK-001"
        mock_task.title = "Test Task"
        mock_task.plan_id = "plan-test"
        mock_task.priority = "P0"
        mock_get_next.return_value = mock_task

        result = workflow.select_next_task()

        assert result == "TASK-001"
        assert workflow.state.current_task_id == "TASK-001"
        assert workflow.state.phase == WorkflowPhase.SELECTING_TASK

    @patch("bpsai_pair.planning.auto_assign.get_next_pending_task")
    def test_select_next_task_none_available(self, mock_get_next, workflow):
        """Test task selection when no tasks available."""
        mock_get_next.return_value = None

        result = workflow.select_next_task()

        assert result is None
        assert workflow.state.phase == WorkflowPhase.IDLE

    def test_start_planning(self, workflow):
        """Test planning phase start."""
        workflow.state.current_task_id = "TASK-001"

        # Mock task parser
        mock_task = MagicMock()
        mock_task.title = "Build a new feature"
        workflow._task_parser = MagicMock()
        workflow._task_parser.get_task_by_id.return_value = mock_task

        flow = workflow.start_planning()

        assert workflow.state.phase == WorkflowPhase.PLANNING
        assert flow is not None  # Some flow should be suggested

    def test_start_implementation(self, workflow):
        """Test implementation phase start."""
        workflow.state.current_task_id = "TASK-001"

        mock_task = MagicMock()
        workflow._task_parser = MagicMock()
        workflow._task_parser.get_task_by_id.return_value = mock_task

        result = workflow.start_implementation()

        assert result is True
        assert workflow.state.phase == WorkflowPhase.IMPLEMENTING

    def test_complete_task(self, workflow):
        """Test task completion."""
        workflow.state.current_task_id = "TASK-001"

        mock_task = MagicMock()
        workflow._task_parser = MagicMock()
        workflow._task_parser.get_task_by_id.return_value = mock_task

        result = workflow.complete_task()

        assert result is True
        assert workflow.state.current_task_id is None
        assert workflow.state.phase == WorkflowPhase.IDLE

    def test_get_status(self, workflow):
        """Test getting workflow status."""
        workflow.state.current_task_id = "TASK-001"
        workflow.state.phase = WorkflowPhase.IMPLEMENTING

        status = workflow.get_status()

        assert "workflow_state" in status
        assert "config" in status
        assert status["workflow_state"]["current_task_id"] == "TASK-001"

    def test_hooks_called(self, workflow):
        """Test that hooks are called."""
        called = []
        workflow.hooks["on_task_selected"] = lambda t: called.append("selected")

        mock_task = MagicMock()
        mock_task.id = "TASK-001"
        mock_task.title = "Test"
        mock_task.plan_id = "plan"
        mock_task.priority = "P0"

        with patch("bpsai_pair.planning.auto_assign.get_next_pending_task", return_value=mock_task):
            workflow.select_next_task()

        assert "selected" in called


class TestWorkflowSequencer:
    """Tests for WorkflowSequencer."""

    @pytest.fixture
    def sequencer(self, tmp_path):
        """Create a sequencer instance for testing."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()
        workflow = AutonomousWorkflow(paircoder_dir)
        return WorkflowSequencer(workflow)

    def test_phase_sequence(self, sequencer):
        """Test phase sequence is defined."""
        assert len(sequencer.PHASE_SEQUENCE) > 0
        assert WorkflowPhase.SELECTING_TASK in sequencer.PHASE_SEQUENCE
        assert WorkflowPhase.COMPLETING in sequencer.PHASE_SEQUENCE

    def test_current_phase(self, sequencer):
        """Test getting current phase."""
        assert sequencer.current_phase == WorkflowPhase.IDLE

    def test_next_phase_from_idle(self, sequencer):
        """Test next phase determination."""
        # When idle, next phase should be selecting_task
        sequencer.workflow.state.phase = WorkflowPhase.SELECTING_TASK
        assert sequencer.next_phase == WorkflowPhase.PLANNING


class TestWorkflowPhase:
    """Tests for WorkflowPhase enum."""

    def test_all_phases_defined(self):
        """Test all expected phases exist."""
        expected = ["IDLE", "SELECTING_TASK", "PLANNING", "IMPLEMENTING",
                    "TESTING", "REVIEWING", "CREATING_PR", "COMPLETING", "ERROR"]
        for phase in expected:
            assert hasattr(WorkflowPhase, phase)


class TestWorkflowEvent:
    """Tests for WorkflowEvent enum."""

    def test_all_events_defined(self):
        """Test all expected events exist."""
        expected = ["TASK_SELECTED", "PLANNING_STARTED", "PLANNING_COMPLETED",
                    "IMPLEMENTATION_STARTED", "IMPLEMENTATION_COMPLETED",
                    "TESTS_PASSED", "TESTS_FAILED", "PR_CREATED", "TASK_COMPLETED"]
        for event in expected:
            assert hasattr(WorkflowEvent, event)
