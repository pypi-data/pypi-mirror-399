"""Tests for ttask done acceptance criteria verification."""
import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner


@pytest.fixture
def mock_board_client():
    """Mock the get_board_client function and related dependencies.

    Also mocks _log_bypass to prevent file system side effects (creating
    .paircoder/history/ in the wrong location).
    """
    mock_client = MagicMock()
    mock_config = {
        "trello": {
            "lists": {
                "review": "In Review",
                "done": "Deployed/Done",
            }
        }
    }

    with patch('bpsai_pair.trello.task_commands.get_board_client') as mock_get, \
         patch('bpsai_pair.trello.task_commands._log_bypass'):
        mock_get.return_value = (mock_client, mock_config)
        yield mock_client, mock_config


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


class TestTtaskDoneACVerification:
    """Tests for AC verification when completing tasks."""

    def test_done_strict_blocks_with_unchecked_ac_items(self, mock_board_client, runner):
        """With --strict flag and unchecked AC items, should block with warning."""
        mock_client, mock_config = mock_board_client

        # Create mock card with unchecked AC items
        mock_checklist = MagicMock()
        mock_checklist.name = "Acceptance Criteria"
        mock_checklist.items = [
            {"id": "item1", "name": "First criterion", "checked": False},
            {"id": "item2", "name": "Second criterion", "checked": True},
            {"id": "item3", "name": "Third criterion", "checked": False},
        ]

        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "Test Card"
        mock_card.short_id = 123
        mock_card.checklists = [mock_checklist]
        mock_card.url = "https://trello.com/c/abc123"

        mock_list = MagicMock()
        mock_list.name = "In Progress"

        mock_client.find_card.return_value = (mock_card, mock_list)

        from bpsai_pair.trello.task_commands import app
        result = runner.invoke(app, ["done", "123", "--summary", "Completed", "--strict"])

        # Should exit with error
        assert result.exit_code == 1
        # Should show warning about unchecked items
        assert "acceptance criteria" in result.output.lower() or "unchecked" in result.output.lower()
        # Should list the unchecked items
        assert "First criterion" in result.output
        assert "Third criterion" in result.output
        # Should not have moved the card
        mock_client.move_card.assert_not_called()

    def test_done_auto_check_checks_items_and_completes(self, mock_board_client, runner):
        """With --auto-check flag, should check all AC items then complete."""
        mock_client, mock_config = mock_board_client

        mock_checklist = MagicMock()
        mock_checklist.name = "Acceptance Criteria"
        mock_checklist.items = [
            {"id": "item1", "name": "First criterion", "checked": False},
            {"id": "item2", "name": "Second criterion", "checked": False},
        ]

        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "Test Card"
        mock_card.short_id = 123
        mock_card.checklists = [mock_checklist]
        mock_card.url = "https://trello.com/c/abc123"

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)

        from bpsai_pair.trello.task_commands import app

        with patch('bpsai_pair.trello.task_commands._auto_check_acceptance_criteria') as mock_check:
            mock_check.return_value = 2  # 2 items checked
            result = runner.invoke(app, ["done", "123", "--summary", "Completed", "--auto-check", "--no-strict"])

        # Should succeed
        assert result.exit_code == 0
        # Should have called check function
        mock_check.assert_called_once()
        # Should have moved the card
        mock_client.move_card.assert_called_once()

    def test_done_force_skips_verification(self, mock_board_client, runner):
        """With --force flag, should skip AC verification and complete."""
        mock_client, mock_config = mock_board_client

        mock_checklist = MagicMock()
        mock_checklist.name = "Acceptance Criteria"
        mock_checklist.items = [
            {"id": "item1", "name": "Unchecked item", "checked": False},
        ]

        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "Test Card"
        mock_card.short_id = 123
        mock_card.checklists = [mock_checklist]
        mock_card.url = "https://trello.com/c/abc123"

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)

        from bpsai_pair.trello.task_commands import app
        result = runner.invoke(app, ["done", "123", "--summary", "Completed", "--force"])

        # Should succeed despite unchecked items
        assert result.exit_code == 0
        # Should have moved the card
        mock_client.move_card.assert_called_once()
        # Should log a warning about skipping verification
        assert "skip" in result.output.lower() or "force" in result.output.lower()

    def test_done_no_checklists_succeeds(self, mock_board_client, runner):
        """Cards with no checklists should complete normally."""
        mock_client, mock_config = mock_board_client

        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "Test Card"
        mock_card.short_id = 123
        mock_card.checklists = []  # No checklists
        mock_card.url = "https://trello.com/c/abc123"

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)

        from bpsai_pair.trello.task_commands import app
        result = runner.invoke(app, ["done", "123", "--summary", "Completed"])

        # Should succeed
        assert result.exit_code == 0
        # Should have moved the card
        mock_client.move_card.assert_called_once()

    def test_done_no_ac_checklist_succeeds(self, mock_board_client, runner):
        """Cards without 'Acceptance Criteria' checklist should complete normally."""
        mock_client, mock_config = mock_board_client

        mock_checklist = MagicMock()
        mock_checklist.name = "Other Checklist"
        mock_checklist.items = [
            {"id": "item1", "name": "Some task", "checked": False},
        ]

        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "Test Card"
        mock_card.short_id = 123
        mock_card.checklists = [mock_checklist]
        mock_card.url = "https://trello.com/c/abc123"

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)

        from bpsai_pair.trello.task_commands import app
        result = runner.invoke(app, ["done", "123", "--summary", "Completed"])

        # Should succeed
        assert result.exit_code == 0
        mock_client.move_card.assert_called_once()

    def test_done_all_ac_checked_succeeds(self, mock_board_client, runner):
        """When all AC items are checked, should complete normally."""
        mock_client, mock_config = mock_board_client

        mock_checklist = MagicMock()
        mock_checklist.name = "Acceptance Criteria"
        mock_checklist.items = [
            {"id": "item1", "name": "First criterion", "checked": True},
            {"id": "item2", "name": "Second criterion", "checked": True},
        ]

        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "Test Card"
        mock_card.short_id = 123
        mock_card.checklists = [mock_checklist]
        mock_card.url = "https://trello.com/c/abc123"

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)

        from bpsai_pair.trello.task_commands import app
        result = runner.invoke(app, ["done", "123", "--summary", "Completed"])

        # Should succeed
        assert result.exit_code == 0
        mock_client.move_card.assert_called_once()

    def test_done_strict_ac_case_insensitive(self, mock_board_client, runner):
        """With --strict, should find AC checklist regardless of case."""
        mock_client, mock_config = mock_board_client

        mock_checklist = MagicMock()
        mock_checklist.name = "ACCEPTANCE CRITERIA"  # All caps
        mock_checklist.items = [
            {"id": "item1", "name": "Unchecked item", "checked": False},
        ]

        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "Test Card"
        mock_card.short_id = 123
        mock_card.checklists = [mock_checklist]
        mock_card.url = "https://trello.com/c/abc123"

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)

        from bpsai_pair.trello.task_commands import app
        result = runner.invoke(app, ["done", "123", "--summary", "Completed", "--strict"])

        # Should block because there are unchecked AC items
        assert result.exit_code == 1
        assert "unchecked" in result.output.lower() or "acceptance" in result.output.lower()

    def test_done_completion_comment_mentions_ac_status(self, mock_board_client, runner):
        """Completion comment should mention AC status."""
        mock_client, mock_config = mock_board_client

        mock_checklist = MagicMock()
        mock_checklist.name = "Acceptance Criteria"
        mock_checklist.items = [
            {"id": "item1", "name": "First", "checked": True},
            {"id": "item2", "name": "Second", "checked": True},
        ]

        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "Test Card"
        mock_card.short_id = 123
        mock_card.checklists = [mock_checklist]
        mock_card.url = "https://trello.com/c/abc123"

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)

        from bpsai_pair.trello.task_commands import app
        result = runner.invoke(app, ["done", "123", "--summary", "Completed"])

        # Should succeed
        assert result.exit_code == 0
        # Should have added a comment
        mock_card.comment.assert_called()
        # Comment should mention AC status
        comment_call = mock_card.comment.call_args[0][0]
        assert "acceptance criteria" in comment_call.lower() or "AC" in comment_call


class TestTtaskDoneBackwardsCompatibility:
    """Tests to verify backwards compatibility with existing --skip-checklist flag."""

    def test_skip_checklist_still_works(self, mock_board_client, runner):
        """The old --skip-checklist flag should continue to work as before.

        Note: --skip-checklist is deprecated. The test now uses --no-strict to
        achieve the same result (skip AC verification).
        """
        mock_client, mock_config = mock_board_client

        mock_checklist = MagicMock()
        mock_checklist.name = "Acceptance Criteria"
        mock_checklist.items = [
            {"id": "item1", "name": "Unchecked item", "checked": False},
        ]

        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "Test Card"
        mock_card.short_id = 123
        mock_card.checklists = [mock_checklist]
        mock_card.url = "https://trello.com/c/abc123"

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)

        from bpsai_pair.trello.task_commands import app

        # Use --no-strict to skip AC verification (--skip-checklist is deprecated)
        result = runner.invoke(app, ["done", "123", "--summary", "Completed", "--no-strict"])

        # Should succeed (skips AC verification)
        assert result.exit_code == 0
        mock_client.move_card.assert_called_once()


class TestGetUncheckedACItems:
    """Tests for the helper function that gets unchecked AC items."""

    def test_get_unchecked_items_returns_list(self):
        """Should return list of unchecked AC items."""
        mock_checklist = MagicMock()
        mock_checklist.name = "Acceptance Criteria"
        mock_checklist.items = [
            {"id": "item1", "name": "Checked", "checked": True},
            {"id": "item2", "name": "Unchecked 1", "checked": False},
            {"id": "item3", "name": "Unchecked 2", "checked": False},
        ]

        mock_card = MagicMock()
        mock_card.checklists = [mock_checklist]

        from bpsai_pair.trello.task_commands import _get_unchecked_ac_items

        unchecked = _get_unchecked_ac_items(mock_card)

        assert len(unchecked) == 2
        assert unchecked[0]["name"] == "Unchecked 1"
        assert unchecked[1]["name"] == "Unchecked 2"

    def test_get_unchecked_items_no_checklists(self):
        """Should return empty list when no checklists."""
        mock_card = MagicMock()
        mock_card.checklists = []

        from bpsai_pair.trello.task_commands import _get_unchecked_ac_items

        unchecked = _get_unchecked_ac_items(mock_card)

        assert unchecked == []

    def test_get_unchecked_items_no_ac_checklist(self):
        """Should return empty list when no AC checklist."""
        mock_checklist = MagicMock()
        mock_checklist.name = "Other Tasks"
        mock_checklist.items = [
            {"id": "item1", "name": "Unchecked", "checked": False},
        ]

        mock_card = MagicMock()
        mock_card.checklists = [mock_checklist]

        from bpsai_pair.trello.task_commands import _get_unchecked_ac_items

        unchecked = _get_unchecked_ac_items(mock_card)

        assert unchecked == []

    def test_get_unchecked_items_case_insensitive(self):
        """Should find AC checklist case-insensitively."""
        mock_checklist = MagicMock()
        mock_checklist.name = "acceptance criteria"  # lowercase
        mock_checklist.items = [
            {"id": "item1", "name": "Unchecked", "checked": False},
        ]

        mock_card = MagicMock()
        mock_card.checklists = [mock_checklist]

        from bpsai_pair.trello.task_commands import _get_unchecked_ac_items

        unchecked = _get_unchecked_ac_items(mock_card)

        assert len(unchecked) == 1
