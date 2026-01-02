"""
Tests for MCP Planning Tools

Tests the planning management MCP tools:
- paircoder_plan_status
- paircoder_plan_list
- Helper functions
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch
import os


class TestFindPaircoderDir:
    """Tests for find_paircoder_dir helper."""

    def test_raises_when_not_found(self, tmp_path):
        """find_paircoder_dir raises FileNotFoundError when no .paircoder exists."""
        from bpsai_pair.mcp.tools.planning import find_paircoder_dir

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(FileNotFoundError):
                find_paircoder_dir()
        finally:
            os.chdir(original_cwd)

    def test_finds_directory_in_current(self, tmp_path):
        """find_paircoder_dir finds .paircoder in current directory."""
        from bpsai_pair.mcp.tools.planning import find_paircoder_dir

        (tmp_path / ".paircoder").mkdir()

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = find_paircoder_dir()
            assert result.name == ".paircoder"
        finally:
            os.chdir(original_cwd)

    def test_finds_directory_in_parent(self, tmp_path):
        """find_paircoder_dir finds .paircoder in parent directory."""
        from bpsai_pair.mcp.tools.planning import find_paircoder_dir

        (tmp_path / ".paircoder").mkdir()
        subdir = tmp_path / "subdir" / "deep"
        subdir.mkdir(parents=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(subdir)
            result = find_paircoder_dir()
            assert result.name == ".paircoder"
            assert result.parent == tmp_path
        finally:
            os.chdir(original_cwd)


class TestPlanStatus:
    """Tests for paircoder_plan_status tool."""

    @pytest.fixture
    def mock_server(self):
        """Create a mock MCP server that captures registered tools."""
        server = MagicMock()
        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        server.tool = tool_decorator
        server._registered_tools = registered_tools
        return server

    @pytest.fixture
    def setup_paircoder_dir(self, tmp_path):
        """Set up a .paircoder directory structure."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "plans").mkdir()
        (paircoder_dir / "tasks").mkdir()
        (paircoder_dir / "context").mkdir()
        return paircoder_dir

    def test_no_paircoder_dir_returns_error(self, mock_server, tmp_path):
        """Returns error when no .paircoder directory found."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = asyncio.run(plan_status(plan_id="PLAN-001"))

            assert "error" in result
            assert result["error"]["code"] == "NOT_FOUND"
        finally:
            os.chdir(original_cwd)

    def test_plan_not_found_returns_error(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns error when specified plan is not found."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager"):
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    with patch("bpsai_pair.mcp.tools.planning.TaskParser"):
                        mock_plan_parser.return_value.get_plan_by_id.return_value = None

                        result = asyncio.run(plan_status(plan_id="NONEXISTENT"))

                        assert "error" in result
                        assert result["error"]["code"] == "PLAN_NOT_FOUND"
                        assert "NONEXISTENT" in result["error"]["message"]
        finally:
            os.chdir(original_cwd)

    def test_no_active_plan_returns_error(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns error when no active plan and no plan_id specified."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager") as mock_state_manager:
                with patch("bpsai_pair.mcp.tools.planning.PlanParser"):
                    with patch("bpsai_pair.mcp.tools.planning.TaskParser"):
                        mock_state_manager.return_value.get_active_plan_id.return_value = None

                        result = asyncio.run(plan_status(plan_id=None))

                        assert "error" in result
                        assert result["error"]["code"] == "PLAN_NOT_FOUND"
        finally:
            os.chdir(original_cwd)

    def test_returns_plan_status_with_specified_id(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns plan status when plan_id is specified."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, Task, Sprint, TaskStatus, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        mock_plan = Plan(
            id="PLAN-001",
            title="Test Plan",
            status=PlanStatus.IN_PROGRESS,
            type=PlanType.FEATURE,
            goals=["Goal 1", "Goal 2"],
            sprints=[
                Sprint(id="sprint-1", title="Sprint 1"),
                Sprint(id="sprint-2", title="Sprint 2"),
            ],
        )

        mock_tasks = [
            Task(id="TASK-001", title="Task 1", plan_id="PLAN-001", status=TaskStatus.DONE, sprint="sprint-1"),
            Task(id="TASK-002", title="Task 2", plan_id="PLAN-001", status=TaskStatus.IN_PROGRESS, sprint="sprint-1"),
            Task(id="TASK-003", title="Task 3", plan_id="PLAN-001", status=TaskStatus.PENDING, sprint="sprint-2"),
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager"):
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    with patch("bpsai_pair.mcp.tools.planning.TaskParser") as mock_task_parser:
                        mock_plan_parser.return_value.get_plan_by_id.return_value = mock_plan
                        mock_task_parser.return_value.get_tasks_for_plan.return_value = mock_tasks

                        result = asyncio.run(plan_status(plan_id="PLAN-001"))

                        assert "error" not in result
                        assert result["plan"]["id"] == "PLAN-001"
                        assert result["plan"]["title"] == "Test Plan"
                        assert result["plan"]["status"] == "in_progress"
                        assert result["plan"]["type"] == "feature"
                        assert result["goals"] == ["Goal 1", "Goal 2"]
                        assert result["total_tasks"] == 3
                        assert result["task_counts"]["done"] == 1
                        assert result["task_counts"]["in_progress"] == 1
                        assert result["task_counts"]["pending"] == 1
        finally:
            os.chdir(original_cwd)

    def test_returns_plan_status_with_active_plan(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns active plan status when no plan_id specified."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, Task, TaskStatus, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        mock_plan = Plan(
            id="PLAN-ACTIVE",
            title="Active Plan",
            status=PlanStatus.IN_PROGRESS,
            type=PlanType.FEATURE,
        )

        mock_tasks = [
            Task(id="TASK-001", title="Task 1", plan_id="PLAN-ACTIVE", status=TaskStatus.PENDING),
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager") as mock_state_manager:
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    with patch("bpsai_pair.mcp.tools.planning.TaskParser") as mock_task_parser:
                        mock_state_manager.return_value.get_active_plan_id.return_value = "PLAN-ACTIVE"
                        mock_plan_parser.return_value.get_plan_by_id.return_value = mock_plan
                        mock_task_parser.return_value.get_tasks_for_plan.return_value = mock_tasks

                        result = asyncio.run(plan_status(plan_id=None))

                        assert "error" not in result
                        assert result["plan"]["id"] == "PLAN-ACTIVE"
        finally:
            os.chdir(original_cwd)

    def test_calculates_progress_percentage(self, mock_server, setup_paircoder_dir, tmp_path):
        """Correctly calculates progress percentage."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, Task, TaskStatus, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan", status=PlanStatus.IN_PROGRESS, type=PlanType.FEATURE)
        mock_tasks = [
            Task(id="TASK-001", title="Task 1", plan_id="PLAN-001", status=TaskStatus.DONE),
            Task(id="TASK-002", title="Task 2", plan_id="PLAN-001", status=TaskStatus.DONE),
            Task(id="TASK-003", title="Task 3", plan_id="PLAN-001", status=TaskStatus.PENDING),
            Task(id="TASK-004", title="Task 4", plan_id="PLAN-001", status=TaskStatus.PENDING),
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager"):
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    with patch("bpsai_pair.mcp.tools.planning.TaskParser") as mock_task_parser:
                        mock_plan_parser.return_value.get_plan_by_id.return_value = mock_plan
                        mock_task_parser.return_value.get_tasks_for_plan.return_value = mock_tasks

                        result = asyncio.run(plan_status(plan_id="PLAN-001"))

                        assert result["progress_percent"] == 50  # 2 done out of 4
        finally:
            os.chdir(original_cwd)

    def test_handles_zero_tasks(self, mock_server, setup_paircoder_dir, tmp_path):
        """Handles plans with zero tasks."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        mock_plan = Plan(id="PLAN-001", title="Empty Plan", status=PlanStatus.PLANNED, type=PlanType.FEATURE)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager"):
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    with patch("bpsai_pair.mcp.tools.planning.TaskParser") as mock_task_parser:
                        mock_plan_parser.return_value.get_plan_by_id.return_value = mock_plan
                        mock_task_parser.return_value.get_tasks_for_plan.return_value = []

                        result = asyncio.run(plan_status(plan_id="PLAN-001"))

                        assert result["total_tasks"] == 0
                        assert result["progress_percent"] == 0
        finally:
            os.chdir(original_cwd)

    def test_calculates_sprint_progress(self, mock_server, setup_paircoder_dir, tmp_path):
        """Calculates progress for each sprint."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, Task, Sprint, TaskStatus, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        mock_plan = Plan(
            id="PLAN-001",
            title="Test Plan",
            status=PlanStatus.IN_PROGRESS,
            type=PlanType.FEATURE,
            sprints=[
                Sprint(id="sprint-1", title="Sprint 1"),
                Sprint(id="sprint-2", title="Sprint 2"),
            ],
        )

        mock_tasks = [
            Task(id="TASK-001", title="Task 1", plan_id="PLAN-001", status=TaskStatus.DONE, sprint="sprint-1"),
            Task(id="TASK-002", title="Task 2", plan_id="PLAN-001", status=TaskStatus.DONE, sprint="sprint-1"),
            Task(id="TASK-003", title="Task 3", plan_id="PLAN-001", status=TaskStatus.PENDING, sprint="sprint-2"),
            Task(id="TASK-004", title="Task 4", plan_id="PLAN-001", status=TaskStatus.PENDING, sprint="sprint-2"),
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager"):
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    with patch("bpsai_pair.mcp.tools.planning.TaskParser") as mock_task_parser:
                        mock_plan_parser.return_value.get_plan_by_id.return_value = mock_plan
                        mock_task_parser.return_value.get_tasks_for_plan.return_value = mock_tasks

                        result = asyncio.run(plan_status(plan_id="PLAN-001"))

                        assert len(result["sprint_progress"]) == 2

                        sprint1 = next(s for s in result["sprint_progress"] if s["id"] == "sprint-1")
                        assert sprint1["done"] == 2
                        assert sprint1["total"] == 2
                        assert sprint1["percent"] == 100

                        sprint2 = next(s for s in result["sprint_progress"] if s["id"] == "sprint-2")
                        assert sprint2["done"] == 0
                        assert sprint2["total"] == 2
                        assert sprint2["percent"] == 0
        finally:
            os.chdir(original_cwd)

    def test_identifies_blocked_tasks(self, mock_server, setup_paircoder_dir, tmp_path):
        """Identifies and returns blocked tasks."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, Task, TaskStatus, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan", status=PlanStatus.IN_PROGRESS, type=PlanType.FEATURE)

        # Create tasks with depends_on attribute (mock the attribute)
        task1 = Task(id="TASK-001", title="Task 1", plan_id="PLAN-001", status=TaskStatus.DONE)
        task2 = Task(id="TASK-002", title="Blocked Task", plan_id="PLAN-001", status=TaskStatus.BLOCKED)
        task2.depends_on = ["TASK-003"]  # Add depends_on attribute
        task3 = Task(id="TASK-003", title="Task 3", plan_id="PLAN-001", status=TaskStatus.PENDING)

        mock_tasks = [task1, task2, task3]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager"):
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    with patch("bpsai_pair.mcp.tools.planning.TaskParser") as mock_task_parser:
                        mock_plan_parser.return_value.get_plan_by_id.return_value = mock_plan
                        mock_task_parser.return_value.get_tasks_for_plan.return_value = mock_tasks

                        result = asyncio.run(plan_status(plan_id="PLAN-001"))

                        assert len(result["blockers"]) == 1
                        assert result["blockers"][0]["task_id"] == "TASK-002"
                        assert result["blockers"][0]["title"] == "Blocked Task"
                        assert result["blockers"][0]["blocked_by"] == ["TASK-003"]
        finally:
            os.chdir(original_cwd)

    def test_handles_exception(self, mock_server, setup_paircoder_dir, tmp_path):
        """Handles unexpected exceptions gracefully."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager") as mock_state_manager:
                mock_state_manager.side_effect = RuntimeError("Unexpected error")

                result = asyncio.run(plan_status(plan_id="PLAN-001"))

                assert "error" in result
                assert result["error"]["code"] == "ERROR"
                assert "Unexpected error" in result["error"]["message"]
        finally:
            os.chdir(original_cwd)

    def test_counts_all_status_types(self, mock_server, setup_paircoder_dir, tmp_path):
        """Counts all task status types correctly."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, Task, TaskStatus, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan", status=PlanStatus.IN_PROGRESS, type=PlanType.FEATURE)

        task_blocked = Task(id="TASK-BLOCKED", title="Blocked", plan_id="PLAN-001", status=TaskStatus.BLOCKED)
        task_blocked.depends_on = []  # Add depends_on attribute

        mock_tasks = [
            Task(id="TASK-001", title="Pending", plan_id="PLAN-001", status=TaskStatus.PENDING),
            Task(id="TASK-002", title="In Progress", plan_id="PLAN-001", status=TaskStatus.IN_PROGRESS),
            Task(id="TASK-003", title="Done", plan_id="PLAN-001", status=TaskStatus.DONE),
            task_blocked,
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager"):
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    with patch("bpsai_pair.mcp.tools.planning.TaskParser") as mock_task_parser:
                        mock_plan_parser.return_value.get_plan_by_id.return_value = mock_plan
                        mock_task_parser.return_value.get_tasks_for_plan.return_value = mock_tasks

                        result = asyncio.run(plan_status(plan_id="PLAN-001"))

                        assert result["task_counts"]["pending"] == 1
                        assert result["task_counts"]["in_progress"] == 1
                        assert result["task_counts"]["done"] == 1
                        assert result["task_counts"]["blocked"] == 1
                        assert result["total_tasks"] == 4
        finally:
            os.chdir(original_cwd)


class TestPlanList:
    """Tests for paircoder_plan_list tool."""

    @pytest.fixture
    def mock_server(self):
        """Create a mock MCP server that captures registered tools."""
        server = MagicMock()
        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        server.tool = tool_decorator
        server._registered_tools = registered_tools
        return server

    @pytest.fixture
    def setup_paircoder_dir(self, tmp_path):
        """Set up a .paircoder directory structure."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "plans").mkdir()
        (paircoder_dir / "context").mkdir()
        return paircoder_dir

    def test_no_paircoder_dir_returns_error(self, mock_server, tmp_path):
        """Returns error when no .paircoder directory found."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools

        register_planning_tools(mock_server)
        plan_list = mock_server._registered_tools["paircoder_plan_list"]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = asyncio.run(plan_list())

            assert "error" in result
            assert result["error"]["code"] == "NOT_FOUND"
        finally:
            os.chdir(original_cwd)

    def test_returns_empty_list_when_no_plans(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns empty list when no plans exist."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools

        register_planning_tools(mock_server)
        plan_list = mock_server._registered_tools["paircoder_plan_list"]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager") as mock_state_manager:
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    mock_plan_parser.return_value.parse_all.return_value = []
                    mock_state_manager.return_value.get_active_plan_id.return_value = None

                    result = asyncio.run(plan_list())

                    assert result == []
        finally:
            os.chdir(original_cwd)

    def test_returns_list_of_plans(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns list of all plans with metadata."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, Sprint, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_list = mock_server._registered_tools["paircoder_plan_list"]

        mock_plans = [
            Plan(
                id="PLAN-001",
                title="Plan 1",
                status=PlanStatus.IN_PROGRESS,
                type=PlanType.FEATURE,
                sprints=[Sprint(id="s1", title="Sprint 1")],
            ),
            Plan(
                id="PLAN-002",
                title="Plan 2",
                status=PlanStatus.COMPLETE,
                type=PlanType.BUGFIX,
                sprints=[Sprint(id="s1", title="S1"), Sprint(id="s2", title="S2")],
            ),
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager") as mock_state_manager:
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    mock_plan_parser.return_value.parse_all.return_value = mock_plans
                    mock_state_manager.return_value.get_active_plan_id.return_value = None

                    result = asyncio.run(plan_list())

                    assert len(result) == 2

                    plan1 = next(p for p in result if p["id"] == "PLAN-001")
                    assert plan1["title"] == "Plan 1"
                    assert plan1["status"] == "in_progress"
                    assert plan1["type"] == "feature"
                    assert plan1["sprint_count"] == 1
                    assert plan1["is_active"] is False

                    plan2 = next(p for p in result if p["id"] == "PLAN-002")
                    assert plan2["title"] == "Plan 2"
                    assert plan2["status"] == "complete"
                    assert plan2["type"] == "bugfix"
                    assert plan2["sprint_count"] == 2
        finally:
            os.chdir(original_cwd)

    def test_marks_active_plan(self, mock_server, setup_paircoder_dir, tmp_path):
        """Marks the active plan correctly."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_list = mock_server._registered_tools["paircoder_plan_list"]

        mock_plans = [
            Plan(id="PLAN-001", title="Plan 1", status=PlanStatus.IN_PROGRESS, type=PlanType.FEATURE),
            Plan(id="PLAN-002", title="Plan 2", status=PlanStatus.PLANNED, type=PlanType.FEATURE),
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager") as mock_state_manager:
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    mock_plan_parser.return_value.parse_all.return_value = mock_plans
                    mock_state_manager.return_value.get_active_plan_id.return_value = "PLAN-001"

                    result = asyncio.run(plan_list())

                    plan1 = next(p for p in result if p["id"] == "PLAN-001")
                    assert plan1["is_active"] is True

                    plan2 = next(p for p in result if p["id"] == "PLAN-002")
                    assert plan2["is_active"] is False
        finally:
            os.chdir(original_cwd)

    def test_handles_exception(self, mock_server, setup_paircoder_dir, tmp_path):
        """Handles unexpected exceptions gracefully."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools

        register_planning_tools(mock_server)
        plan_list = mock_server._registered_tools["paircoder_plan_list"]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                mock_plan_parser.side_effect = RuntimeError("Database error")

                result = asyncio.run(plan_list())

                assert "error" in result
                assert result["error"]["code"] == "ERROR"
                assert "Database error" in result["error"]["message"]
        finally:
            os.chdir(original_cwd)

    def test_handles_plans_with_no_sprints(self, mock_server, setup_paircoder_dir, tmp_path):
        """Handles plans that have no sprints."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_list = mock_server._registered_tools["paircoder_plan_list"]

        mock_plans = [
            Plan(id="PLAN-001", title="Plan 1", status=PlanStatus.PLANNED, type=PlanType.CHORE),
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager") as mock_state_manager:
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    mock_plan_parser.return_value.parse_all.return_value = mock_plans
                    mock_state_manager.return_value.get_active_plan_id.return_value = None

                    result = asyncio.run(plan_list())

                    assert len(result) == 1
                    assert result[0]["sprint_count"] == 0
        finally:
            os.chdir(original_cwd)


class TestPlanningToolsRegistration:
    """Tests for planning tools registration."""

    def test_tools_are_registered_with_server(self):
        """register_planning_tools registers both tools with the server."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools

        server = MagicMock()
        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        server.tool = tool_decorator

        register_planning_tools(server)

        assert "paircoder_plan_status" in registered_tools
        assert "paircoder_plan_list" in registered_tools

    def test_plan_status_is_async(self):
        """paircoder_plan_status is an async function."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        import asyncio

        server = MagicMock()
        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        server.tool = tool_decorator

        register_planning_tools(server)

        assert asyncio.iscoroutinefunction(registered_tools["paircoder_plan_status"])

    def test_plan_list_is_async(self):
        """paircoder_plan_list is an async function."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        import asyncio

        server = MagicMock()
        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        server.tool = tool_decorator

        register_planning_tools(server)

        assert asyncio.iscoroutinefunction(registered_tools["paircoder_plan_list"])


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def mock_server(self):
        """Create a mock MCP server that captures registered tools."""
        server = MagicMock()
        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        server.tool = tool_decorator
        server._registered_tools = registered_tools
        return server

    @pytest.fixture
    def setup_paircoder_dir(self, tmp_path):
        """Set up a .paircoder directory structure."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "plans").mkdir()
        (paircoder_dir / "tasks").mkdir()
        (paircoder_dir / "context").mkdir()
        return paircoder_dir

    def test_sprint_with_no_tasks(self, mock_server, setup_paircoder_dir, tmp_path):
        """Handles sprint with no tasks (empty sprint)."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, Task, Sprint, TaskStatus, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        mock_plan = Plan(
            id="PLAN-001",
            title="Test Plan",
            status=PlanStatus.IN_PROGRESS,
            type=PlanType.FEATURE,
            sprints=[
                Sprint(id="sprint-1", title="Sprint 1"),
                Sprint(id="sprint-2", title="Empty Sprint"),  # No tasks
            ],
        )

        mock_tasks = [
            Task(id="TASK-001", title="Task 1", plan_id="PLAN-001", status=TaskStatus.DONE, sprint="sprint-1"),
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager"):
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    with patch("bpsai_pair.mcp.tools.planning.TaskParser") as mock_task_parser:
                        mock_plan_parser.return_value.get_plan_by_id.return_value = mock_plan
                        mock_task_parser.return_value.get_tasks_for_plan.return_value = mock_tasks

                        result = asyncio.run(plan_status(plan_id="PLAN-001"))

                        sprint2 = next(s for s in result["sprint_progress"] if s["id"] == "sprint-2")
                        assert sprint2["total"] == 0
                        assert sprint2["done"] == 0
                        assert sprint2["percent"] == 0  # Should be 0, not divide by zero
        finally:
            os.chdir(original_cwd)

    def test_task_with_cancelled_status(self, mock_server, setup_paircoder_dir, tmp_path):
        """Handles tasks with cancelled status (not in task_counts)."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, Task, TaskStatus, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan", status=PlanStatus.IN_PROGRESS, type=PlanType.FEATURE)
        mock_tasks = [
            Task(id="TASK-001", title="Done Task", plan_id="PLAN-001", status=TaskStatus.DONE),
            Task(id="TASK-002", title="Cancelled Task", plan_id="PLAN-001", status=TaskStatus.CANCELLED),
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager"):
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    with patch("bpsai_pair.mcp.tools.planning.TaskParser") as mock_task_parser:
                        mock_plan_parser.return_value.get_plan_by_id.return_value = mock_plan
                        mock_task_parser.return_value.get_tasks_for_plan.return_value = mock_tasks

                        result = asyncio.run(plan_status(plan_id="PLAN-001"))

                        # Cancelled is not in the tracked statuses, so total should be 1
                        assert result["task_counts"]["done"] == 1
                        # CANCELLED is not tracked in task_counts by the implementation
                        assert result["total_tasks"] == 1  # Only counts tracked statuses
        finally:
            os.chdir(original_cwd)

    def test_multiple_blocked_tasks(self, mock_server, setup_paircoder_dir, tmp_path):
        """Handles multiple blocked tasks."""
        from bpsai_pair.mcp.tools.planning import register_planning_tools
        from bpsai_pair.planning.models import Plan, Task, TaskStatus, PlanStatus, PlanType

        register_planning_tools(mock_server)
        plan_status = mock_server._registered_tools["paircoder_plan_status"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan", status=PlanStatus.IN_PROGRESS, type=PlanType.FEATURE)

        task1 = Task(id="TASK-001", title="Blocked 1", plan_id="PLAN-001", status=TaskStatus.BLOCKED)
        task1.depends_on = ["TASK-003"]
        task2 = Task(id="TASK-002", title="Blocked 2", plan_id="PLAN-001", status=TaskStatus.BLOCKED)
        task2.depends_on = ["TASK-004", "TASK-005"]

        mock_tasks = [task1, task2]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.mcp.tools.planning.StateManager"):
                with patch("bpsai_pair.mcp.tools.planning.PlanParser") as mock_plan_parser:
                    with patch("bpsai_pair.mcp.tools.planning.TaskParser") as mock_task_parser:
                        mock_plan_parser.return_value.get_plan_by_id.return_value = mock_plan
                        mock_task_parser.return_value.get_tasks_for_plan.return_value = mock_tasks

                        result = asyncio.run(plan_status(plan_id="PLAN-001"))

                        assert len(result["blockers"]) == 2
                        assert result["task_counts"]["blocked"] == 2
        finally:
            os.chdir(original_cwd)
