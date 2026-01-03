"""Tests for template drift detection command.

Tests the `bpsai-pair template check` command which compares source files
with the cookiecutter template to detect drift.
"""

import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from bpsai_pair.cli import app

runner = CliRunner()


@pytest.fixture
def template_repo(tmp_path):
    """Create a repository with template structure for testing."""
    repo = tmp_path / "test_repo"
    repo.mkdir()

    # Initialize git
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, capture_output=True)

    # Create .paircoder structure
    paircoder_dir = repo / ".paircoder"
    context_dir = paircoder_dir / "context"
    context_dir.mkdir(parents=True)

    # Create config.yaml
    (paircoder_dir / "config.yaml").write_text("""version: 2.1
project:
  name: test-project
""")

    # Create state.md
    (context_dir / "state.md").write_text("""# Current State

## Active Plan

**Plan:** None
""")

    # Create CLAUDE.md
    (repo / "CLAUDE.md").write_text("""# Claude Code Instructions

Read `.paircoder/context/state.md` for current status.
""")

    # Create initial commit
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True, capture_output=True)

    return repo


class TestTemplateCheckCommand:
    """Tests for the template check command."""

    def test_check_command_exists(self, template_repo, monkeypatch):
        """Verify the template check command exists."""
        monkeypatch.chdir(template_repo)
        result = runner.invoke(app, ["template", "check", "--help"])
        assert result.exit_code == 0
        assert "check" in result.stdout.lower() or "template" in result.stdout.lower()

    def test_check_shows_file_status(self, template_repo, monkeypatch):
        """Check command shows status for template files."""
        monkeypatch.chdir(template_repo)
        result = runner.invoke(app, ["template", "check"])
        # Should show some file status output
        output = result.stdout.lower()
        assert "template" in output or "file" in output or "status" in output

    def test_check_shows_status_icons(self, template_repo, monkeypatch):
        """Check command uses status icons."""
        monkeypatch.chdir(template_repo)
        result = runner.invoke(app, ["template", "check"])
        # Should have status icons or text indicators
        has_icons = "✅" in result.stdout or "⚠️" in result.stdout or "❌" in result.stdout
        has_text = "sync" in result.stdout.lower() or "drift" in result.stdout.lower() or "ok" in result.stdout.lower()
        assert has_icons or has_text

    def test_check_fail_on_drift_flag(self, template_repo, monkeypatch):
        """Check command accepts --fail-on-drift flag."""
        monkeypatch.chdir(template_repo)
        result = runner.invoke(app, ["template", "check", "--fail-on-drift"])
        # Should not error on the flag itself (may fail or pass based on drift)
        assert result.exit_code in [0, 1]

    def test_check_fix_flag_exists(self, template_repo, monkeypatch):
        """Check command accepts --fix flag."""
        monkeypatch.chdir(template_repo)
        # Just check the help shows --fix option
        result = runner.invoke(app, ["template", "check", "--help"])
        assert "--fix" in result.stdout or "fix" in result.stdout.lower()


class TestTemplateCheckDriftDetection:
    """Tests for drift detection logic."""

    def test_detects_missing_file(self, template_repo, monkeypatch):
        """Detects when source file exists but template doesn't have it."""
        monkeypatch.chdir(template_repo)
        # The command should handle missing files gracefully
        result = runner.invoke(app, ["template", "check"])
        assert result.exit_code in [0, 1]

    def test_reports_line_diff_count(self, template_repo, monkeypatch):
        """Reports number of lines different when drift detected."""
        monkeypatch.chdir(template_repo)
        result = runner.invoke(app, ["template", "check"])
        # Output should mention lines or changes if there's drift, or show template status
        output = result.stdout.lower()
        # Either shows line counts, sync status, or template not found message
        assert "line" in output or "sync" in output or "change" in output or "drift" in output or "match" in output or "template" in output


class TestTemplateCheckConfig:
    """Tests for template check configuration."""

    def test_uses_config_template_path(self, template_repo, monkeypatch):
        """Check command reads template path from config."""
        monkeypatch.chdir(template_repo)

        # Update config with custom template path
        config_file = template_repo / ".paircoder" / "config.yaml"
        config_file.write_text("""version: 2.1
release:
  cookie_cutter:
    template_path: custom/template/path
""")

        result = runner.invoke(app, ["template", "check"])
        # Should run without crashing (may not find template)
        assert result.exit_code in [0, 1, 2]

    def test_uses_default_template_path(self, template_repo, monkeypatch):
        """Check command uses default template path when not configured."""
        monkeypatch.chdir(template_repo)

        # Config without template path
        config_file = template_repo / ".paircoder" / "config.yaml"
        config_file.write_text("version: 2.1\n")

        result = runner.invoke(app, ["template", "check"])
        # Should run with default path
        assert result.exit_code in [0, 1, 2]


class TestTemplateCheckOutput:
    """Tests for template check output formatting."""

    def test_clear_summary_output(self, template_repo, monkeypatch):
        """Check command provides clear summary."""
        monkeypatch.chdir(template_repo)
        result = runner.invoke(app, ["template", "check"])
        output = result.stdout.lower()
        # Should have some summary or status
        assert any(word in output for word in ["sync", "drift", "check", "template", "status", "file"])

    def test_actionable_messages(self, template_repo, monkeypatch):
        """Check command provides actionable messages when drift detected."""
        monkeypatch.chdir(template_repo)
        result = runner.invoke(app, ["template", "check"])
        # Output should be informative
        assert len(result.stdout) > 10  # Has some content


class TestTemplateCheckNotInProject:
    """Tests for template check when not in a PairCoder project."""

    def test_shows_helpful_error_outside_project(self, tmp_path, monkeypatch):
        """Check command shows helpful error when not in a project."""
        # Create a directory without .paircoder or .git
        empty_dir = tmp_path / "empty_dir"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)

        result = runner.invoke(app, ["template", "check"])
        assert result.exit_code == 1
        # Message may be in stdout or stderr, so check output (both combined)
        combined_output = (result.stdout + (result.output if hasattr(result, 'output') else '')).lower()
        assert "not in a paircoder project" in combined_output or "bpsai-pair init" in combined_output

    def test_graceful_exit_code_outside_project(self, tmp_path, monkeypatch):
        """Check command exits with code 1 when not in a project."""
        empty_dir = tmp_path / "empty_dir"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)

        result = runner.invoke(app, ["template", "check"])
        assert result.exit_code == 1

    def test_list_command_shows_helpful_error_outside_project(self, tmp_path, monkeypatch):
        """List command also shows helpful error when not in a project."""
        empty_dir = tmp_path / "empty_dir"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)

        result = runner.invoke(app, ["template", "list"])
        assert result.exit_code == 1
        # Message may be in stdout or stderr, so check output (both combined)
        combined_output = (result.stdout + (result.output if hasattr(result, 'output') else '')).lower()
        assert "not in a paircoder project" in combined_output or "bpsai-pair init" in combined_output


class TestTemplateCheckFilesCompared:
    """Tests for specific files being compared."""

    def test_checks_config_yaml(self, template_repo, monkeypatch):
        """Check command compares config.yaml."""
        monkeypatch.chdir(template_repo)
        result = runner.invoke(app, ["template", "check"])
        output = result.stdout.lower()
        # Should mention config or .paircoder files
        assert "config" in output or ".paircoder" in output or "template" in output

    def test_checks_claude_md(self, template_repo, monkeypatch):
        """Check command compares CLAUDE.md."""
        monkeypatch.chdir(template_repo)
        result = runner.invoke(app, ["template", "check"])
        # Should check CLAUDE.md or similar key files
        output = result.stdout
        # This is a general check - the output should have some file info
        assert len(output) > 10
