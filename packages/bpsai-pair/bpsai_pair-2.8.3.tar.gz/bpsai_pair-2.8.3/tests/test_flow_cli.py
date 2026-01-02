"""Tests for the flow CLI commands."""

import json
import os
import pytest
from pathlib import Path
from typer.testing import CliRunner

from bpsai_pair.cli import app


runner = CliRunner()


@pytest.fixture
def temp_dir_with_flows(tmp_path, monkeypatch):
    """Create a temporary directory with sample flows."""
    # Change to temp directory for CLI commands
    monkeypatch.chdir(tmp_path)

    # Create .git directory (required for repo_root())
    (tmp_path / ".git").mkdir()

    # Create .paircoder/flows directory
    flows_dir = tmp_path / ".paircoder" / "flows"
    flows_dir.mkdir(parents=True)

    # Create sample flows (must be .flow.md for v2 parser)
    (flows_dir / "code-review.flow.md").write_text("""---
name: code-review
description: Review code for quality and best practices
tags: [review, quality]
triggers: [review_request]
version: 1
---

# Code Review Flow

Follow these steps to review code:

1. Check for code style
2. Look for potential bugs
3. Verify test coverage
""")

    (flows_dir / "deploy.flow.md").write_text("""---
name: deploy
description: Deploy application to production
tags: [deployment, ci-cd]
triggers: [deploy_request]
version: 2
---

# Deployment Flow

Steps for deploying to production:

1. Run tests
2. Build artifacts
3. Deploy to staging
4. Deploy to production
""")

    return tmp_path


@pytest.fixture
def temp_dir_empty(tmp_path, monkeypatch):
    """Create an empty temporary directory."""
    monkeypatch.chdir(tmp_path)
    # Create .git directory (required for repo_root())
    (tmp_path / ".git").mkdir()
    return tmp_path


class TestFlowList:
    """Tests for 'flow list' command."""

    def test_flow_list_shows_flows(self, temp_dir_with_flows):
        """flow list shows available flows."""
        result = runner.invoke(app, ["flow", "list"])

        assert result.exit_code == 0
        assert "code-review" in result.stdout
        assert "deploy" in result.stdout
        assert "Review code for quality" in result.stdout

    def test_flow_list_shows_tags(self, temp_dir_with_flows):
        """flow list shows flow triggers."""
        result = runner.invoke(app, ["flow", "list"])

        assert result.exit_code == 0
        # v2 parser shows triggers instead of tags in list
        assert "review_request" in result.stdout or "deploy_request" in result.stdout

    def test_flow_list_empty(self, temp_dir_empty):
        """flow list shows message when no flows found."""
        result = runner.invoke(app, ["flow", "list"])

        assert result.exit_code == 0
        assert "No flows" in result.stdout

    def test_flow_list_json(self, temp_dir_with_flows):
        """flow list --json outputs valid JSON."""
        result = runner.invoke(app, ["flow", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "flows" in data
        assert "count" in data
        assert data["count"] == 2
        assert len(data["flows"]) == 2

        # Check flow structure
        flow_names = [f["name"] for f in data["flows"]]
        assert "code-review" in flow_names
        assert "deploy" in flow_names

    def test_flow_list_json_empty(self, temp_dir_empty):
        """flow list --json with no flows."""
        result = runner.invoke(app, ["flow", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["flows"] == []
        assert data["count"] == 0


class TestFlowShow:
    """Tests for 'flow show' command."""

    def test_flow_show_displays_flow(self, temp_dir_with_flows):
        """flow show displays flow details."""
        result = runner.invoke(app, ["flow", "show", "code-review"])

        assert result.exit_code == 0
        assert "code-review" in result.stdout
        assert "Review code for quality" in result.stdout
        assert "# Code Review Flow" in result.stdout
        assert "Check for code style" in result.stdout

    def test_flow_show_displays_metadata(self, temp_dir_with_flows):
        """flow show displays version and triggers."""
        result = runner.invoke(app, ["flow", "show", "deploy"])

        assert result.exit_code == 0
        assert "Version: 2" in result.stdout or "MD" in result.stdout  # format indicator
        assert "deploy_request" in result.stdout  # triggers

    def test_flow_show_not_found(self, temp_dir_with_flows):
        """flow show shows error for non-existent flow."""
        result = runner.invoke(app, ["flow", "show", "nonexistent"])

        assert result.exit_code == 1
        assert "Flow not found" in result.stdout

    def test_flow_show_not_found_empty(self, temp_dir_empty):
        """flow show shows error when no flows exist."""
        result = runner.invoke(app, ["flow", "show", "any"])

        assert result.exit_code == 1
        assert "Flow not found" in result.stdout

    def test_flow_show_body_only(self, temp_dir_with_flows):
        """flow show includes body content."""
        result = runner.invoke(app, ["flow", "show", "code-review"])

        assert result.exit_code == 0
        assert "# Code Review Flow" in result.stdout
        assert "Check for code style" in result.stdout

    def test_flow_show_json(self, temp_dir_with_flows):
        """flow show --json outputs valid JSON."""
        result = runner.invoke(app, ["flow", "show", "deploy", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["name"] == "deploy"
        assert data["description"] == "Deploy application to production"
        assert data["tags"] == ["deployment", "ci-cd"]
        assert data["version"] == 2  # integer in v2


class TestFlowHelp:
    """Tests for flow command help."""

    def test_flow_help(self):
        """flow --help shows subcommands."""
        result = runner.invoke(app, ["flow", "--help"])

        assert result.exit_code == 0
        assert "list" in result.stdout
        assert "show" in result.stdout

    def test_flow_list_help(self):
        """flow list --help shows options."""
        result = runner.invoke(app, ["flow", "list", "--help"])

        assert result.exit_code == 0
        assert "--json" in result.stdout

    def test_flow_show_help(self):
        """flow show --help shows options."""
        result = runner.invoke(app, ["flow", "show", "--help"])

        assert result.exit_code == 0
        assert "--json" in result.stdout
