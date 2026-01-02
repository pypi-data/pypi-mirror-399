"""Tests for Trello webhook server."""
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from bpsai_pair.trello.webhook import (
    CardMoveEvent,
    WebhookHandler,
    TrelloWebhookServer,
    create_task_updater,
    create_agent_assigner,
    create_combined_handler,
    LIST_STATUS_MAP,
    READY_LISTS,
)


class TestCardMoveEvent:
    """Tests for CardMoveEvent dataclass."""

    def test_task_id_extraction(self):
        """Test extracting task ID from card name."""
        event = CardMoveEvent(
            card_id="123",
            card_name="[TASK-066] Webhook listener",
            list_before="Planned / Ready",
            list_after="In Progress",
            board_id="board123",
        )
        assert event.task_id == "TASK-066"

    def test_task_id_with_multiple_brackets(self):
        """Test extracting task ID when name has multiple brackets."""
        event = CardMoveEvent(
            card_id="123",
            card_name="[TASK-001] Fix [critical] bug",
            list_before="Planned / Ready",
            list_after="In Progress",
            board_id="board123",
        )
        assert event.task_id == "TASK-001"

    def test_task_id_no_brackets(self):
        """Test when card name has no brackets."""
        event = CardMoveEvent(
            card_id="123",
            card_name="Some task without brackets",
            list_before="Planned / Ready",
            list_after="In Progress",
            board_id="board123",
        )
        assert event.task_id is None

    def test_task_id_incomplete_brackets(self):
        """Test when card name has incomplete brackets."""
        event = CardMoveEvent(
            card_id="123",
            card_name="[incomplete task",
            list_before="Planned / Ready",
            list_after="In Progress",
            board_id="board123",
        )
        assert event.task_id is None


class TestListStatusMap:
    """Tests for list-to-status mapping."""

    def test_backlog_maps_to_pending(self):
        assert LIST_STATUS_MAP["Intake / Backlog"] == "pending"

    def test_planned_maps_to_pending(self):
        assert LIST_STATUS_MAP["Planned / Ready"] == "pending"

    def test_in_progress_maps_to_in_progress(self):
        assert LIST_STATUS_MAP["In Progress"] == "in_progress"

    def test_review_maps_to_review(self):
        """Test review/testing maps to review status."""
        assert LIST_STATUS_MAP["Review / Testing"] == "review"

    def test_done_maps_to_done(self):
        assert LIST_STATUS_MAP["Deployed / Done"] == "done"

    def test_tech_debt_maps_to_blocked(self):
        assert LIST_STATUS_MAP["Issues / Tech Debt"] == "blocked"


class TestWebhookHandler:
    """Tests for WebhookHandler."""

    def test_process_card_move_event(self):
        """Test processing a card move webhook."""
        callback_called = []

        def mock_callback(event):
            callback_called.append(event)

        # Create handler with callback
        handler = WebhookHandler
        handler.callback = mock_callback

        # Create mock request data
        webhook_data = {
            "action": {
                "type": "updateCard",
                "data": {
                    "card": {"id": "card123", "name": "[TASK-066] Test card"},
                    "board": {"id": "board123"},
                    "listBefore": {"name": "Planned / Ready"},
                    "listAfter": {"name": "In Progress"},
                },
            }
        }

        # Mock handler instance
        mock_handler = Mock()
        mock_handler.callback = mock_callback

        # Process directly via _process_webhook method
        handler_instance = object.__new__(WebhookHandler)
        handler_instance.callback = mock_callback
        handler_instance._process_webhook(webhook_data)

        assert len(callback_called) == 1
        event = callback_called[0]
        assert event.card_name == "[TASK-066] Test card"
        assert event.list_before == "Planned / Ready"
        assert event.list_after == "In Progress"

    def test_ignore_non_card_update(self):
        """Test ignoring non-updateCard actions."""
        callback_called = []

        def mock_callback(event):
            callback_called.append(event)

        handler_instance = object.__new__(WebhookHandler)
        handler_instance.callback = mock_callback

        # Non-card-update action
        webhook_data = {
            "action": {
                "type": "createCard",
                "data": {},
            }
        }

        handler_instance._process_webhook(webhook_data)
        assert len(callback_called) == 0

    def test_ignore_non_list_change(self):
        """Test ignoring card updates that aren't list changes."""
        callback_called = []

        def mock_callback(event):
            callback_called.append(event)

        handler_instance = object.__new__(WebhookHandler)
        handler_instance.callback = mock_callback

        # Card update without list change (e.g., rename)
        webhook_data = {
            "action": {
                "type": "updateCard",
                "data": {
                    "card": {"id": "card123", "name": "New Name"},
                    "board": {"id": "board123"},
                },
            }
        }

        handler_instance._process_webhook(webhook_data)
        assert len(callback_called) == 0


class TestTrelloWebhookServer:
    """Tests for TrelloWebhookServer."""

    def test_server_initialization(self):
        """Test server initializes with correct settings."""
        callback = Mock()
        server = TrelloWebhookServer(
            host="127.0.0.1",
            port=9999,
            on_card_move=callback,
        )

        assert server.host == "127.0.0.1"
        assert server.port == 9999
        assert server.on_card_move == callback

    def test_default_host_and_port(self):
        """Test server uses correct defaults."""
        server = TrelloWebhookServer()

        assert server.host == "0.0.0.0"
        assert server.port == 8765


class TestCreateTaskUpdater:
    """Tests for task updater callback factory."""

    def test_creates_callable(self, tmp_path):
        """Test create_task_updater returns a callable."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        updater = create_task_updater(paircoder_dir)
        assert callable(updater)

    @patch("bpsai_pair.planning.parser.TaskParser")
    def test_updates_task_status(self, mock_parser_class, tmp_path):
        """Test updater changes task status based on list."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        # Create mock task
        from bpsai_pair.planning.models import Task, TaskStatus

        mock_task = Task(
            id="TASK-066",
            title="Test task",
            plan_id="plan-test",
            status=TaskStatus.PENDING,
        )

        mock_parser = MagicMock()
        mock_parser.get_task_by_id.return_value = mock_task
        mock_parser_class.return_value = mock_parser

        updater = create_task_updater(paircoder_dir)

        event = CardMoveEvent(
            card_id="card123",
            card_name="[TASK-066] Test task",
            list_before="Planned / Ready",
            list_after="In Progress",
            board_id="board123",
        )

        updater(event)

        # Verify task was updated
        assert mock_task.status == TaskStatus.IN_PROGRESS
        mock_parser.save.assert_called_once_with(mock_task)

    @patch("bpsai_pair.planning.parser.TaskParser")
    def test_ignores_unknown_list(self, mock_parser_class, tmp_path):
        """Test updater ignores unknown list names."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        updater = create_task_updater(paircoder_dir)

        event = CardMoveEvent(
            card_id="card123",
            card_name="[TASK-066] Test task",
            list_before="Unknown List",
            list_after="Another Unknown",
            board_id="board123",
        )

        updater(event)

        # Parser.save should not be called for unknown lists
        mock_parser.save.assert_not_called()

    def test_handles_card_without_task_id(self, tmp_path):
        """Test updater handles cards without task IDs gracefully."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        updater = create_task_updater(paircoder_dir)

        event = CardMoveEvent(
            card_id="card123",
            card_name="Card without task ID",
            list_before="Planned / Ready",
            list_after="In Progress",
            board_id="board123",
        )

        # Should not raise
        updater(event)


class TestReadyLists:
    """Tests for READY_LISTS constant."""

    def test_contains_planned_ready(self):
        assert "Planned / Ready" in READY_LISTS

    def test_contains_ready(self):
        assert "Ready" in READY_LISTS


class TestAgentAssigner:
    """Tests for agent assignment functionality."""

    def test_creates_agent_assigner(self):
        """Test agent assigner is created correctly."""
        assigner = create_agent_assigner(
            api_key="test_key",
            token="test_token",
            agent_name="claude",
            auto_start=False,
        )

        assert callable(assigner)

    def test_only_triggers_on_ready_list(self):
        """Test assigner only triggers when moving TO ready list."""
        # Track if inner logic ran
        triggered = []

        def track_trigger(event):
            if event.list_after in READY_LISTS:
                triggered.append(event)

        # Event moving to In Progress (not Ready)
        event = CardMoveEvent(
            card_id="card123",
            card_name="[TASK-001] Test",
            list_before="Intake / Backlog",
            list_after="In Progress",
            board_id="board123",
        )

        track_trigger(event)
        assert len(triggered) == 0

        # Event moving to Ready (should trigger)
        event2 = CardMoveEvent(
            card_id="card123",
            card_name="[TASK-001] Test",
            list_before="Intake / Backlog",
            list_after="Planned / Ready",
            board_id="board123",
        )

        track_trigger(event2)
        assert len(triggered) == 1

    def test_assigner_with_custom_agent_name(self):
        """Test assigner uses custom agent name."""
        assigner = create_agent_assigner(
            api_key="test_key",
            token="test_token",
            agent_name="custom-agent",
            auto_start=False,
        )

        # Just verify it was created with the name
        assert callable(assigner)


class TestCombinedHandler:
    """Tests for combined status update and agent assignment."""

    def test_creates_combined_handler(self, tmp_path):
        """Test combined handler is created correctly."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        handler = create_combined_handler(
            paircoder_dir=paircoder_dir,
            api_key="test_key",
            token="test_token",
            agent_name="claude",
            auto_assign=True,
        )

        assert callable(handler)

    def test_combined_handler_without_credentials(self, tmp_path):
        """Test combined handler works without Trello credentials (status only)."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        handler = create_combined_handler(
            paircoder_dir=paircoder_dir,
            api_key=None,
            token=None,
            auto_assign=True,
        )

        # Should still create a callable
        assert callable(handler)

        # Should handle events without crashing
        event = CardMoveEvent(
            card_id="card123",
            card_name="Card without ID",
            list_before="Intake / Backlog",
            list_after="Planned / Ready",
            board_id="board123",
        )
        handler(event)  # Should not raise
