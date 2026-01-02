"""Tests for standup module."""
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from bpsai_pair.planning.standup import (
    StandupSummary,
    StandupGenerator,
    generate_standup,
)


class TestStandupSummary:
    """Tests for StandupSummary dataclass."""

    def test_default_values(self):
        """Test default initialization."""
        summary = StandupSummary()
        assert summary.completed == []
        assert summary.in_progress == []
        assert summary.blocked == []
        assert summary.ready == []
        assert summary.since is None
        assert summary.until is None
        assert summary.total_completed == 0
        assert summary.total_in_progress == 0
        assert summary.total_blocked == 0

    def test_with_tasks(self):
        """Test initialization with tasks."""
        completed = [{"id": "TASK-001", "title": "Done task"}]
        in_progress = [{"id": "TASK-002", "title": "Working on"}]
        summary = StandupSummary(
            completed=completed,
            in_progress=in_progress,
            total_completed=1,
            total_in_progress=1,
        )
        assert len(summary.completed) == 1
        assert len(summary.in_progress) == 1

    def test_with_date_range(self):
        """Test initialization with date range."""
        since = datetime.now() - timedelta(hours=24)
        until = datetime.now()
        summary = StandupSummary(since=since, until=until)
        assert summary.since == since
        assert summary.until == until

    def test_to_markdown_empty(self):
        """Test markdown output with no tasks."""
        summary = StandupSummary()
        md = summary.to_markdown()
        assert "# Daily Standup" in md
        assert "## Completed" in md
        assert "No tasks completed" in md
        assert "## In Progress" in md
        assert "No tasks in progress" in md
        assert "Completed: 0" in md

    def test_to_markdown_with_completed(self):
        """Test markdown output with completed tasks."""
        summary = StandupSummary(
            completed=[{"id": "TASK-001", "title": "Finished task"}],
            total_completed=1,
        )
        md = summary.to_markdown()
        assert "[TASK-001] Finished task" in md
        assert "Completed: 1" in md

    def test_to_markdown_with_in_progress(self):
        """Test markdown output with in progress tasks."""
        summary = StandupSummary(
            in_progress=[{"id": "TASK-002", "title": "Working task"}],
            total_in_progress=1,
        )
        md = summary.to_markdown()
        assert "[TASK-002] Working task" in md
        assert "In Progress: 1" in md

    def test_to_markdown_with_blockers(self):
        """Test markdown output with blocked tasks."""
        summary = StandupSummary(
            blocked=[{"id": "TASK-003", "title": "Blocked task", "blocked_reason": "API issue"}],
            total_blocked=1,
        )
        md = summary.to_markdown()
        assert "## Blockers" in md
        assert "[TASK-003] Blocked task" in md
        assert "Reason: API issue" in md
        assert "Blocked: 1" in md

    def test_to_markdown_blocked_unknown_reason(self):
        """Test markdown with blocked task missing reason."""
        summary = StandupSummary(
            blocked=[{"id": "TASK-001", "title": "Blocked"}],
        )
        md = summary.to_markdown()
        assert "Reason: Unknown" in md

    def test_to_markdown_with_ready(self):
        """Test markdown output with ready tasks."""
        summary = StandupSummary(
            ready=[{"id": "TASK-004", "title": "Ready task", "priority": "P1"}],
        )
        md = summary.to_markdown()
        assert "## Up Next" in md
        assert "[TASK-004] Ready task" in md
        assert "P1" in md

    def test_to_markdown_ready_priority_missing(self):
        """Test markdown with ready task missing priority."""
        summary = StandupSummary(
            ready=[{"id": "TASK-001", "title": "Ready"}],
        )
        md = summary.to_markdown()
        assert "(P?)" in md

    def test_to_markdown_limits_ready(self):
        """Test markdown limits ready tasks to 3."""
        summary = StandupSummary(
            ready=[
                {"id": f"TASK-{i:03d}", "title": f"Ready {i}", "priority": "P1"}
                for i in range(5)
            ],
        )
        md = summary.to_markdown()
        assert "TASK-000" in md
        assert "TASK-001" in md
        assert "TASK-002" in md
        assert "TASK-003" not in md
        assert "TASK-004" not in md

    def test_to_markdown_full(self):
        """Test markdown output with all sections."""
        summary = StandupSummary(
            completed=[{"id": "TASK-001", "title": "Finished task"}],
            in_progress=[{"id": "TASK-002", "title": "Working task"}],
            blocked=[{"id": "TASK-003", "title": "Blocked task", "blocked_reason": "API issue"}],
            ready=[{"id": "TASK-004", "title": "Ready task", "priority": "P1"}],
            total_completed=1,
            total_in_progress=1,
            total_blocked=1,
        )
        md = summary.to_markdown()
        assert "[TASK-001] Finished task" in md
        assert "[TASK-002] Working task" in md
        assert "## Blockers" in md
        assert "[TASK-003] Blocked task" in md
        assert "Reason: API issue" in md
        assert "## Up Next" in md
        assert "[TASK-004] Ready task" in md
        assert "Completed: 1 | In Progress: 1 | Blocked: 1" in md

    def test_to_slack_empty(self):
        """Test Slack output with no tasks."""
        summary = StandupSummary()
        slack = summary.to_slack()
        assert ":sunrise:" in slack
        assert "*Daily Standup" in slack  # Contains date suffix
        assert "*Completed*" in slack
        assert "_No tasks completed_" in slack
        assert "*In Progress*" in slack
        assert "_No tasks in progress_" in slack

    def test_to_slack_with_completed(self):
        """Test Slack output with completed tasks."""
        summary = StandupSummary(
            completed=[{"id": "TASK-001", "title": "Done"}],
        )
        slack = summary.to_slack()
        assert "`TASK-001` Done" in slack
        assert ":white_check_mark:" in slack

    def test_to_slack_with_in_progress(self):
        """Test Slack output with in progress tasks."""
        summary = StandupSummary(
            in_progress=[{"id": "TASK-002", "title": "Working"}],
        )
        slack = summary.to_slack()
        assert "`TASK-002` Working" in slack
        assert ":hammer_and_wrench:" in slack

    def test_to_slack_with_blockers(self):
        """Test Slack output with blocked tasks."""
        summary = StandupSummary(
            blocked=[{"id": "TASK-003", "title": "Blocked", "blocked_reason": "Issue"}],
        )
        slack = summary.to_slack()
        assert ":no_entry:" in slack
        assert "`TASK-003` Blocked - _Issue_" in slack

    def test_to_slack_blocked_unknown(self):
        """Test Slack with blocked task missing reason."""
        summary = StandupSummary(
            blocked=[{"id": "TASK-001", "title": "Blocked"}],
        )
        slack = summary.to_slack()
        assert "_Unknown_" in slack

    def test_to_trello_comment_empty(self):
        """Test Trello comment with no tasks."""
        summary = StandupSummary()
        comment = summary.to_trello_comment()
        assert "## Standup Update" in comment
        assert "**Completed:**" not in comment
        assert "**Working On:**" not in comment
        assert "**Blocked:**" not in comment

    def test_to_trello_comment_with_completed(self):
        """Test Trello comment with completed tasks."""
        summary = StandupSummary(
            completed=[{"id": "TASK-001", "title": "Done"}],
        )
        comment = summary.to_trello_comment()
        assert "**Completed:**" in comment
        assert "- TASK-001: Done" in comment

    def test_to_trello_comment_with_in_progress(self):
        """Test Trello comment with in progress tasks."""
        summary = StandupSummary(
            in_progress=[{"id": "TASK-002", "title": "Working"}],
        )
        comment = summary.to_trello_comment()
        assert "**Working On:**" in comment
        assert "- TASK-002: Working" in comment

    def test_to_trello_comment_with_blocked(self):
        """Test Trello comment with blocked tasks."""
        summary = StandupSummary(
            blocked=[{"id": "TASK-003", "title": "Blocked", "blocked_reason": "API down"}],
        )
        comment = summary.to_trello_comment()
        assert "**Blocked:**" in comment
        assert "- TASK-003: API down" in comment

    def test_to_trello_comment_blocked_no_reason(self):
        """Test Trello comment with blocked task no reason."""
        summary = StandupSummary(
            blocked=[{"id": "TASK-001", "title": "Blocked"}],
        )
        comment = summary.to_trello_comment()
        assert "- TASK-001: Unknown" in comment


class TestStandupGenerator:
    """Tests for StandupGenerator class."""

    def test_init(self, tmp_path):
        """Test generator initialization."""
        gen = StandupGenerator(tmp_path)
        assert gen.paircoder_dir == tmp_path
        assert gen.tasks_dir == tmp_path / "tasks"

    def test_init_string_path(self):
        """Test initialization with string path."""
        gen = StandupGenerator("/tmp/test")
        assert gen.paircoder_dir == Path("/tmp/test")


class TestGenerateStandup:
    """Tests for generate_standup function."""

    def test_default_path(self, tmp_path, monkeypatch):
        """Test default paircoder directory."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".paircoder" / "tasks").mkdir(parents=True)

        with patch.object(StandupGenerator, 'generate') as mock_gen:
            mock_gen.return_value = StandupSummary()
            result = generate_standup()
            assert "Daily Standup" in result

    def test_markdown_format(self, tmp_path):
        """Test markdown format output."""
        with patch.object(StandupGenerator, 'generate') as mock_gen:
            mock_gen.return_value = StandupSummary()
            result = generate_standup(paircoder_dir=tmp_path, format="markdown")
            assert "# Daily Standup" in result

    def test_slack_format(self, tmp_path):
        """Test slack format output."""
        with patch.object(StandupGenerator, 'generate') as mock_gen:
            mock_gen.return_value = StandupSummary()
            result = generate_standup(paircoder_dir=tmp_path, format="slack")
            assert ":sunrise:" in result

    def test_trello_format(self, tmp_path):
        """Test trello format output."""
        with patch.object(StandupGenerator, 'generate') as mock_gen:
            mock_gen.return_value = StandupSummary()
            result = generate_standup(paircoder_dir=tmp_path, format="trello")
            assert "## Standup Update" in result

    def test_with_plan_id(self, tmp_path):
        """Test with plan_id filter."""
        with patch.object(StandupGenerator, 'generate') as mock_gen:
            mock_gen.return_value = StandupSummary()
            generate_standup(paircoder_dir=tmp_path, plan_id="PLAN-001")
            mock_gen.assert_called_with(since_hours=24, plan_id="PLAN-001")

    def test_custom_since_hours(self, tmp_path):
        """Test custom since_hours."""
        with patch.object(StandupGenerator, 'generate') as mock_gen:
            mock_gen.return_value = StandupSummary()
            generate_standup(paircoder_dir=tmp_path, since_hours=48)
            mock_gen.assert_called_with(since_hours=48, plan_id=None)
