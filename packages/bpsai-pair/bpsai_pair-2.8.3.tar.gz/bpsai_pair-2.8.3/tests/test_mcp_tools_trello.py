"""
Tests for MCP Trello Tools

Tests the Trello integration MCP tools:
- paircoder_trello_sync_plan
- paircoder_trello_update_card
- Helper functions
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import os


class TestFindPaircoderDir:
    """Tests for find_paircoder_dir helper."""

    def test_raises_when_not_found(self, tmp_path):
        """find_paircoder_dir raises FileNotFoundError when no .paircoder exists."""
        from bpsai_pair.mcp.tools.trello import find_paircoder_dir

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(FileNotFoundError):
                find_paircoder_dir()
        finally:
            os.chdir(original_cwd)

    def test_finds_directory_in_current(self, tmp_path):
        """find_paircoder_dir finds .paircoder in current directory."""
        from bpsai_pair.mcp.tools.trello import find_paircoder_dir

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
        from bpsai_pair.mcp.tools.trello import find_paircoder_dir

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


class TestGetTrelloService:
    """Tests for get_trello_service helper."""

    def test_raises_when_no_token(self):
        """get_trello_service raises ValueError when not connected."""
        with patch("bpsai_pair.trello.auth.load_token", return_value=None):
            from bpsai_pair.mcp.tools.trello import get_trello_service
            with pytest.raises(ValueError, match="Not connected to Trello"):
                get_trello_service()

    def test_creates_service_with_token(self):
        """get_trello_service creates TrelloService with valid token."""
        mock_token_data = {"api_key": "test-key", "token": "test-token"}
        mock_service = MagicMock()

        with patch("bpsai_pair.trello.auth.load_token", return_value=mock_token_data):
            with patch("bpsai_pair.trello.client.TrelloService", return_value=mock_service) as mock_class:
                from bpsai_pair.mcp.tools.trello import get_trello_service
                result = get_trello_service()

                mock_class.assert_called_once_with(api_key="test-key", token="test-token")
                assert result == mock_service


class TestTrelloSyncPlan:
    """Tests for paircoder_trello_sync_plan tool."""

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
        return paircoder_dir

    def test_dry_run_returns_preview(self, mock_server, setup_paircoder_dir, tmp_path):
        """Dry run returns preview of cards to create."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        from bpsai_pair.planning.models import Task, Plan, TaskStatus

        register_trello_tools(mock_server)
        sync_plan = mock_server._registered_tools["paircoder_trello_sync_plan"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan")
        mock_tasks = [
            Task(id="TASK-001", title="Task 1", plan_id="PLAN-001", sprint="Sprint 1"),
            Task(id="TASK-002", title="Task 2", plan_id="PLAN-001", sprint="Sprint 1"),
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.PlanParser") as mock_plan_parser_cls:
                with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                    mock_plan_parser_cls.return_value.get_plan_by_id.return_value = mock_plan
                    mock_task_parser_cls.return_value.get_tasks_for_plan.return_value = mock_tasks

                    result = asyncio.run(sync_plan(plan_id="PLAN-001", dry_run=True))

                    assert result["dry_run"] is True
                    assert result["plan_id"] == "PLAN-001"
                    assert len(result["cards_created"]) == 2
                    assert result["cards_created"][0]["task_id"] == "TASK-001"
                    assert result["cards_created"][0]["would_create"] is True
        finally:
            os.chdir(original_cwd)

    def test_plan_not_found_returns_error(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns error when plan is not found."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools

        register_trello_tools(mock_server)
        sync_plan = mock_server._registered_tools["paircoder_trello_sync_plan"]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.PlanParser") as mock_plan_parser_cls:
                with patch("bpsai_pair.planning.parser.TaskParser"):
                    mock_plan_parser_cls.return_value.get_plan_by_id.return_value = None

                    result = asyncio.run(sync_plan(plan_id="NONEXISTENT"))

                    assert "error" in result
                    assert result["error"]["code"] == "PLAN_NOT_FOUND"
        finally:
            os.chdir(original_cwd)

    def test_no_tasks_returns_error(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns error when no tasks found for plan."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        from bpsai_pair.planning.models import Plan

        register_trello_tools(mock_server)
        sync_plan = mock_server._registered_tools["paircoder_trello_sync_plan"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.PlanParser") as mock_plan_parser_cls:
                with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                    mock_plan_parser_cls.return_value.get_plan_by_id.return_value = mock_plan
                    mock_task_parser_cls.return_value.get_tasks_for_plan.return_value = []

                    result = asyncio.run(sync_plan(plan_id="PLAN-001"))

                    assert "error" in result
                    assert result["error"]["code"] == "NO_TASKS"
        finally:
            os.chdir(original_cwd)

    def test_no_paircoder_dir_returns_error(self, mock_server, tmp_path):
        """Returns error when no .paircoder directory found."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools

        register_trello_tools(mock_server)
        sync_plan = mock_server._registered_tools["paircoder_trello_sync_plan"]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = asyncio.run(sync_plan(plan_id="PLAN-001"))

            assert "error" in result
            assert result["error"]["code"] == "NOT_FOUND"
        finally:
            os.chdir(original_cwd)

    def test_trello_not_connected_returns_error(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns error when Trello is not connected."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        from bpsai_pair.planning.models import Task, Plan

        register_trello_tools(mock_server)
        sync_plan = mock_server._registered_tools["paircoder_trello_sync_plan"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan")
        mock_tasks = [Task(id="TASK-001", title="Task 1", plan_id="PLAN-001")]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.PlanParser") as mock_plan_parser_cls:
                with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                    with patch("bpsai_pair.trello.auth.load_token", return_value=None):
                        mock_plan_parser_cls.return_value.get_plan_by_id.return_value = mock_plan
                        mock_task_parser_cls.return_value.get_tasks_for_plan.return_value = mock_tasks

                        result = asyncio.run(sync_plan(plan_id="PLAN-001", dry_run=False))

                        assert "error" in result
                        assert result["error"]["code"] == "TRELLO_NOT_CONNECTED"
        finally:
            os.chdir(original_cwd)

    def test_no_board_id_returns_error(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns error when no board_id is specified."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        from bpsai_pair.planning.models import Task, Plan

        register_trello_tools(mock_server)
        sync_plan = mock_server._registered_tools["paircoder_trello_sync_plan"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan")
        mock_tasks = [Task(id="TASK-001", title="Task 1", plan_id="PLAN-001")]
        mock_service = MagicMock()

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.PlanParser") as mock_plan_parser_cls:
                with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                    with patch("bpsai_pair.trello.auth.load_token", return_value={"api_key": "k", "token": "t"}):
                        with patch("bpsai_pair.trello.client.TrelloService", return_value=mock_service):
                            mock_plan_parser_cls.return_value.get_plan_by_id.return_value = mock_plan
                            mock_task_parser_cls.return_value.get_tasks_for_plan.return_value = mock_tasks

                            result = asyncio.run(sync_plan(plan_id="PLAN-001", board_id=None))

                            assert "error" in result
                            assert result["error"]["code"] == "NO_BOARD"
        finally:
            os.chdir(original_cwd)

    def test_sync_creates_cards(self, mock_server, setup_paircoder_dir, tmp_path):
        """Successfully syncs tasks to Trello cards."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        from bpsai_pair.planning.models import Task, Plan

        register_trello_tools(mock_server)
        sync_plan = mock_server._registered_tools["paircoder_trello_sync_plan"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan")
        task = Task(id="TASK-001", title="Task 1", plan_id="PLAN-001", sprint="Sprint 1", priority="P1", complexity=50)
        task.objective = "Complete feature implementation"  # Add objective attribute used by trello.py
        mock_tasks = [task]

        mock_service = MagicMock()
        mock_list = MagicMock()
        mock_list.name = "Sprint 1"
        mock_list.list_cards.return_value = []
        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_list.add_card.return_value = mock_card

        mock_service.get_board_lists.return_value = {"Sprint 1": mock_list}
        mock_service.lists = {"Sprint 1": mock_list}

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.PlanParser") as mock_plan_parser_cls:
                with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                    with patch("bpsai_pair.trello.auth.load_token", return_value={"api_key": "k", "token": "t"}):
                        with patch("bpsai_pair.trello.client.TrelloService", return_value=mock_service):
                            mock_plan_parser_cls.return_value.get_plan_by_id.return_value = mock_plan
                            mock_task_parser_cls.return_value.get_tasks_for_plan.return_value = mock_tasks

                            result = asyncio.run(sync_plan(
                                plan_id="PLAN-001",
                                board_id="board-123",
                                create_lists=True,
                                link_cards=False,  # Disable linking to avoid _update_task_with_card_id
                            ))

                            assert "error" not in result
                            assert result["board_id"] == "board-123"
                            assert len(result["cards_created"]) == 1
                            assert result["cards_created"][0]["task_id"] == "TASK-001"
                            assert result["cards_created"][0]["card_id"] == "card-123"
        finally:
            os.chdir(original_cwd)

    def test_sync_updates_existing_cards(self, mock_server, setup_paircoder_dir, tmp_path):
        """Updates existing cards instead of creating duplicates."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        from bpsai_pair.planning.models import Task, Plan

        register_trello_tools(mock_server)
        sync_plan = mock_server._registered_tools["paircoder_trello_sync_plan"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan")
        task = Task(id="TASK-001", title="Task 1", plan_id="PLAN-001", sprint="Sprint 1")
        task.objective = "Update feature"  # Add objective attribute used by trello.py
        mock_tasks = [task]

        mock_service = MagicMock()
        mock_list = MagicMock()
        mock_list.name = "Sprint 1"

        existing_card = MagicMock()
        existing_card.id = "existing-card-123"
        existing_card.name = "[TASK-001] Task 1"
        mock_list.list_cards.return_value = [existing_card]

        mock_service.get_board_lists.return_value = {"Sprint 1": mock_list}
        mock_service.lists = {"Sprint 1": mock_list}

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.PlanParser") as mock_plan_parser_cls:
                with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                    with patch("bpsai_pair.trello.auth.load_token", return_value={"api_key": "k", "token": "t"}):
                        with patch("bpsai_pair.trello.client.TrelloService", return_value=mock_service):
                            mock_plan_parser_cls.return_value.get_plan_by_id.return_value = mock_plan
                            mock_task_parser_cls.return_value.get_tasks_for_plan.return_value = mock_tasks

                            result = asyncio.run(sync_plan(plan_id="PLAN-001", board_id="board-123"))

                            assert len(result["cards_updated"]) == 1
                            assert result["cards_updated"][0]["card_id"] == "existing-card-123"
                            existing_card.set_description.assert_called_once()
        finally:
            os.chdir(original_cwd)

    def test_sync_creates_lists_when_missing(self, mock_server, setup_paircoder_dir, tmp_path):
        """Creates lists when they don't exist and create_lists=True."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        from bpsai_pair.planning.models import Task, Plan

        register_trello_tools(mock_server)
        sync_plan = mock_server._registered_tools["paircoder_trello_sync_plan"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan")
        mock_tasks = [
            Task(id="TASK-001", title="Task 1", plan_id="PLAN-001", sprint="New Sprint"),
        ]

        mock_service = MagicMock()
        mock_board = MagicMock()
        mock_service.board = mock_board

        # First call: list doesn't exist, second call after creation: it exists
        new_list = MagicMock()
        new_list.name = "New Sprint"
        new_list.list_cards.return_value = []
        mock_card = MagicMock()
        mock_card.id = "card-new"
        new_list.add_card.return_value = mock_card

        mock_service.get_board_lists.return_value = {}
        mock_board.all_lists.return_value = [new_list]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.PlanParser") as mock_plan_parser_cls:
                with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                    with patch("bpsai_pair.trello.auth.load_token", return_value={"api_key": "k", "token": "t"}):
                        with patch("bpsai_pair.trello.client.TrelloService", return_value=mock_service):
                            mock_plan_parser_cls.return_value.get_plan_by_id.return_value = mock_plan
                            mock_task_parser_cls.return_value.get_tasks_for_plan.return_value = mock_tasks

                            result = asyncio.run(sync_plan(
                                plan_id="PLAN-001",
                                board_id="board-123",
                                create_lists=True,
                                link_cards=False,
                            ))

                            assert "New Sprint" in result["lists_created"]
                            mock_board.add_list.assert_called_once_with("New Sprint")
        finally:
            os.chdir(original_cwd)

    def test_sync_groups_tasks_by_sprint(self, mock_server, setup_paircoder_dir, tmp_path):
        """Groups tasks by sprint when syncing."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        from bpsai_pair.planning.models import Task, Plan

        register_trello_tools(mock_server)
        sync_plan = mock_server._registered_tools["paircoder_trello_sync_plan"]

        mock_plan = Plan(id="PLAN-001", title="Test Plan")
        mock_tasks = [
            Task(id="TASK-001", title="Task 1", plan_id="PLAN-001", sprint="Sprint 1"),
            Task(id="TASK-002", title="Task 2", plan_id="PLAN-001", sprint="Sprint 2"),
            Task(id="TASK-003", title="Task 3", plan_id="PLAN-001", sprint=None),  # Goes to Backlog
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.PlanParser") as mock_plan_parser_cls:
                with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                    mock_plan_parser_cls.return_value.get_plan_by_id.return_value = mock_plan
                    mock_task_parser_cls.return_value.get_tasks_for_plan.return_value = mock_tasks

                    result = asyncio.run(sync_plan(plan_id="PLAN-001", dry_run=True))

                    sprints = {c["sprint"] for c in result["cards_created"]}
                    assert "Sprint 1" in sprints
                    assert "Sprint 2" in sprints
                    assert "Backlog" in sprints  # Default for None sprint
        finally:
            os.chdir(original_cwd)


class TestTrelloUpdateCard:
    """Tests for paircoder_trello_update_card tool."""

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
        (paircoder_dir / "tasks").mkdir()
        return paircoder_dir

    def test_task_not_found_returns_error(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns error when task is not found."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools

        register_trello_tools(mock_server)
        update_card = mock_server._registered_tools["paircoder_trello_update_card"]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                mock_task_parser_cls.return_value.get_task_by_id.return_value = None

                result = asyncio.run(update_card(task_id="NONEXISTENT", action="start"))

                assert "error" in result
                assert result["error"]["code"] == "TASK_NOT_FOUND"
        finally:
            os.chdir(original_cwd)

    def test_task_not_linked_returns_error(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns error when task is not linked to Trello."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        from bpsai_pair.planning.models import Task

        register_trello_tools(mock_server)
        update_card = mock_server._registered_tools["paircoder_trello_update_card"]

        mock_task = Task(id="TASK-001", title="Task 1", plan_id="PLAN-001")
        # Task has no trello_card_id attribute

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                mock_task_parser_cls.return_value.get_task_by_id.return_value = mock_task

                result = asyncio.run(update_card(task_id="TASK-001", action="start"))

                assert "error" in result
                assert result["error"]["code"] == "NOT_LINKED"
        finally:
            os.chdir(original_cwd)

    def test_trello_not_connected_returns_error(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns error when Trello is not connected."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        from bpsai_pair.planning.models import Task

        register_trello_tools(mock_server)
        update_card = mock_server._registered_tools["paircoder_trello_update_card"]

        mock_task = MagicMock(spec=Task)
        mock_task.id = "TASK-001"
        mock_task.trello_card_id = "card-123"

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                with patch("bpsai_pair.trello.auth.load_token", return_value=None):
                    mock_task_parser_cls.return_value.get_task_by_id.return_value = mock_task

                    result = asyncio.run(update_card(task_id="TASK-001", action="start"))

                    assert "error" in result
                    assert result["error"]["code"] == "TRELLO_NOT_CONNECTED"
        finally:
            os.chdir(original_cwd)

    def test_card_not_found_returns_error(self, mock_server, setup_paircoder_dir, tmp_path):
        """Returns error when Trello card is not found."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        from bpsai_pair.planning.models import Task

        register_trello_tools(mock_server)
        update_card = mock_server._registered_tools["paircoder_trello_update_card"]

        mock_task = MagicMock(spec=Task)
        mock_task.id = "TASK-001"
        mock_task.trello_card_id = "card-123"

        mock_service = MagicMock()
        mock_service.find_card.return_value = (None, None)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                with patch("bpsai_pair.trello.auth.load_token", return_value={"api_key": "k", "token": "t"}):
                    with patch("bpsai_pair.trello.client.TrelloService", return_value=mock_service):
                        mock_task_parser_cls.return_value.get_task_by_id.return_value = mock_task

                        result = asyncio.run(update_card(task_id="TASK-001", action="start"))

                        assert "error" in result
                        assert result["error"]["code"] == "CARD_NOT_FOUND"
        finally:
            os.chdir(original_cwd)

    def test_start_action_moves_card(self, mock_server, setup_paircoder_dir, tmp_path):
        """Start action moves card to In Progress."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools

        register_trello_tools(mock_server)
        update_card = mock_server._registered_tools["paircoder_trello_update_card"]

        mock_task = MagicMock()
        mock_task.id = "TASK-001"
        mock_task.trello_card_id = "card-123"

        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_service = MagicMock()
        mock_service.find_card.return_value = (mock_card, "Sprint 1")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                with patch("bpsai_pair.trello.auth.load_token", return_value={"api_key": "k", "token": "t"}):
                    with patch("bpsai_pair.trello.client.TrelloService", return_value=mock_service):
                        mock_task_parser_cls.return_value.get_task_by_id.return_value = mock_task

                        result = asyncio.run(update_card(task_id="TASK-001", action="start"))

                        assert result["updated"] is True
                        assert result["action"] == "start"
                        mock_service.move_card.assert_called_once_with(mock_card, "In Progress")
                        mock_service.add_comment.assert_called_once()
        finally:
            os.chdir(original_cwd)

    def test_complete_action_moves_card_to_done(self, mock_server, setup_paircoder_dir, tmp_path):
        """Complete action moves card to Done."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools

        register_trello_tools(mock_server)
        update_card = mock_server._registered_tools["paircoder_trello_update_card"]

        mock_task = MagicMock()
        mock_task.id = "TASK-001"
        mock_task.trello_card_id = "card-123"

        mock_card = MagicMock()
        mock_service = MagicMock()
        mock_service.find_card.return_value = (mock_card, "In Progress")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                with patch("bpsai_pair.trello.auth.load_token", return_value={"api_key": "k", "token": "t"}):
                    with patch("bpsai_pair.trello.client.TrelloService", return_value=mock_service):
                        mock_task_parser_cls.return_value.get_task_by_id.return_value = mock_task

                        result = asyncio.run(update_card(
                            task_id="TASK-001",
                            action="complete",
                            comment="All tests passing",
                        ))

                        assert result["updated"] is True
                        mock_service.move_card.assert_called_once_with(mock_card, "Done")
                        # Check comment contains completion message
                        call_args = mock_service.add_comment.call_args[0]
                        assert "Completed" in call_args[1]
                        assert "All tests passing" in call_args[1]
        finally:
            os.chdir(original_cwd)

    def test_block_action_adds_label_and_comment(self, mock_server, setup_paircoder_dir, tmp_path):
        """Block action adds blocked label and comment."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools

        register_trello_tools(mock_server)
        update_card = mock_server._registered_tools["paircoder_trello_update_card"]

        mock_task = MagicMock()
        mock_task.id = "TASK-001"
        mock_task.trello_card_id = "card-123"

        mock_card = MagicMock()
        mock_label = MagicMock()
        mock_label.name = "Blocked"

        mock_board = MagicMock()
        mock_board.get_labels.return_value = [mock_label]

        mock_service = MagicMock()
        mock_service.find_card.return_value = (mock_card, "In Progress")
        mock_service.board = mock_board

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                with patch("bpsai_pair.trello.auth.load_token", return_value={"api_key": "k", "token": "t"}):
                    with patch("bpsai_pair.trello.client.TrelloService", return_value=mock_service):
                        mock_task_parser_cls.return_value.get_task_by_id.return_value = mock_task

                        result = asyncio.run(update_card(
                            task_id="TASK-001",
                            action="block",
                            comment="Waiting for API access",
                        ))

                        assert result["updated"] is True
                        mock_card.add_label.assert_called_once_with(mock_label)
                        call_args = mock_service.add_comment.call_args[0]
                        assert "Blocked" in call_args[1]
                        assert "Waiting for API access" in call_args[1]
        finally:
            os.chdir(original_cwd)

    def test_comment_action_adds_comment(self, mock_server, setup_paircoder_dir, tmp_path):
        """Comment action adds a comment to the card."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools

        register_trello_tools(mock_server)
        update_card = mock_server._registered_tools["paircoder_trello_update_card"]

        mock_task = MagicMock()
        mock_task.id = "TASK-001"
        mock_task.trello_card_id = "card-123"

        mock_card = MagicMock()
        mock_service = MagicMock()
        mock_service.find_card.return_value = (mock_card, "In Progress")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                with patch("bpsai_pair.trello.auth.load_token", return_value={"api_key": "k", "token": "t"}):
                    with patch("bpsai_pair.trello.client.TrelloService", return_value=mock_service):
                        mock_task_parser_cls.return_value.get_task_by_id.return_value = mock_task

                        result = asyncio.run(update_card(
                            task_id="TASK-001",
                            action="comment",
                            comment="Progress update: 50% done",
                        ))

                        assert result["updated"] is True
                        mock_service.add_comment.assert_called_once_with(mock_card, "Progress update: 50% done")
        finally:
            os.chdir(original_cwd)

    def test_comment_action_requires_comment(self, mock_server, setup_paircoder_dir, tmp_path):
        """Comment action requires a comment parameter."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools

        register_trello_tools(mock_server)
        update_card = mock_server._registered_tools["paircoder_trello_update_card"]

        mock_task = MagicMock()
        mock_task.id = "TASK-001"
        mock_task.trello_card_id = "card-123"

        mock_card = MagicMock()
        mock_service = MagicMock()
        mock_service.find_card.return_value = (mock_card, "In Progress")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                with patch("bpsai_pair.trello.auth.load_token", return_value={"api_key": "k", "token": "t"}):
                    with patch("bpsai_pair.trello.client.TrelloService", return_value=mock_service):
                        mock_task_parser_cls.return_value.get_task_by_id.return_value = mock_task

                        result = asyncio.run(update_card(task_id="TASK-001", action="comment"))

                        assert "error" in result
                        assert result["error"]["code"] == "MISSING_COMMENT"
        finally:
            os.chdir(original_cwd)

    def test_invalid_action_returns_error(self, mock_server, setup_paircoder_dir, tmp_path):
        """Invalid action returns error."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools

        register_trello_tools(mock_server)
        update_card = mock_server._registered_tools["paircoder_trello_update_card"]

        mock_task = MagicMock()
        mock_task.id = "TASK-001"
        mock_task.trello_card_id = "card-123"

        mock_card = MagicMock()
        mock_service = MagicMock()
        mock_service.find_card.return_value = (mock_card, "In Progress")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("bpsai_pair.planning.parser.TaskParser") as mock_task_parser_cls:
                with patch("bpsai_pair.trello.auth.load_token", return_value={"api_key": "k", "token": "t"}):
                    with patch("bpsai_pair.trello.client.TrelloService", return_value=mock_service):
                        mock_task_parser_cls.return_value.get_task_by_id.return_value = mock_task

                        result = asyncio.run(update_card(task_id="TASK-001", action="invalid_action"))

                        assert "error" in result
                        assert result["error"]["code"] == "INVALID_ACTION"
        finally:
            os.chdir(original_cwd)

    def test_no_paircoder_dir_returns_error(self, mock_server, tmp_path):
        """Returns error when no .paircoder directory found."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools

        register_trello_tools(mock_server)
        update_card = mock_server._registered_tools["paircoder_trello_update_card"]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = asyncio.run(update_card(task_id="TASK-001", action="start"))

            assert "error" in result
            assert result["error"]["code"] == "NOT_FOUND"
        finally:
            os.chdir(original_cwd)


class TestUpdateTaskWithCardId:
    """Tests for _update_task_with_card_id helper."""

    def test_updates_task_file_with_card_id(self, tmp_path):
        """Updates task file frontmatter with trello_card_id."""
        from bpsai_pair.mcp.tools.trello import _update_task_with_card_id

        task_file = tmp_path / "TASK-001.task.md"
        task_file.write_text("""---
id: TASK-001
title: Test Task
status: pending
---

## Objective
Test task content
""")

        mock_parser = MagicMock()
        mock_parser._find_task_file.return_value = task_file

        result = _update_task_with_card_id("TASK-001", "card-abc123", mock_parser)

        assert result is True
        content = task_file.read_text()
        assert 'trello_card_id: "card-abc123"' in content

    def test_returns_false_when_card_id_exists(self, tmp_path):
        """Returns False when trello_card_id already in file."""
        from bpsai_pair.mcp.tools.trello import _update_task_with_card_id

        task_file = tmp_path / "TASK-001.task.md"
        task_file.write_text("""---
id: TASK-001
title: Test Task
trello_card_id: "existing-card"
---

## Objective
Test task content
""")

        mock_parser = MagicMock()
        mock_parser._find_task_file.return_value = task_file

        result = _update_task_with_card_id("TASK-001", "new-card", mock_parser)

        assert result is False
        content = task_file.read_text()
        assert "existing-card" in content
        assert "new-card" not in content

    def test_returns_false_when_task_file_not_found(self, tmp_path):
        """Returns False when task file is not found."""
        from bpsai_pair.mcp.tools.trello import _update_task_with_card_id

        mock_parser = MagicMock()
        mock_parser._find_task_file.return_value = None

        result = _update_task_with_card_id("NONEXISTENT", "card-123", mock_parser)

        assert result is False

    def test_returns_false_on_exception(self, tmp_path):
        """Returns False when an exception occurs."""
        from bpsai_pair.mcp.tools.trello import _update_task_with_card_id

        mock_parser = MagicMock()
        mock_parser._find_task_file.side_effect = Exception("Error")

        result = _update_task_with_card_id("TASK-001", "card-123", mock_parser)

        assert result is False

    def test_preserves_other_frontmatter(self, tmp_path):
        """Preserves other frontmatter fields when adding card ID."""
        from bpsai_pair.mcp.tools.trello import _update_task_with_card_id

        task_file = tmp_path / "TASK-001.task.md"
        task_file.write_text("""---
id: TASK-001
title: Test Task
status: pending
priority: P1
tags:
  - feature
  - urgent
---

## Objective
Test task content
""")

        mock_parser = MagicMock()
        mock_parser._find_task_file.return_value = task_file

        _update_task_with_card_id("TASK-001", "card-xyz", mock_parser)

        content = task_file.read_text()
        assert "id: TASK-001" in content
        assert "title: Test Task" in content
        assert "status: pending" in content
        assert "priority: P1" in content
        assert "- feature" in content
        assert 'trello_card_id: "card-xyz"' in content


class TestTrelloToolsRegistration:
    """Tests for Trello tools registration."""

    def test_tools_are_registered_with_server(self):
        """register_trello_tools registers both tools with the server."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools

        server = MagicMock()
        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        server.tool = tool_decorator

        register_trello_tools(server)

        assert "paircoder_trello_sync_plan" in registered_tools
        assert "paircoder_trello_update_card" in registered_tools

    def test_sync_plan_is_async(self):
        """paircoder_trello_sync_plan is an async function."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        import asyncio

        server = MagicMock()
        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        server.tool = tool_decorator

        register_trello_tools(server)

        assert asyncio.iscoroutinefunction(registered_tools["paircoder_trello_sync_plan"])

    def test_update_card_is_async(self):
        """paircoder_trello_update_card is an async function."""
        from bpsai_pair.mcp.tools.trello import register_trello_tools
        import asyncio

        server = MagicMock()
        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        server.tool = tool_decorator

        register_trello_tools(server)

        assert asyncio.iscoroutinefunction(registered_tools["paircoder_trello_update_card"])
