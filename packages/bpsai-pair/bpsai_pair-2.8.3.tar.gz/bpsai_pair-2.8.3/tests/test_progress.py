"""Tests for Trello progress reporter."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from bpsai_pair.trello.progress import (
    ProgressReporter,
    PROGRESS_TEMPLATES,
    create_progress_reporter,
)


class TestProgressTemplates:
    """Test progress comment templates."""

    def test_started_template_exists(self):
        assert "started" in PROGRESS_TEMPLATES

    def test_progress_template_exists(self):
        assert "progress" in PROGRESS_TEMPLATES

    def test_completed_step_template_exists(self):
        assert "completed_step" in PROGRESS_TEMPLATES

    def test_blocked_template_exists(self):
        assert "blocked" in PROGRESS_TEMPLATES

    def test_waiting_template_exists(self):
        assert "waiting" in PROGRESS_TEMPLATES

    def test_completed_template_exists(self):
        assert "completed" in PROGRESS_TEMPLATES

    def test_review_template_exists(self):
        assert "review" in PROGRESS_TEMPLATES

    def test_templates_have_agent_placeholder(self):
        """All templates should include {agent} placeholder."""
        for name, template in PROGRESS_TEMPLATES.items():
            assert "{agent}" in template, f"Template {name} missing {{agent}}"


class TestProgressReporter:
    """Tests for ProgressReporter class."""

    @pytest.fixture
    def mock_service(self):
        """Create mock Trello service."""
        service = MagicMock()
        mock_card = MagicMock()
        service.find_card.return_value = (mock_card, MagicMock())
        service.find_card_with_prefix.return_value = (mock_card, MagicMock())
        return service

    @pytest.fixture
    def reporter(self, mock_service):
        """Create ProgressReporter with mock service."""
        return ProgressReporter(
            trello_service=mock_service,
            task_id="TASK-001",
            agent_name="test-agent"
        )

    def test_init_with_task_id(self, mock_service):
        """Test initialization with task ID."""
        reporter = ProgressReporter(mock_service, task_id="TASK-001")
        assert reporter._task_id == "TASK-001"
        assert reporter.agent == "claude"

    def test_init_with_card_id(self, mock_service):
        """Test initialization with card ID."""
        reporter = ProgressReporter(mock_service, card_id="abc123")
        assert reporter._card_id == "abc123"

    def test_init_with_custom_agent(self, mock_service):
        """Test initialization with custom agent name."""
        reporter = ProgressReporter(mock_service, agent_name="codex")
        assert reporter.agent == "codex"

    def test_report_start(self, reporter, mock_service):
        """Test reporting task start."""
        result = reporter.report_start()
        assert result is True
        mock_service.add_comment.assert_called_once()
        comment = mock_service.add_comment.call_args[0][1]
        assert "[test-agent]" in comment
        assert "Started" in comment

    def test_report_progress(self, reporter, mock_service):
        """Test reporting progress update."""
        result = reporter.report_progress("Working on implementation")
        assert result is True
        comment = mock_service.add_comment.call_args[0][1]
        assert "Working on implementation" in comment

    def test_report_step_complete(self, reporter, mock_service):
        """Test reporting step completion."""
        result = reporter.report_step_complete("Unit tests")
        assert result is True
        comment = mock_service.add_comment.call_args[0][1]
        assert "Completed" in comment
        assert "Unit tests" in comment

    def test_report_blocked(self, reporter, mock_service):
        """Test reporting blocking issue."""
        result = reporter.report_blocked("Missing API credentials")
        assert result is True
        comment = mock_service.add_comment.call_args[0][1]
        assert "issue" in comment.lower()
        assert "Missing API credentials" in comment

    def test_report_waiting(self, reporter, mock_service):
        """Test reporting waiting for dependency."""
        result = reporter.report_waiting("code review")
        assert result is True
        comment = mock_service.add_comment.call_args[0][1]
        assert "Waiting" in comment
        assert "code review" in comment

    def test_report_completion(self, reporter, mock_service):
        """Test reporting task completion."""
        result = reporter.report_completion("Implemented OAuth2 authentication")
        assert result is True
        comment = mock_service.add_comment.call_args[0][1]
        assert "completed" in comment.lower()
        assert "Implemented OAuth2 authentication" in comment

    def test_report_review(self, reporter, mock_service):
        """Test reporting submitted for review."""
        result = reporter.report_review()
        assert result is True
        comment = mock_service.add_comment.call_args[0][1]
        assert "review" in comment.lower()

    def test_card_not_found(self, mock_service):
        """Test handling when card is not found."""
        mock_service.find_card_with_prefix.return_value = (None, None)
        reporter = ProgressReporter(mock_service, task_id="TASK-999")

        result = reporter.report_start()
        assert result is False
        mock_service.add_comment.assert_not_called()

    def test_comment_includes_timestamp(self, reporter, mock_service):
        """Test that comments include timestamp."""
        reporter.report_start()
        comment = mock_service.add_comment.call_args[0][1]
        # Should contain date format like 2025-12-16
        assert any(c.isdigit() for c in comment)


class TestCreateProgressReporter:
    """Tests for create_progress_reporter factory."""

    @patch("bpsai_pair.trello.auth.load_token")
    def test_returns_none_when_not_connected(self, mock_load_token, tmp_path):
        """Test returns None when Trello not connected."""
        mock_load_token.return_value = None
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()

        result = create_progress_reporter(paircoder_dir, "TASK-001")
        assert result is None

    @patch("bpsai_pair.trello.auth.load_token")
    @patch("bpsai_pair.trello.progress._load_config")
    def test_returns_none_when_no_board(self, mock_config, mock_token, tmp_path):
        """Test returns None when no board configured."""
        mock_token.return_value = {"api_key": "key", "token": "token"}
        mock_config.return_value = {"trello": {}}
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()

        result = create_progress_reporter(paircoder_dir, "TASK-001")
        assert result is None

    @patch("bpsai_pair.trello.auth.load_token")
    @patch("bpsai_pair.trello.progress._load_config")
    @patch("bpsai_pair.trello.client.TrelloService")
    def test_creates_reporter_with_board(self, mock_service, mock_config, mock_token, tmp_path):
        """Test creates reporter when properly configured."""
        mock_token.return_value = {"api_key": "key", "token": "token"}
        mock_config.return_value = {"trello": {"board_id": "board123"}}
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()

        result = create_progress_reporter(paircoder_dir, "TASK-001", "test-agent")

        assert result is not None
        assert result.agent == "test-agent"
        mock_service.return_value.set_board.assert_called_once_with("board123")
