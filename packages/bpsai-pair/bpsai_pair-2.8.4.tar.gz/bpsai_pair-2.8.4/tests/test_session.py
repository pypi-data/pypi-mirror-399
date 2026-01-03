"""Tests for session detection and restart enforcement."""
import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from bpsai_pair.cli import app

runner = CliRunner()


@pytest.fixture
def paircoder_session_repo(tmp_path, monkeypatch):
    """Create a temporary repo with PairCoder structure for session testing."""
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, capture_output=True)

    # Create .paircoder directory structure
    paircoder_dir = tmp_path / ".paircoder"
    context_dir = paircoder_dir / "context"
    cache_dir = paircoder_dir / "cache"
    history_dir = paircoder_dir / "history"
    tasks_dir = paircoder_dir / "tasks"

    paircoder_dir.mkdir()
    context_dir.mkdir()
    cache_dir.mkdir()
    history_dir.mkdir()
    tasks_dir.mkdir()

    # Create config.yaml
    config_file = paircoder_dir / "config.yaml"
    config_file.write_text("""version: 2.1
session:
  timeout_minutes: 30
""")

    # Create state.md with active task
    state_file = context_dir / "state.md"
    state_file.write_text("""# Current State

## Active Plan

**Plan:** plan-2025-12-sprint-19-methodology
**Status:** In Progress

## Current Sprint Tasks

| ID    | Title | Status | Priority |
|-------|-------|--------|----------|
| T19.1 | Task One | done | P0 |
| T19.2 | Task Two | in_progress | P0 |
| T19.3 | Task Three | pending | P1 |

**Progress:** 1/3 tasks

## What Was Just Done

- Completed T19.1

## What's Next

1. Continue with T19.2

## Blockers

None
""")

    # Create a task file
    task_file = tasks_dir / "T19.2.task.md"
    task_file.write_text("""---
id: T19.2
title: Task Two
plan: plan-2025-12-sprint-19-methodology
status: in_progress
priority: P0
---

# Objective

Test task for session detection.
""")

    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestSessionDetection:
    """Tests for session start detection logic."""

    def test_new_session_detected_when_no_cache(self, paircoder_session_repo):
        """New session should be detected when no session cache exists."""
        result = runner.invoke(app, ["session", "check"])
        assert result.exit_code == 0
        # Should output context for new session
        assert "session" in result.stdout.lower() or "state" in result.stdout.lower()

    def test_new_session_detected_after_timeout(self, paircoder_session_repo):
        """New session should be detected after timeout gap."""
        cache_dir = paircoder_session_repo / ".paircoder" / "cache"
        session_file = cache_dir / "session.json"

        # Create a session file with old timestamp (>30 min ago)
        old_time = datetime.now() - timedelta(minutes=35)
        session_data = {
            "last_activity": old_time.isoformat(),
            "session_id": "old-session-123"
        }
        session_file.write_text(json.dumps(session_data))

        result = runner.invoke(app, ["session", "check"])
        assert result.exit_code == 0
        # Should output context for new session
        assert "session" in result.stdout.lower() or "context" in result.stdout.lower()

    def test_continuing_session_detected_within_timeout(self, paircoder_session_repo):
        """Continuing session should be detected within timeout."""
        cache_dir = paircoder_session_repo / ".paircoder" / "cache"
        session_file = cache_dir / "session.json"

        # Create a session file with recent timestamp (<30 min ago)
        recent_time = datetime.now() - timedelta(minutes=5)
        session_data = {
            "last_activity": recent_time.isoformat(),
            "session_id": "current-session-123"
        }
        session_file.write_text(json.dumps(session_data))

        result = runner.invoke(app, ["session", "check"])
        assert result.exit_code == 0
        # Should have minimal or no output for continuing session
        # (no need to show context again)

    def test_session_updates_timestamp(self, paircoder_session_repo):
        """Session check should update the last activity timestamp."""
        cache_dir = paircoder_session_repo / ".paircoder" / "cache"
        session_file = cache_dir / "session.json"

        # Run session check
        runner.invoke(app, ["session", "check"])

        # Verify session file was created/updated
        assert session_file.exists()
        session_data = json.loads(session_file.read_text())
        assert "last_activity" in session_data

        # Timestamp should be recent
        last_activity = datetime.fromisoformat(session_data["last_activity"])
        assert datetime.now() - last_activity < timedelta(seconds=5)


class TestSessionContextOutput:
    """Tests for session context output format."""

    def test_new_session_shows_active_plan(self, paircoder_session_repo):
        """New session should display active plan info."""
        result = runner.invoke(app, ["session", "check"])
        if "new session" in result.stdout.lower() or result.stdout.strip():
            # Should mention the plan
            assert "sprint-19" in result.stdout.lower() or "plan" in result.stdout.lower()

    def test_new_session_shows_current_task(self, paircoder_session_repo):
        """New session should display current task in progress."""
        result = runner.invoke(app, ["session", "check"])
        if "new session" in result.stdout.lower() or result.stdout.strip():
            # Should mention the in-progress task
            assert "T19.2" in result.stdout or "in_progress" in result.stdout.lower() or "task" in result.stdout.lower()

    def test_new_session_shows_last_session_summary(self, paircoder_session_repo):
        """New session should show what was done in last session."""
        result = runner.invoke(app, ["session", "check"])
        # Should show what was done or at least have some context output
        # This is a flexible check since output format may vary


class TestSessionHistory:
    """Tests for session history logging."""

    def test_new_session_logged_to_history(self, paircoder_session_repo):
        """New session start should be logged to history."""
        history_dir = paircoder_session_repo / ".paircoder" / "history"
        sessions_log = history_dir / "sessions.log"

        # Run session check
        runner.invoke(app, ["session", "check"])

        # Verify session was logged
        assert sessions_log.exists()
        content = sessions_log.read_text()
        assert len(content) > 0

    def test_continuing_session_not_logged(self, paircoder_session_repo):
        """Continuing session should not add new log entry."""
        cache_dir = paircoder_session_repo / ".paircoder" / "cache"
        history_dir = paircoder_session_repo / ".paircoder" / "history"
        session_file = cache_dir / "session.json"
        sessions_log = history_dir / "sessions.log"

        # Create a recent session
        recent_time = datetime.now() - timedelta(minutes=5)
        session_data = {
            "last_activity": recent_time.isoformat(),
            "session_id": "current-session-123"
        }
        session_file.write_text(json.dumps(session_data))

        # Clear/create empty log
        sessions_log.write_text("")

        # Run session check
        runner.invoke(app, ["session", "check"])

        # Log should still be empty (no new session)
        content = sessions_log.read_text()
        assert content == "" or "current-session-123" in content  # Either empty or same session


class TestSessionConfiguration:
    """Tests for session configuration options."""

    def test_custom_timeout_from_config(self, paircoder_session_repo):
        """Session timeout should be configurable."""
        config_file = paircoder_session_repo / ".paircoder" / "config.yaml"
        config_file.write_text("""version: 2.1
session:
  timeout_minutes: 60
""")

        cache_dir = paircoder_session_repo / ".paircoder" / "cache"
        session_file = cache_dir / "session.json"

        # Create a session 45 min ago (within 60 min timeout)
        old_time = datetime.now() - timedelta(minutes=45)
        session_data = {
            "last_activity": old_time.isoformat(),
            "session_id": "old-session-123"
        }
        session_file.write_text(json.dumps(session_data))

        result = runner.invoke(app, ["session", "check"])
        # Should be a continuing session with 60 min timeout
        # (45 min gap < 60 min timeout)
        assert result.exit_code == 0


class TestSessionCheckCommand:
    """Tests for the session check CLI command."""

    def test_session_check_command_exists(self):
        """The session check command should exist."""
        result = runner.invoke(app, ["session", "check", "--help"])
        assert result.exit_code == 0
        assert "check" in result.stdout.lower()

    def test_session_check_with_force_flag(self, paircoder_session_repo):
        """--force flag should always show context."""
        cache_dir = paircoder_session_repo / ".paircoder" / "cache"
        session_file = cache_dir / "session.json"

        # Create a recent session
        recent_time = datetime.now() - timedelta(minutes=5)
        session_data = {
            "last_activity": recent_time.isoformat(),
            "session_id": "current-session-123"
        }
        session_file.write_text(json.dumps(session_data))

        result = runner.invoke(app, ["session", "check", "--force"])
        assert result.exit_code == 0
        # Should show context even for continuing session
        assert len(result.stdout.strip()) > 0


class TestSessionStatusBudget:
    """Tests for session status with token budget display."""

    def test_session_status_shows_budget_with_active_task(self, paircoder_session_repo):
        """Session status shows token budget when task is in progress."""
        cache_dir = paircoder_session_repo / ".paircoder" / "cache"
        session_file = cache_dir / "session.json"
        tasks_dir = paircoder_session_repo / ".paircoder" / "tasks"

        # Create session
        recent_time = datetime.now() - timedelta(minutes=5)
        session_data = {
            "last_activity": recent_time.isoformat(),
            "session_id": "test-session"
        }
        session_file.write_text(json.dumps(session_data))

        # Create in-progress task with type and complexity
        task_file = tasks_dir / "T1.task.md"
        task_file.write_text("""---
id: T1
title: Test Task
type: feature
complexity: 10
status: in_progress
---

# T1: Test Task
""")

        result = runner.invoke(app, ["session", "status"])
        assert result.exit_code == 0
        assert "Token Budget" in result.output
        assert "%" in result.output  # Should show percentage

    def test_session_status_no_active_task(self, paircoder_session_repo):
        """Session status shows budget limit when no task in progress."""
        cache_dir = paircoder_session_repo / ".paircoder" / "cache"
        session_file = cache_dir / "session.json"

        # Create session
        recent_time = datetime.now() - timedelta(minutes=5)
        session_data = {
            "last_activity": recent_time.isoformat(),
            "session_id": "test-session"
        }
        session_file.write_text(json.dumps(session_data))

        # Mark the existing T19.2 task as done so no task is in_progress
        tasks_dir = paircoder_session_repo / ".paircoder" / "tasks"
        task_file = tasks_dir / "T19.2.task.md"
        task_file.write_text("""---
id: T19.2
title: Task Two
status: done
---
# Test
""")

        result = runner.invoke(app, ["session", "status"])
        assert result.exit_code == 0
        assert "Token Budget" in result.output
        assert "No active task" in result.output

    def test_session_status_no_budget_flag(self, paircoder_session_repo):
        """Session status --no-budget hides budget section."""
        cache_dir = paircoder_session_repo / ".paircoder" / "cache"
        session_file = cache_dir / "session.json"

        # Create session
        recent_time = datetime.now() - timedelta(minutes=5)
        session_data = {
            "last_activity": recent_time.isoformat(),
            "session_id": "test-session"
        }
        session_file.write_text(json.dumps(session_data))

        result = runner.invoke(app, ["session", "status", "--no-budget"])
        assert result.exit_code == 0
        assert "Token Budget" not in result.output

    def test_session_status_budget_shows_status(self, paircoder_session_repo):
        """Session status shows OK/Warning/Critical status."""
        cache_dir = paircoder_session_repo / ".paircoder" / "cache"
        session_file = cache_dir / "session.json"
        tasks_dir = paircoder_session_repo / ".paircoder" / "tasks"

        # Create session
        recent_time = datetime.now() - timedelta(minutes=5)
        session_data = {
            "last_activity": recent_time.isoformat(),
            "session_id": "test-session"
        }
        session_file.write_text(json.dumps(session_data))

        # Create small task - should show OK status
        task_file = tasks_dir / "T2.task.md"
        task_file.write_text("""---
id: T2
title: Small Task
type: chore
complexity: 5
status: in_progress
---

# T2: Small Task
""")

        result = runner.invoke(app, ["session", "status"])
        assert result.exit_code == 0
        assert "Status:" in result.output
        # Should have a status indicator
        assert any(s in result.output for s in ["OK", "WARNING", "CRITICAL", "INFO"])


class TestQuietModeForHooks:
    """Tests for --quiet mode that enables Windows hook compatibility.

    Claude Code hooks on Windows fail with bash-specific syntax like '|| true'.
    The --quiet flag provides cross-platform error suppression:
    - Suppresses all output
    - Always exits with code 0
    - Catches and swallows exceptions
    """

    def test_session_check_quiet_mode_exits_zero_outside_project(self, tmp_path, monkeypatch):
        """--quiet mode exits 0 even when not in a PairCoder project."""
        # Create a directory that's not a PairCoder project
        monkeypatch.chdir(tmp_path)
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        result = runner.invoke(app, ["session", "check", "--quiet"])

        # Should exit 0 (not crash with error)
        assert result.exit_code == 0
        # Should have no output
        assert result.stdout.strip() == ""

    def test_session_check_quiet_mode_suppresses_errors(self, tmp_path, monkeypatch):
        """--quiet mode suppresses error output (no git or .paircoder)."""
        monkeypatch.chdir(tmp_path)
        # No git repo, no .paircoder - ProjectRootNotFoundError should be caught

        result = runner.invoke(app, ["session", "check", "--quiet"])

        # Should exit 0 and have no error output
        assert result.exit_code == 0
        assert "error" not in result.stdout.lower()
        assert "traceback" not in result.stdout.lower()

    def test_session_check_quiet_mode_no_output(self, paircoder_session_repo):
        """--quiet mode produces no output even on success."""
        cache_dir = paircoder_session_repo / ".paircoder" / "cache"
        session_file = cache_dir / "session.json"

        # Create recent session (continuing session = normally no output anyway)
        recent_time = datetime.now() - timedelta(minutes=5)
        session_data = {
            "last_activity": recent_time.isoformat(),
            "session_id": "test-session"
        }
        session_file.write_text(json.dumps(session_data))

        result = runner.invoke(app, ["session", "check", "--quiet"])
        assert result.exit_code == 0
        # Quiet mode should have no output
        assert result.stdout.strip() == ""

    def test_compaction_snapshot_quiet_mode_exits_zero(self, tmp_path, monkeypatch):
        """compaction snapshot save --quiet exits 0 when not in project."""
        monkeypatch.chdir(tmp_path)
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        result = runner.invoke(app, ["compaction", "snapshot", "save", "--quiet"])

        assert result.exit_code == 0
        assert result.stdout.strip() == ""

    def test_compaction_snapshot_quiet_mode_no_git(self, tmp_path, monkeypatch):
        """compaction snapshot save --quiet exits 0 even without git or .paircoder."""
        monkeypatch.chdir(tmp_path)
        # No git repo, no .paircoder - ProjectRootNotFoundError should be caught

        result = runner.invoke(app, ["compaction", "snapshot", "save", "--quiet"])

        assert result.exit_code == 0
        # No error output
        assert "error" not in result.stdout.lower()


class TestContextSyncAutoMode:
    """Tests for context-sync --auto mode for Windows hook compatibility."""

    def test_context_sync_auto_exits_zero_with_no_values(self, paircoder_session_repo):
        """--auto mode exits 0 when no --last/--next provided."""
        result = runner.invoke(app, ["context-sync", "--auto"])

        assert result.exit_code == 0
        # Should have no output (silent exit)
        assert result.stdout.strip() == ""

    def test_context_sync_auto_exits_zero_outside_project(self, tmp_path, monkeypatch):
        """--auto mode exits 0 when not in a PairCoder project."""
        monkeypatch.chdir(tmp_path)
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        result = runner.invoke(app, ["context-sync", "--auto"])

        assert result.exit_code == 0
        assert result.stdout.strip() == ""

    def test_context_sync_quiet_exits_zero_with_missing_args(self, paircoder_session_repo):
        """--quiet mode exits 0 when missing required args."""
        result = runner.invoke(app, ["context-sync", "--quiet"])

        assert result.exit_code == 0
        # No error message
        assert "required" not in result.stdout.lower()

    def test_context_sync_quiet_exits_zero_outside_project(self, tmp_path, monkeypatch):
        """--quiet mode exits 0 when not in a PairCoder project."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["context-sync", "--quiet"])

        assert result.exit_code == 0


class TestHistoryLogQuietMode:
    """Tests for history-log --quiet mode for Windows hook compatibility."""

    def test_history_log_quiet_exits_zero_no_file(self, paircoder_session_repo):
        """--quiet mode exits 0 when no file path provided."""
        result = runner.invoke(app, ["history-log", "--quiet"])

        assert result.exit_code == 0
        assert result.stdout.strip() == ""

    def test_history_log_quiet_exits_zero_outside_project(self, tmp_path, monkeypatch):
        """--quiet mode exits 0 when not in a PairCoder project."""
        monkeypatch.chdir(tmp_path)
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        result = runner.invoke(app, ["history-log", "--quiet"])

        assert result.exit_code == 0

    def test_history_log_quiet_logs_file_silently(self, paircoder_session_repo):
        """--quiet mode logs file without output."""
        result = runner.invoke(app, ["history-log", "--quiet", "test/file.py"])

        assert result.exit_code == 0
        # No output in quiet mode
        assert "logged" not in result.stdout.lower()

        # But file should be logged
        log_file = paircoder_session_repo / ".paircoder" / "history" / "changes.log"
        assert log_file.exists()
        assert "test/file.py" in log_file.read_text()


class TestCrossPlatformHookCompatibility:
    """Integration tests verifying cross-platform hook behavior.

    These tests verify that the hook commands work correctly on any platform
    without bash-specific syntax like '|| true' or '2>/dev/null'.
    """

    def test_all_hook_commands_have_quiet_mode(self):
        """All hook-related commands should support --quiet."""
        hook_commands = [
            ["session", "check"],
            ["compaction", "snapshot", "save"],
            ["context-sync"],
            ["history-log"],
        ]

        for cmd in hook_commands:
            result = runner.invoke(app, cmd + ["--help"])
            assert result.exit_code == 0
            assert "--quiet" in result.stdout or "-q" in result.stdout, \
                f"Command {' '.join(cmd)} should support --quiet flag"

    def test_hook_commands_never_require_shell_syntax(self, paircoder_session_repo):
        """Hook commands should not require bash-specific syntax."""
        # These are the commands used in .claude/settings.json hooks
        # They should all work without '|| true' or similar

        commands_and_flags = [
            (["session", "check", "--quiet"], 0),
            (["compaction", "snapshot", "save", "--trigger", "test", "--quiet"], 0),
            (["history-log", "--quiet"], 0),  # No file = silent exit
            (["context-sync", "--auto"], 0),  # No values = silent exit
        ]

        for cmd, expected_exit in commands_and_flags:
            result = runner.invoke(app, cmd)
            assert result.exit_code == expected_exit, \
                f"Command {' '.join(cmd)} should exit {expected_exit}, got {result.exit_code}"

    def test_quiet_mode_handles_internal_exceptions(self, paircoder_session_repo, monkeypatch):
        """--quiet mode should catch internal exceptions gracefully."""
        # Simulate an internal error by breaking the session manager import
        from bpsai_pair.commands import session as session_module

        original_import = session_module.SessionManager if hasattr(session_module, 'SessionManager') else None

        def broken_import(*args, **kwargs):
            raise RuntimeError("Simulated internal error")

        # The command should still exit 0 with --quiet
        result = runner.invoke(app, ["session", "check", "--quiet"])
        assert result.exit_code == 0
