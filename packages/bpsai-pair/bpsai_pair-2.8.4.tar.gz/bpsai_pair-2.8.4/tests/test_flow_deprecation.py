"""Tests for flow command deprecation warnings."""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from bpsai_pair.cli import app
from bpsai_pair.core.deprecation import (
    deprecated_command,
    suppress_deprecation_warnings,
    is_warnings_suppressed,
    show_migration_hint_once,
)


runner = CliRunner()


@pytest.fixture
def temp_dir_with_flows(tmp_path, monkeypatch):
    """Create a temporary directory with sample flows."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()
    flows_dir = tmp_path / ".paircoder" / "flows"
    flows_dir.mkdir(parents=True)

    (flows_dir / "test-flow.flow.md").write_text("""---
name: test-flow
description: A test flow
version: 1
---

# Test Flow
Test content.
""")
    return tmp_path


@pytest.fixture(autouse=True)
def reset_deprecation_state():
    """Reset deprecation warning state before each test."""
    suppress_deprecation_warnings(False)
    yield
    suppress_deprecation_warnings(False)


class TestDeprecationDecorator:
    """Tests for the deprecated_command decorator."""

    def test_deprecated_decorator_emits_warning(self, temp_dir_with_flows):
        """Deprecated command emits warning."""
        result = runner.invoke(app, ["flow", "list"])

        assert "DEPRECATED" in result.output
        assert "Flows are deprecated" in result.output

    def test_deprecated_decorator_shows_alternative(self, temp_dir_with_flows):
        """Deprecated command shows alternative in warning."""
        result = runner.invoke(app, ["flow", "list"])

        assert "Use instead: bpsai-pair skill list" in result.output

    def test_deprecated_decorator_shows_removal_version(self, temp_dir_with_flows):
        """Deprecated command shows removal version."""
        result = runner.invoke(app, ["flow", "list"])

        assert "2.11.0" in result.output

    def test_no_deprecation_warnings_flag_suppresses(self, temp_dir_with_flows):
        """--no-deprecation-warnings suppresses deprecation warnings."""
        result = runner.invoke(app, ["flow", "--no-deprecation-warnings", "list"])

        # Should not have deprecation warning
        assert "DEPRECATED" not in result.output

    def test_command_still_works_with_deprecation(self, temp_dir_with_flows):
        """Deprecated command still executes successfully."""
        result = runner.invoke(app, ["flow", "list"])

        assert result.exit_code == 0
        assert "test-flow" in result.output


class TestFlowListDeprecation:
    """Tests for 'flow list' deprecation."""

    def test_flow_list_deprecation_warning(self, temp_dir_with_flows):
        """flow list shows deprecation warning."""
        result = runner.invoke(app, ["flow", "list"])

        assert result.exit_code == 0
        assert "DEPRECATED" in result.output
        assert "skill list" in result.output

    def test_flow_list_help_shows_deprecated(self):
        """flow list help text indicates deprecation."""
        result = runner.invoke(app, ["flow", "list", "--help"])

        assert result.exit_code == 0
        assert "DEPRECATED" in result.output


class TestFlowShowDeprecation:
    """Tests for 'flow show' deprecation."""

    def test_flow_show_deprecation_warning(self, temp_dir_with_flows):
        """flow show shows deprecation warning."""
        result = runner.invoke(app, ["flow", "show", "test-flow"])

        assert result.exit_code == 0
        assert "DEPRECATED" in result.output
        assert "skill show" in result.output

    def test_flow_show_help_shows_deprecated(self):
        """flow show help text indicates deprecation."""
        result = runner.invoke(app, ["flow", "show", "--help"])

        assert result.exit_code == 0
        assert "DEPRECATED" in result.output


class TestFlowRunDeprecation:
    """Tests for 'flow run' deprecation."""

    def test_flow_run_deprecation_warning(self, temp_dir_with_flows):
        """flow run shows deprecation warning."""
        result = runner.invoke(app, ["flow", "run", "test-flow"])

        assert result.exit_code == 0
        assert "DEPRECATED" in result.output
        assert "auto" in result.output.lower()  # "skills auto-invoke"

    def test_flow_run_help_shows_deprecated(self):
        """flow run help text indicates deprecation."""
        result = runner.invoke(app, ["flow", "run", "--help"])

        assert result.exit_code == 0
        assert "DEPRECATED" in result.output


class TestFlowValidateDeprecation:
    """Tests for 'flow validate' deprecation."""

    def test_flow_validate_deprecation_warning(self, temp_dir_with_flows):
        """flow validate shows deprecation warning."""
        result = runner.invoke(app, ["flow", "validate", "test-flow"])

        assert result.exit_code == 0
        assert "DEPRECATED" in result.output
        assert "skill validate" in result.output

    def test_flow_validate_help_shows_deprecated(self):
        """flow validate help text indicates deprecation."""
        result = runner.invoke(app, ["flow", "validate", "--help"])

        assert result.exit_code == 0
        assert "DEPRECATED" in result.output


class TestFlowHelpDeprecation:
    """Tests for flow command group help."""

    def test_flow_help_shows_deprecated(self):
        """flow --help indicates deprecation."""
        result = runner.invoke(app, ["flow", "--help"])

        assert result.exit_code == 0
        assert "DEPRECATED" in result.output

    def test_flow_help_shows_no_deprecation_warnings_option(self):
        """flow --help shows --no-deprecation-warnings option."""
        result = runner.invoke(app, ["flow", "--help"])

        assert result.exit_code == 0
        assert "--no-deprecation-warnings" in result.output


class TestMigrationHint:
    """Tests for migration hint functionality."""

    def test_migration_hint_content_in_output(self, temp_dir_with_flows, tmp_path):
        """Migration hint appears in output on first flow command."""
        # Clear any cached hints
        cache_file = Path.home() / ".cache" / "paircoder" / "deprecation_hint_flows_to_skills"
        if cache_file.exists():
            cache_file.unlink()

        result = runner.invoke(app, ["flow", "list"])

        # Migration hint should be in output
        assert "migrate" in result.output.lower() or "skills" in result.output.lower()


class TestDeprecationUtilities:
    """Tests for deprecation utility functions."""

    def test_suppress_deprecation_warnings(self):
        """suppress_deprecation_warnings sets global flag."""
        assert not is_warnings_suppressed()

        suppress_deprecation_warnings(True)
        assert is_warnings_suppressed()

        suppress_deprecation_warnings(False)
        assert not is_warnings_suppressed()

    def test_show_migration_hint_respects_suppression(self, tmp_path):
        """show_migration_hint_once respects suppression flag."""
        suppress_deprecation_warnings(True)

        # Should return False when suppressed
        result = show_migration_hint_once("test_hint")
        assert result is False


class TestDeprecationWithJsonOutput:
    """Tests for deprecation warnings with JSON output."""

    def test_json_output_still_works(self, temp_dir_with_flows):
        """JSON output still works with deprecation warning present."""
        result = runner.invoke(app, ["flow", "list", "--json"])

        assert result.exit_code == 0
        # Both deprecation and JSON in output
        assert "DEPRECATED" in result.output
        assert '"flows"' in result.output

    def test_no_deprecation_warnings_clean_json(self, temp_dir_with_flows):
        """--no-deprecation-warnings gives clean JSON output."""
        result = runner.invoke(app, ["flow", "--no-deprecation-warnings", "list", "--json"])

        assert result.exit_code == 0
        # No deprecation warning
        assert "DEPRECATED" not in result.output
        # Clean JSON
        assert '"flows"' in result.output
