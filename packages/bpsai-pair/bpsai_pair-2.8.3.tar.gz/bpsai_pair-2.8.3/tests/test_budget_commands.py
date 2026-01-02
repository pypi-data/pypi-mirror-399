"""Tests for budget CLI commands."""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from bpsai_pair.cli import app


runner = CliRunner()


class TestBudgetEstimate:
    """Tests for budget estimate command."""

    def test_estimate_help(self):
        """Estimate command has help."""
        result = runner.invoke(app, ["budget", "estimate", "--help"])
        assert result.exit_code == 0
        assert "Estimate token usage" in result.output

    def test_estimate_no_args_shows_usage(self):
        """Estimate without args shows usage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up a git repo
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()

            with patch("bpsai_pair.commands.budget.ops.find_project_root", return_value=Path(tmpdir)):
                with patch("bpsai_pair.commands.budget.ops.GitOps.is_repo", return_value=True):
                    result = runner.invoke(app, ["budget", "estimate"])
                    assert result.exit_code == 1
                    assert "Please provide a task ID or files" in result.output

    def test_estimate_task_not_found(self):
        """Estimate with nonexistent task shows error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            paircoder_dir = Path(tmpdir) / ".paircoder" / "tasks"
            paircoder_dir.mkdir(parents=True)

            with patch("bpsai_pair.commands.budget.ops.find_project_root", return_value=Path(tmpdir)):
                with patch("bpsai_pair.commands.budget.ops.GitOps.is_repo", return_value=True):
                    result = runner.invoke(app, ["budget", "estimate", "NONEXISTENT"])
                    assert result.exit_code == 2
                    assert "not found" in result.output.lower()

    def test_estimate_task_shows_breakdown(self):
        """Estimate with valid task shows breakdown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            paircoder_dir = Path(tmpdir) / ".paircoder" / "tasks"
            paircoder_dir.mkdir(parents=True)

            # Create a task file
            task_file = paircoder_dir / "T1.task.md"
            task_file.write_text("""---
id: T1
title: Test Task
type: feature
complexity: 10
---

# T1: Test Task

## Objective

Test objective.
""")

            with patch("bpsai_pair.commands.budget.ops.find_project_root", return_value=Path(tmpdir)):
                with patch("bpsai_pair.commands.budget.ops.GitOps.is_repo", return_value=True):
                    result = runner.invoke(app, ["budget", "estimate", "T1"])
                    assert result.exit_code == 0
                    assert "Token Breakdown" in result.output
                    assert "Base context" in result.output
                    assert "Total" in result.output

    def test_estimate_json_output(self):
        """Estimate with --json outputs valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            paircoder_dir = Path(tmpdir) / ".paircoder" / "tasks"
            paircoder_dir.mkdir(parents=True)

            task_file = paircoder_dir / "T1.task.md"
            task_file.write_text("""---
id: T1
title: Test Task
type: feature
complexity: 10
---

# T1: Test Task
""")

            with patch("bpsai_pair.commands.budget.ops.find_project_root", return_value=Path(tmpdir)):
                with patch("bpsai_pair.commands.budget.ops.GitOps.is_repo", return_value=True):
                    result = runner.invoke(app, ["budget", "estimate", "T1", "--json"])
                    assert result.exit_code == 0
                    data = json.loads(result.output)
                    assert "task_id" in data
                    assert "breakdown" in data
                    assert "budget" in data

    def test_estimate_files(self):
        """Estimate with -f flag estimates specific files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()

            # Create test files
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('hello world')")

            with patch("bpsai_pair.commands.budget.ops.find_project_root", return_value=Path(tmpdir)):
                with patch("bpsai_pair.commands.budget.ops.GitOps.is_repo", return_value=True):
                    result = runner.invoke(app, ["budget", "estimate", "-f", "test.py"])
                    assert result.exit_code == 0
                    assert "File Token Estimate" in result.output
                    assert "test.py" in result.output


class TestBudgetStatus:
    """Tests for budget status command."""

    def test_status_help(self):
        """Status command has help."""
        result = runner.invoke(app, ["budget", "status", "--help"])
        assert result.exit_code == 0
        assert "budget status" in result.output.lower()

    def test_status_shows_thresholds(self):
        """Status shows model and thresholds."""
        result = runner.invoke(app, ["budget", "status"])
        assert result.exit_code == 0
        assert "Budget Status" in result.output
        assert "Context limit" in result.output
        assert "Thresholds" in result.output

    def test_status_json_output(self):
        """Status with --json outputs valid JSON."""
        result = runner.invoke(app, ["budget", "status", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "model" in data
        assert "limit" in data
        assert "thresholds" in data

    def test_status_different_model(self):
        """Status with different model shows correct limit."""
        result = runner.invoke(app, ["budget", "status", "--model", "claude-opus-4-5", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["model"] == "claude-opus-4-5"


class TestBudgetCheck:
    """Tests for budget check command."""

    def test_check_help(self):
        """Check command has help."""
        result = runner.invoke(app, ["budget", "check", "--help"])
        assert result.exit_code == 0
        assert "Pre-flight" in result.output

    def test_check_task_not_found(self):
        """Check with nonexistent task exits 2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            paircoder_dir = Path(tmpdir) / ".paircoder" / "tasks"
            paircoder_dir.mkdir(parents=True)

            with patch("bpsai_pair.commands.budget.ops.find_project_root", return_value=Path(tmpdir)):
                with patch("bpsai_pair.commands.budget.ops.GitOps.is_repo", return_value=True):
                    result = runner.invoke(app, ["budget", "check", "NONEXISTENT"])
                    assert result.exit_code == 2

    def test_check_under_threshold(self):
        """Check under threshold exits 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            paircoder_dir = Path(tmpdir) / ".paircoder" / "tasks"
            paircoder_dir.mkdir(parents=True)

            task_file = paircoder_dir / "T1.task.md"
            task_file.write_text("""---
id: T1
title: Test Task
type: chore
complexity: 5
---

# T1: Small Task
""")

            with patch("bpsai_pair.commands.budget.ops.find_project_root", return_value=Path(tmpdir)):
                with patch("bpsai_pair.commands.budget.ops.GitOps.is_repo", return_value=True):
                    result = runner.invoke(app, ["budget", "check", "T1", "--threshold", "50"])
                    assert result.exit_code == 0
                    assert "OK" in result.output

    def test_check_over_threshold(self):
        """Check over threshold exits 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            paircoder_dir = Path(tmpdir) / ".paircoder" / "tasks"
            paircoder_dir.mkdir(parents=True)

            task_file = paircoder_dir / "T1.task.md"
            task_file.write_text("""---
id: T1
title: Test Task
type: feature
complexity: 5
---

# T1: Small Task
""")

            with patch("bpsai_pair.commands.budget.ops.find_project_root", return_value=Path(tmpdir)):
                with patch("bpsai_pair.commands.budget.ops.GitOps.is_repo", return_value=True):
                    # Use threshold of 1% which should be exceeded by base context alone
                    result = runner.invoke(app, ["budget", "check", "T1", "--threshold", "1"])
                    assert result.exit_code == 1
                    assert "OVER THRESHOLD" in result.output

    def test_check_json_output(self):
        """Check with --json outputs valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            paircoder_dir = Path(tmpdir) / ".paircoder" / "tasks"
            paircoder_dir.mkdir(parents=True)

            task_file = paircoder_dir / "T1.task.md"
            task_file.write_text("""---
id: T1
title: Test Task
type: chore
complexity: 5
---

# T1: Small Task
""")

            with patch("bpsai_pair.commands.budget.ops.find_project_root", return_value=Path(tmpdir)):
                with patch("bpsai_pair.commands.budget.ops.GitOps.is_repo", return_value=True):
                    result = runner.invoke(app, ["budget", "check", "T1", "--json"])
                    # Parse JSON ignoring exit code
                    data = json.loads(result.output)
                    assert "task_id" in data
                    assert "estimated_tokens" in data
                    assert "threshold" in data
                    assert "over_threshold" in data
                    assert "exit_code" in data
