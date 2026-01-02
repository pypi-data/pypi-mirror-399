"""Tests for state.md update check on task completion."""
import os
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from bpsai_pair.cli import app

runner = CliRunner()


@pytest.fixture
def paircoder_repo(tmp_path, monkeypatch):
    """Create a temporary repo with PairCoder structure."""
    # Create .paircoder directory structure
    paircoder_dir = tmp_path / ".paircoder"
    context_dir = paircoder_dir / "context"
    tasks_dir = paircoder_dir / "tasks"

    paircoder_dir.mkdir()
    context_dir.mkdir()
    tasks_dir.mkdir()

    # Create config.yaml with time tracking enabled (for task start time)
    config_file = paircoder_dir / "config.yaml"
    config_file.write_text("""version: 2.1
time_tracking:
  provider: none
  auto_start: true
  auto_stop: true
hooks:
  enabled: true
  on_task_start:
    - start_timer
  on_task_complete:
    - stop_timer
""")

    # Create state.md
    state_file = context_dir / "state.md"
    state_file.write_text("""# Current State

## Active Plan

**Plan:** test-plan
**Status:** In Progress

## Current Focus

Testing state.md check.

## What Was Just Done

- Initial setup

## What's Next

1. Work on test task

## Blockers

None
""")

    # Create a test task file
    task_file = tasks_dir / "T19.1.task.md"
    task_file.write_text("""---
id: T19.1
title: Test Task
plan: test-plan
type: feature
priority: P1
complexity: 20
status: pending
depends_on: []
---

# Objective

Test the state.md check feature.

# Acceptance Criteria

- [ ] Test passes
""")

    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestStateCheckOnCompletion:
    """Tests for blocking task completion when state.md not updated."""

    def test_task_update_done_blocked_when_state_not_updated(self, paircoder_repo):
        """Task completion should be blocked if state.md wasn't updated since task started."""
        # First start the task to record the start time
        result = runner.invoke(app, ["task", "update", "T19.1", "--status", "in_progress", "--no-hooks"])
        assert result.exit_code == 0

        # Small delay to ensure start time is before any potential state.md update
        time.sleep(0.1)

        # Try to complete without updating state.md
        result = runner.invoke(app, ["task", "update", "T19.1", "--status", "done", "--no-hooks"])

        # Should fail with helpful error message
        assert result.exit_code == 1
        assert "state.md not updated" in result.stdout.lower() or "cannot complete" in result.stdout.lower()

    def test_task_update_done_allowed_when_state_updated(self, paircoder_repo):
        """Task completion should succeed if state.md was updated after task started."""
        # Start the task
        result = runner.invoke(app, ["task", "update", "T19.1", "--status", "in_progress", "--no-hooks"])
        assert result.exit_code == 0

        # Small delay
        time.sleep(0.1)

        # Update state.md
        state_file = paircoder_repo / ".paircoder" / "context" / "state.md"
        original_content = state_file.read_text()
        state_file.write_text(original_content + "\n- Completed T19.1\n")

        # Complete the task - should succeed
        result = runner.invoke(app, ["task", "update", "T19.1", "--status", "done", "--no-hooks"])
        assert result.exit_code == 0
        assert "T19.1" in result.stdout

    def test_skip_state_check_flag_allows_bypass(self, paircoder_repo):
        """--skip-state-check should bypass the check with a warning."""
        # Start the task
        result = runner.invoke(app, ["task", "update", "T19.1", "--status", "in_progress", "--no-hooks"])
        assert result.exit_code == 0

        # Complete without updating state.md, but with bypass flag
        result = runner.invoke(app, ["task", "update", "T19.1", "--status", "done", "--skip-state-check", "--no-hooks"])

        # Should succeed with warning
        assert result.exit_code == 0
        assert "warning" in result.stdout.lower() or "skipping" in result.stdout.lower()

    def test_state_check_only_applies_to_done_status(self, paircoder_repo):
        """State check should only apply when transitioning to 'done' status."""
        # Start the task
        result = runner.invoke(app, ["task", "update", "T19.1", "--status", "in_progress", "--no-hooks"])
        assert result.exit_code == 0

        # Transition to review (not done) - should not require state.md update
        result = runner.invoke(app, ["task", "update", "T19.1", "--status", "review", "--no-hooks"])
        assert result.exit_code == 0

    def test_state_check_with_no_active_timer(self, paircoder_repo):
        """State check should handle case when task was never formally started."""
        # Try to complete task directly without starting
        result = runner.invoke(app, ["task", "update", "T19.1", "--status", "done", "--no-hooks"])

        # Should either block or use a different check (e.g., file create time)
        # At minimum it should not crash
        assert result.exit_code in [0, 1]


class TestStateCheckErrorMessages:
    """Tests for helpful error messages when state.md check fails."""

    def test_error_message_includes_instructions(self, paircoder_repo):
        """Error message should include instructions on what to update."""
        # Start the task
        runner.invoke(app, ["task", "update", "T19.1", "--status", "in_progress", "--no-hooks"])
        time.sleep(0.1)

        # Try to complete without updating state.md
        result = runner.invoke(app, ["task", "update", "T19.1", "--status", "done", "--no-hooks"])

        if result.exit_code == 1:
            output = result.stdout.lower()
            # Should mention what to update
            assert "state.md" in output or "what was just done" in output

    def test_error_message_includes_task_id(self, paircoder_repo):
        """Error message should include the task ID being completed."""
        # Start the task
        runner.invoke(app, ["task", "update", "T19.1", "--status", "in_progress", "--no-hooks"])
        time.sleep(0.1)

        # Try to complete
        result = runner.invoke(app, ["task", "update", "T19.1", "--status", "done", "--no-hooks"])

        if result.exit_code == 1:
            assert "T19.1" in result.stdout or "t19.1" in result.stdout.lower()
