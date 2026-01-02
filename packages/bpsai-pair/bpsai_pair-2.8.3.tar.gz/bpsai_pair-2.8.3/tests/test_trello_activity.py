"""Tests for Trello activity logging functionality."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone


class TestActivityEvent:
    """Tests for ActivityEvent enum."""

    def test_all_events_defined(self):
        """Test all expected events are defined."""
        from bpsai_pair.trello.activity import ActivityEvent

        assert hasattr(ActivityEvent, 'TASK_STARTED')
        assert hasattr(ActivityEvent, 'TASK_COMPLETED')
        assert hasattr(ActivityEvent, 'TASK_BLOCKED')
        assert hasattr(ActivityEvent, 'PR_CREATED')
        assert hasattr(ActivityEvent, 'PR_MERGED')
        assert hasattr(ActivityEvent, 'PROGRESS')


class TestActivityEventFormat:
    """Tests for activity event formatting."""

    def test_task_started_format(self):
        """Test task started event format."""
        from bpsai_pair.trello.activity import format_activity_comment, ActivityEvent

        comment = format_activity_comment(
            ActivityEvent.TASK_STARTED,
            agent="Claude",
            timestamp=datetime(2025, 12, 17, 10, 30, 0, tzinfo=timezone.utc)
        )

        assert "🚀" in comment
        assert "Started" in comment
        assert "Claude" in comment
        assert "10:30" in comment

    def test_task_completed_format(self):
        """Test task completed event format."""
        from bpsai_pair.trello.activity import format_activity_comment, ActivityEvent

        comment = format_activity_comment(
            ActivityEvent.TASK_COMPLETED,
            summary="Implemented all features",
            timestamp=datetime(2025, 12, 17, 14, 0, 0, tzinfo=timezone.utc)
        )

        assert "✅" in comment
        assert "Completed" in comment
        assert "Implemented all features" in comment

    def test_task_blocked_format(self):
        """Test task blocked event format."""
        from bpsai_pair.trello.activity import format_activity_comment, ActivityEvent

        comment = format_activity_comment(
            ActivityEvent.TASK_BLOCKED,
            reason="Waiting on API design review"
        )

        assert "⊘" in comment or "🚫" in comment
        assert "Blocked" in comment
        assert "Waiting on API design review" in comment

    def test_pr_created_format(self):
        """Test PR created event format."""
        from bpsai_pair.trello.activity import format_activity_comment, ActivityEvent

        comment = format_activity_comment(
            ActivityEvent.PR_CREATED,
            pr_url="https://github.com/org/repo/pull/123"
        )

        assert "🔗" in comment
        assert "PR" in comment
        assert "https://github.com/org/repo/pull/123" in comment

    def test_pr_merged_format(self):
        """Test PR merged event format."""
        from bpsai_pair.trello.activity import format_activity_comment, ActivityEvent

        comment = format_activity_comment(ActivityEvent.PR_MERGED)

        assert "🎉" in comment
        assert "merged" in comment.lower()

    def test_progress_format(self):
        """Test progress event format."""
        from bpsai_pair.trello.activity import format_activity_comment, ActivityEvent

        comment = format_activity_comment(
            ActivityEvent.PROGRESS,
            note="Halfway done with implementation"
        )

        assert "📝" in comment
        assert "Progress" in comment
        assert "Halfway done with implementation" in comment

    def test_uses_current_time_by_default(self):
        """Test uses current time if timestamp not provided."""
        from bpsai_pair.trello.activity import format_activity_comment, ActivityEvent

        before = datetime.now(timezone.utc)
        comment = format_activity_comment(ActivityEvent.TASK_STARTED, agent="Test")
        after = datetime.now(timezone.utc)

        # Should contain a time from the current hour
        assert before.strftime("%H:") in comment or after.strftime("%H:") in comment


class TestTrelloActivityLogger:
    """Tests for TrelloActivityLogger class."""

    @pytest.fixture
    def mock_service(self):
        """Create mock TrelloService."""
        service = Mock()
        service.board = Mock()
        return service

    @pytest.fixture
    def logger(self, mock_service):
        """Create TrelloActivityLogger with mock service."""
        from bpsai_pair.trello.activity import TrelloActivityLogger
        return TrelloActivityLogger(mock_service)

    def test_log_task_started(self, logger, mock_service):
        """Test logging task started event."""
        mock_card = Mock()
        mock_service.find_card_with_prefix.return_value = (mock_card, Mock())

        result = logger.log_task_started("TASK-001", agent="Claude")

        assert result is True
        mock_service.add_comment.assert_called_once()
        comment = mock_service.add_comment.call_args[0][1]
        assert "🚀" in comment
        assert "Claude" in comment

    def test_log_task_completed(self, logger, mock_service):
        """Test logging task completed event."""
        mock_card = Mock()
        mock_service.find_card_with_prefix.return_value = (mock_card, Mock())

        result = logger.log_task_completed("TASK-001", summary="All tests pass")

        assert result is True
        mock_service.add_comment.assert_called_once()
        comment = mock_service.add_comment.call_args[0][1]
        assert "✅" in comment
        assert "All tests pass" in comment

    def test_log_task_blocked(self, logger, mock_service):
        """Test logging task blocked event."""
        mock_card = Mock()
        mock_service.find_card_with_prefix.return_value = (mock_card, Mock())

        result = logger.log_task_blocked("TASK-001", reason="Waiting on design")

        assert result is True
        mock_service.add_comment.assert_called_once()
        comment = mock_service.add_comment.call_args[0][1]
        assert "Blocked" in comment
        assert "Waiting on design" in comment

    def test_log_pr_created(self, logger, mock_service):
        """Test logging PR created event."""
        mock_card = Mock()
        mock_service.find_card_with_prefix.return_value = (mock_card, Mock())

        result = logger.log_pr_created("TASK-001", pr_url="https://github.com/pr/1")

        assert result is True
        mock_service.add_comment.assert_called_once()
        comment = mock_service.add_comment.call_args[0][1]
        assert "🔗" in comment
        assert "https://github.com/pr/1" in comment

    def test_log_pr_merged(self, logger, mock_service):
        """Test logging PR merged event."""
        mock_card = Mock()
        mock_service.find_card_with_prefix.return_value = (mock_card, Mock())

        result = logger.log_pr_merged("TASK-001")

        assert result is True
        mock_service.add_comment.assert_called_once()
        comment = mock_service.add_comment.call_args[0][1]
        assert "🎉" in comment

    def test_log_progress(self, logger, mock_service):
        """Test logging progress event."""
        mock_card = Mock()
        mock_service.find_card_with_prefix.return_value = (mock_card, Mock())

        result = logger.log_progress("TASK-001", note="50% done")

        assert result is True
        mock_service.add_comment.assert_called_once()
        comment = mock_service.add_comment.call_args[0][1]
        assert "📝" in comment
        assert "50% done" in comment

    def test_log_event_card_not_found(self, logger, mock_service):
        """Test logging when card not found returns False."""
        mock_service.find_card_with_prefix.return_value = (None, None)

        result = logger.log_task_started("TASK-999", agent="Claude")

        assert result is False
        mock_service.add_comment.assert_not_called()

    def test_log_generic_event(self, logger, mock_service):
        """Test logging generic event."""
        from bpsai_pair.trello.activity import ActivityEvent

        mock_card = Mock()
        mock_service.find_card_with_prefix.return_value = (mock_card, Mock())

        result = logger.log_event(
            "TASK-001",
            ActivityEvent.PROGRESS,
            note="Custom progress note"
        )

        assert result is True
        mock_service.add_comment.assert_called_once()


class TestActivityLoggerFromConfig:
    """Tests for creating activity logger from config."""

    def test_create_from_credentials(self):
        """Test creating logger from Trello credentials."""
        with patch("bpsai_pair.trello.activity.TrelloService") as mock_service_class:
            from bpsai_pair.trello.activity import create_activity_logger

            mock_service = Mock()
            mock_service_class.return_value = mock_service

            logger = create_activity_logger(
                api_key="key123",
                token="token456",
                board_id="board789"
            )

            assert logger is not None
            mock_service_class.assert_called_once_with("key123", "token456")
            mock_service.set_board.assert_called_once_with("board789")


class TestHookIntegration:
    """Tests for hook system integration."""

    def test_log_trello_activity_handler(self):
        """Test the log_trello_activity hook handler."""
        from bpsai_pair.trello.activity import ActivityEvent

        # This tests the conceptual integration - the actual hook is in hooks.py
        # Just verify the event types are compatible
        expected_events = {
            "on_task_start": ActivityEvent.TASK_STARTED,
            "on_task_complete": ActivityEvent.TASK_COMPLETED,
            "on_task_block": ActivityEvent.TASK_BLOCKED,
        }

        for hook_event, activity_event in expected_events.items():
            assert activity_event is not None
