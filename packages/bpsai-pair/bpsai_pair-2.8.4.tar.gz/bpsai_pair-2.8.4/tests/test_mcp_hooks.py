"""
Tests for Hook System

Tests HookRunner and hook execution.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import fixtures
pytest_plugins = ["tests.conftest_mcp"]


class TestHookRunner:
    """Tests for the HookRunner class."""

    def test_hook_runner_initializes(self, mcp_paircoder_dir):
        """HookRunner initializes correctly."""
        from bpsai_pair.core.hooks import HookRunner

        config = {
            "hooks": {
                "enabled": True,
                "on_task_start": ["update_state"],
            }
        }

        runner = HookRunner(config, mcp_paircoder_dir)

        assert runner.enabled
        assert runner.get_hooks_for_event("on_task_start") == ["update_state"]

    def test_hook_runner_disabled(self, mcp_paircoder_dir):
        """HookRunner respects enabled=False."""
        from bpsai_pair.core.hooks import HookRunner, HookContext

        config = {
            "hooks": {
                "enabled": False,
                "on_task_start": ["update_state"],
            }
        }

        runner = HookRunner(config, mcp_paircoder_dir)

        mock_task = MagicMock()
        ctx = HookContext(task_id="TASK-001", task=mock_task, event="on_task_start")

        results = runner.run_hooks("on_task_start", ctx)

        assert results == []

    def test_hook_runner_runs_configured_hooks(self, mcp_paircoder_dir, sample_task_file, sample_plan_file):
        """HookRunner executes configured hooks."""
        from bpsai_pair.core.hooks import HookRunner, HookContext
        from bpsai_pair.planning.parser import TaskParser

        config = {
            "hooks": {
                "enabled": True,
                "on_task_start": ["update_state"],
            }
        }

        runner = HookRunner(config, mcp_paircoder_dir)

        # Get real task
        parser = TaskParser(mcp_paircoder_dir / "tasks")
        task = parser.get_task_by_id("TASK-001")

        ctx = HookContext(task_id="TASK-001", task=task, event="on_task_start")
        results = runner.run_hooks("on_task_start", ctx)

        assert len(results) == 1
        assert results[0].hook == "update_state"
        assert results[0].success is True

    def test_hook_unknown_hook_fails_gracefully(self, mcp_paircoder_dir):
        """Unknown hooks are handled gracefully."""
        from bpsai_pair.core.hooks import HookRunner, HookContext

        config = {
            "hooks": {
                "enabled": True,
                "on_task_start": ["nonexistent_hook"],
            }
        }

        runner = HookRunner(config, mcp_paircoder_dir)

        mock_task = MagicMock()
        ctx = HookContext(task_id="TASK-001", task=mock_task, event="on_task_start")

        results = runner.run_hooks("on_task_start", ctx)

        assert len(results) == 1
        assert results[0].hook == "nonexistent_hook"
        assert results[0].success is False
        assert "Unknown hook" in results[0].error

    def test_hook_on_task_complete_runs_update_state(self, mcp_paircoder_dir, sample_task_file, sample_plan_file):
        """on_task_complete event runs configured hooks."""
        from bpsai_pair.core.hooks import HookRunner, HookContext
        from bpsai_pair.planning.parser import TaskParser

        config = {
            "hooks": {
                "enabled": True,
                "on_task_complete": ["update_state"],
            }
        }

        runner = HookRunner(config, mcp_paircoder_dir)

        parser = TaskParser(mcp_paircoder_dir / "tasks")
        task = parser.get_task_by_id("TASK-001")

        ctx = HookContext(task_id="TASK-001", task=task, event="on_task_complete")
        results = runner.run_hooks("on_task_complete", ctx)

        assert len(results) == 1
        assert results[0].hook == "update_state"
        assert results[0].success is True


class TestHookContext:
    """Tests for HookContext dataclass."""

    def test_hook_context_creation(self):
        """HookContext can be created with required fields."""
        from bpsai_pair.core.hooks import HookContext

        mock_task = MagicMock()
        ctx = HookContext(
            task_id="TASK-001",
            task=mock_task,
            event="on_task_start",
        )

        assert ctx.task_id == "TASK-001"
        assert ctx.event == "on_task_start"
        assert ctx.agent is None
        assert ctx.extra == {}

    def test_hook_context_with_extra(self):
        """HookContext can include extra data."""
        from bpsai_pair.core.hooks import HookContext

        mock_task = MagicMock()
        ctx = HookContext(
            task_id="TASK-001",
            task=mock_task,
            event="on_task_complete",
            agent="claude-code",
            extra={
                "input_tokens": 1000,
                "output_tokens": 500,
            },
        )

        assert ctx.agent == "claude-code"
        assert ctx.extra["input_tokens"] == 1000


class TestHookResult:
    """Tests for HookResult dataclass."""

    def test_hook_result_to_dict(self):
        """HookResult.to_dict() returns correct format."""
        from bpsai_pair.core.hooks import HookResult

        result = HookResult(
            hook="update_state",
            success=True,
            result={"state_updated": True},
        )

        d = result.to_dict()

        assert d["hook"] == "update_state"
        assert d["success"] is True
        assert d["result"] == {"state_updated": True}
        assert "error" not in d

    def test_hook_result_error_to_dict(self):
        """HookResult.to_dict() includes error when failed."""
        from bpsai_pair.core.hooks import HookResult

        result = HookResult(
            hook="bad_hook",
            success=False,
            error="Something went wrong",
        )

        d = result.to_dict()

        assert d["hook"] == "bad_hook"
        assert d["success"] is False
        assert d["error"] == "Something went wrong"
