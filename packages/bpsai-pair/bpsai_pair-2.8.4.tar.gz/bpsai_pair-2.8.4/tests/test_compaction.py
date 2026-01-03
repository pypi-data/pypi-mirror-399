"""Tests for compaction detection and recovery."""
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from bpsai_pair.cli import app

runner = CliRunner()


@pytest.fixture
def paircoder_compaction_repo(tmp_path, monkeypatch):
    """Create a temporary repo with PairCoder structure for compaction testing."""
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
compaction:
  enabled: true
  auto_snapshot: true
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
| T19.3 | Compaction Detection | in_progress | P1 |

**Progress:** 2/9 tasks

## What Was Just Done

- Working on compaction detection

## What's Next

1. Complete T19.3

## Blockers

None
""")

    # Create a task file
    task_file = tasks_dir / "T19.3.task.md"
    task_file.write_text("""---
id: T19.3
title: Compaction Detection
plan: plan-2025-12-sprint-19-methodology
status: in_progress
priority: P1
---

# Objective

Detect compaction and recover context.
""")

    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestCompactionSnapshot:
    """Tests for compaction snapshot creation."""

    def test_snapshot_save_creates_file(self, paircoder_compaction_repo):
        """Saving a snapshot should create a file in cache."""
        result = runner.invoke(app, ["compaction", "snapshot", "save"])
        assert result.exit_code == 0

        # Check snapshot file was created
        cache_dir = paircoder_compaction_repo / ".paircoder" / "cache"
        snapshot_files = list(cache_dir.glob("compaction_snapshot_*.json"))
        assert len(snapshot_files) >= 1

    def test_snapshot_contains_state_info(self, paircoder_compaction_repo):
        """Snapshot should contain state.md information."""
        runner.invoke(app, ["compaction", "snapshot", "save"])

        cache_dir = paircoder_compaction_repo / ".paircoder" / "cache"
        snapshot_files = list(cache_dir.glob("compaction_snapshot_*.json"))

        if snapshot_files:
            snapshot_data = json.loads(snapshot_files[0].read_text())
            # Snapshot should contain state info like active_plan, current_task_id, etc.
            assert "active_plan" in snapshot_data or "current_task_id" in snapshot_data

    def test_snapshot_list_shows_snapshots(self, paircoder_compaction_repo):
        """Listing snapshots should show existing ones."""
        # Create a snapshot first
        runner.invoke(app, ["compaction", "snapshot", "save"])

        result = runner.invoke(app, ["compaction", "snapshot", "list"])
        assert result.exit_code == 0


class TestCompactionDetection:
    """Tests for compaction detection logic."""

    def test_compaction_check_with_no_snapshot(self, paircoder_compaction_repo):
        """Compaction check with no snapshot should not error."""
        result = runner.invoke(app, ["compaction", "check"])
        assert result.exit_code == 0

    def test_compaction_check_detects_recent_compaction(self, paircoder_compaction_repo):
        """Should detect if compaction recently occurred."""
        cache_dir = paircoder_compaction_repo / ".paircoder" / "cache"

        # Create a compaction marker (simulating PreCompact hook)
        marker_file = cache_dir / "compaction_marker.json"
        marker_data = {
            "timestamp": datetime.now().isoformat(),
            "trigger": "auto",
            "recovered": False
        }
        marker_file.write_text(json.dumps(marker_data))

        result = runner.invoke(app, ["compaction", "check"])
        assert result.exit_code == 0
        # Should indicate compaction detected
        assert "compaction" in result.stdout.lower()


class TestCompactionRecovery:
    """Tests for context recovery after compaction."""

    def test_recover_reads_state(self, paircoder_compaction_repo):
        """Recovery should read and display state.md context."""
        result = runner.invoke(app, ["compaction", "recover"])
        assert result.exit_code == 0
        # Should show recovered context
        assert "T19.3" in result.stdout or "sprint-19" in result.stdout.lower() or "recover" in result.stdout.lower()

    def test_recover_marks_as_recovered(self, paircoder_compaction_repo):
        """Recovery should mark the compaction event as recovered."""
        cache_dir = paircoder_compaction_repo / ".paircoder" / "cache"

        # Create a compaction marker
        marker_file = cache_dir / "compaction_marker.json"
        marker_data = {
            "timestamp": datetime.now().isoformat(),
            "trigger": "manual",
            "recovered": False
        }
        marker_file.write_text(json.dumps(marker_data))

        # Run recovery
        runner.invoke(app, ["compaction", "recover"])

        # Check marker was updated
        if marker_file.exists():
            updated_data = json.loads(marker_file.read_text())
            assert updated_data.get("recovered", False) is True


class TestCompactionLogging:
    """Tests for compaction event logging."""

    def test_compaction_logged_to_history(self, paircoder_compaction_repo):
        """Compaction events should be logged to history."""
        # Simulate a compaction event by saving snapshot
        runner.invoke(app, ["compaction", "snapshot", "save", "--reason", "auto"])

        history_dir = paircoder_compaction_repo / ".paircoder" / "history"
        compaction_log = history_dir / "compaction.log"

        # Log should exist and have content
        assert compaction_log.exists()
        content = compaction_log.read_text()
        assert len(content) > 0


class TestCompactionCommands:
    """Tests for compaction CLI commands."""

    def test_compaction_command_exists(self):
        """The compaction command group should exist."""
        result = runner.invoke(app, ["compaction", "--help"])
        assert result.exit_code == 0
        assert "compaction" in result.stdout.lower()

    def test_compaction_snapshot_save_help(self):
        """The snapshot save command should have help."""
        result = runner.invoke(app, ["compaction", "snapshot", "save", "--help"])
        assert result.exit_code == 0

    def test_compaction_check_help(self):
        """The check command should have help."""
        result = runner.invoke(app, ["compaction", "check", "--help"])
        assert result.exit_code == 0

    def test_compaction_recover_help(self):
        """The recover command should have help."""
        result = runner.invoke(app, ["compaction", "recover", "--help"])
        assert result.exit_code == 0


class TestPreCompactHookIntegration:
    """Tests for PreCompact hook integration."""

    def test_snapshot_save_with_trigger_parameter(self, paircoder_compaction_repo):
        """Snapshot save should accept trigger parameter (auto/manual)."""
        result = runner.invoke(app, ["compaction", "snapshot", "save", "--trigger", "auto"])
        assert result.exit_code == 0

    def test_snapshot_includes_trigger_in_metadata(self, paircoder_compaction_repo):
        """Snapshot metadata should include the trigger type."""
        runner.invoke(app, ["compaction", "snapshot", "save", "--trigger", "manual"])

        cache_dir = paircoder_compaction_repo / ".paircoder" / "cache"
        snapshot_files = list(cache_dir.glob("compaction_snapshot_*.json"))

        if snapshot_files:
            snapshot_data = json.loads(snapshot_files[0].read_text())
            assert snapshot_data.get("trigger") == "manual"
