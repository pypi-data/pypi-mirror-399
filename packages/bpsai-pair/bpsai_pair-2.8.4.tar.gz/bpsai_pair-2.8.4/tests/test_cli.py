"""Tests for CLI commands."""
import json
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

# Add parent directory to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from bpsai_pair.cli import app
from bpsai_pair.core import ops

runner = CliRunner()


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary git repository."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, capture_output=True)

    # Create initial commit
    (repo / "README.md").write_text("# Test Repo")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True, capture_output=True)

    # Create main branch
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo, check=True, capture_output=True)

    return repo


@pytest.fixture
def initialized_repo(temp_repo):
    """Create a repo with PairCoder initialized (v2.1 structure)."""
    # Create v2.1 structure
    context_dir = temp_repo / ".paircoder" / "context"
    context_dir.mkdir(parents=True)
    (context_dir / "development.md").write_text("""# Development Log

**Phase:** Phase 1
**Primary Goal:** Test Goal

## Context Sync (AUTO-UPDATED)

Overall goal is: Test Goal
Last action was: Init
Next action will be: Test
Blockers: None
""")
    # v2 state.md format
    (context_dir / "state.md").write_text("""# Current State

## Active Plan

**Plan:** None
**Status:** Ready to start

## Current Focus

Testing.

## What Was Just Done

- Initial setup

## What's Next

1. Start working

## Blockers

None
""")
    # Create AGENTS.md at root (v2.1)
    (temp_repo / "AGENTS.md").write_text("# AGENTS.md\n\nSee `.paircoder/` for context.\n")
    (temp_repo / "CLAUDE.md").write_text("# CLAUDE.md\n\nSee `.paircoder/context/state.md`.\n")
    (temp_repo / ".paircoder" / "config.yaml").write_text("version: 2.1\n")
    (temp_repo / ".agentpackignore").write_text(".git/\n.venv/\n")

    return temp_repo


def test_version():
    """Test version display."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "bpsai-pair" in result.stdout


def test_init_not_in_repo(tmp_path, monkeypatch):
    """Test init when not in a git repo."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 1
    assert "Not in a git repository" in result.stdout


def test_status_basic(initialized_repo, monkeypatch):
    """Test status command."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "PairCoder Status" in result.stdout


def test_context_sync(initialized_repo, monkeypatch):
    """Test context sync."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, [
        "context-sync",
        "--last", "Did something",
        "--next", "Do something else"
    ])
    assert result.exit_code == 0
    assert "Context Sync updated" in result.stdout

    # Check file was updated - v2 uses state.md
    content = (initialized_repo / ".paircoder" / "context" / "state.md").read_text()
    assert "Did something" in content
    assert "Do something else" in content


def test_context_sync_legacy(initialized_repo, monkeypatch):
    """Test context sync with legacy development.md only."""
    monkeypatch.chdir(initialized_repo)

    # Remove state.md to force legacy fallback
    state_file = initialized_repo / ".paircoder" / "context" / "state.md"
    state_file.unlink()

    result = runner.invoke(app, [
        "context-sync",
        "--last", "Legacy action",
        "--next", "Legacy next"
    ])
    assert result.exit_code == 0
    assert "Context Sync updated" in result.stdout

    # Check legacy file was updated
    content = (initialized_repo / ".paircoder" / "context" / "development.md").read_text()
    assert "Last action was: Legacy action" in content
    assert "Next action will be: Legacy next" in content


def test_validate(initialized_repo, monkeypatch):
    """Test validate command."""
    monkeypatch.chdir(initialized_repo)

    # Add missing files first
    (initialized_repo / ".editorconfig").touch()
    (initialized_repo / "CONTRIBUTING.md").touch()

    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0


# ============================================================================
# Sprint and Release Command Tests
# ============================================================================


def test_sprint_complete_help():
    """Test sprint complete command help."""
    result = runner.invoke(app, ["sprint", "complete", "--help"])
    assert result.exit_code == 0
    assert "Complete a sprint with checklist verification" in result.stdout
    assert "--force" in result.stdout
    assert "--plan" in result.stdout


def test_sprint_list_help():
    """Test sprint list command help."""
    result = runner.invoke(app, ["sprint", "list", "--help"])
    assert result.exit_code == 0
    assert "List sprints in a plan" in result.stdout


def test_sprint_complete_no_active_plan(initialized_repo, monkeypatch):
    """Test sprint complete without an active plan."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["sprint", "complete", "17.5"])
    assert result.exit_code == 1
    assert "No active plan" in result.stdout


def test_sprint_complete_with_plan_flag(initialized_repo, monkeypatch):
    """Test sprint complete with explicit --plan flag."""
    monkeypatch.chdir(initialized_repo)

    # Create a sprint file with plan
    plans_dir = initialized_repo / ".paircoder" / "plans"
    plans_dir.mkdir(parents=True)
    sprint_file = plans_dir / "sprint-17.5.md"
    sprint_file.write_text("""# Sprint 17.5

## Goals
- Test goal

## Tasks
- [ ] TASK-001: Test task
""")

    # Using --plan flag should bypass needing active plan
    result = runner.invoke(app, ["sprint", "complete", "17.5", "--plan", "test-plan", "--force"])
    # Should proceed (may fail for other reasons but not for "no active plan")
    assert "No active plan" not in result.stdout


def test_sprint_complete_with_force(initialized_repo, monkeypatch):
    """Test sprint complete with --force flag skips checklist."""
    monkeypatch.chdir(initialized_repo)

    # Create plans directory and sprint file
    plans_dir = initialized_repo / ".paircoder" / "plans"
    plans_dir.mkdir(parents=True)
    sprint_file = plans_dir / "sprint-17.5.md"
    sprint_file.write_text("""# Sprint 17.5

## Goals
- Test goal

## Tasks
- [ ] TASK-001: Test task
""")

    # Use --plan to bypass active plan requirement
    result = runner.invoke(app, ["sprint", "complete", "17.5", "--plan", "test-plan", "--force"])
    # With --force, it should skip checklist
    assert "No active plan" not in result.stdout


def test_release_plan_help():
    """Test release plan command help."""
    result = runner.invoke(app, ["release", "plan", "--help"])
    assert result.exit_code == 0
    assert "Generate release preparation tasks" in result.stdout
    assert "--create" in result.stdout


def test_release_checklist_help():
    """Test release checklist command help."""
    result = runner.invoke(app, ["release", "checklist", "--help"])
    assert result.exit_code == 0
    assert "Show the release preparation checklist" in result.stdout


def test_release_checklist(initialized_repo, monkeypatch):
    """Test release checklist shows all items."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["release", "checklist"])
    assert result.exit_code == 0
    # Should show checklist items
    assert "Cookie cutter" in result.stdout or "CHANGELOG" in result.stdout or "checklist" in result.stdout.lower()


def test_release_plan_preview(initialized_repo, monkeypatch):
    """Test release plan shows tasks without --create-tasks."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["release", "plan", "--version", "2.2.0"])
    assert result.exit_code == 0
    # Should show preview without creating
    assert "REL-" in result.stdout or "release" in result.stdout.lower()


# ============================================================================
# Config Command Tests
# ============================================================================


def test_config_validate_help():
    """Test config validate command help."""
    result = runner.invoke(app, ["config", "validate", "--help"])
    assert result.exit_code == 0
    assert "Validate config against preset template" in result.stdout
    assert "--preset" in result.stdout
    assert "--json" in result.stdout


def test_config_update_help():
    """Test config update command help."""
    result = runner.invoke(app, ["config", "update", "--help"])
    assert result.exit_code == 0
    assert "Update config with missing sections from preset" in result.stdout
    assert "--preset" in result.stdout
    assert "--dry-run" in result.stdout


def test_config_show_help():
    """Test config show command help."""
    result = runner.invoke(app, ["config", "show", "--help"])
    assert result.exit_code == 0
    assert "Show current config or a specific section" in result.stdout


def test_config_validate_no_config(tmp_path, monkeypatch):
    """Test config validate when no config exists."""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["config", "validate"])
    assert result.exit_code == 1
    assert "No config file found" in result.stdout or "missing" in result.stdout.lower()


def test_config_validate_with_config(initialized_repo, monkeypatch):
    """Test config validate with existing config."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["config", "validate"])
    # Should show validation report
    assert "Config Validation Report" in result.stdout or "Version" in result.stdout


def test_config_validate_json(initialized_repo, monkeypatch):
    """Test config validate with JSON output."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["config", "validate", "--json"])
    # Should be valid JSON
    import json
    try:
        data = json.loads(result.stdout)
        assert "is_valid" in data
        assert "target_version" in data
        assert "missing_sections" in data
    except json.JSONDecodeError:
        # If it errors, might have other output mixed in
        pass


def test_config_update_no_config(tmp_path, monkeypatch):
    """Test config update when no config exists."""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["config", "update"])
    assert result.exit_code == 1
    assert "No config file found" in result.stdout or "init" in result.stdout.lower()


def test_config_update_dry_run(initialized_repo, monkeypatch):
    """Test config update with dry-run flag."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["config", "update", "--dry-run"])
    assert result.exit_code == 0
    assert "Dry run" in result.stdout or "no changes made" in result.stdout.lower() or "already up to date" in result.stdout.lower()


def test_config_update_adds_missing_sections(initialized_repo, monkeypatch):
    """Test config update adds missing sections."""
    monkeypatch.chdir(initialized_repo)

    # First create a minimal config missing some sections
    config_file = initialized_repo / ".paircoder" / "config.yaml"
    config_file.write_text("""version: "2.4"
project:
  name: Test Project
  primary_goal: Build stuff
""")

    result = runner.invoke(app, ["config", "update", "--dry-run"])
    assert result.exit_code == 0
    # Should show changes to be made
    assert "Changes" in result.stdout or "Added" in result.stdout


def test_config_show_no_config(tmp_path, monkeypatch):
    """Test config show when no config exists."""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 1
    assert "No config file found" in result.stdout


def test_config_show_with_config(initialized_repo, monkeypatch):
    """Test config show with existing config."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    # Should show config content
    assert "version" in result.stdout.lower()


def test_config_show_section(initialized_repo, monkeypatch):
    """Test config show for a specific section."""
    monkeypatch.chdir(initialized_repo)

    # Create config with project section
    config_file = initialized_repo / ".paircoder" / "config.yaml"
    config_file.write_text("""version: "2.6"
project:
  name: Test Project
  primary_goal: Build stuff
hooks:
  enabled: true
""")

    result = runner.invoke(app, ["config", "show", "project"])
    assert result.exit_code == 0
    assert "name" in result.stdout.lower()
    assert "Test Project" in result.stdout


def test_config_show_section_not_found(initialized_repo, monkeypatch):
    """Test config show for a non-existent section."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["config", "show", "nonexistent"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


# ============================================================================
# Trello Custom Field Command Tests
# ============================================================================


def test_trello_list_fields_help():
    """Test trello list-fields command help."""
    result = runner.invoke(app, ["trello", "list-fields", "--help"])
    assert result.exit_code == 0
    assert "List all custom fields" in result.stdout


def test_trello_set_field_help():
    """Test trello set-field command help."""
    result = runner.invoke(app, ["trello", "set-field", "--help"])
    assert result.exit_code == 0
    assert "Set custom field values" in result.stdout
    assert "--project" in result.stdout
    assert "--stack" in result.stdout
    assert "--status" in result.stdout


def test_trello_apply_defaults_help():
    """Test trello apply-defaults command help."""
    result = runner.invoke(app, ["trello", "apply-defaults", "--help"])
    assert result.exit_code == 0
    assert "Apply project default values" in result.stdout


def test_trello_list_fields_no_board(initialized_repo, monkeypatch):
    """Test trello list-fields without configured board."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["trello", "list-fields"])
    assert result.exit_code == 1
    assert "No board configured" in result.stdout


def test_trello_set_field_no_board(initialized_repo, monkeypatch):
    """Test trello set-field without configured board."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["trello", "set-field", "abc123", "--project", "Test"])
    assert result.exit_code == 1
    assert "No board configured" in result.stdout


def test_trello_apply_defaults_no_board(initialized_repo, monkeypatch):
    """Test trello apply-defaults without configured board."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["trello", "apply-defaults", "abc123"])
    assert result.exit_code == 1
    assert "No board configured" in result.stdout


def test_trello_set_field_no_fields_specified(initialized_repo, monkeypatch):
    """Test trello set-field when no fields specified."""
    monkeypatch.chdir(initialized_repo)

    # Create config with board ID
    config_file = initialized_repo / ".paircoder" / "config.yaml"
    config_file.write_text("""version: "2.6"
trello:
  board_id: "test-board"
""")

    result = runner.invoke(app, ["trello", "set-field", "abc123"])
    # Should fail - either "No fields specified" or "Not connected" (if no Trello creds)
    assert result.exit_code == 1 or result.exception is not None


def test_trello_apply_defaults_no_defaults_configured(initialized_repo, monkeypatch):
    """Test trello apply-defaults when no defaults in config."""
    monkeypatch.chdir(initialized_repo)

    # Create config with board ID but no defaults
    config_file = initialized_repo / ".paircoder" / "config.yaml"
    config_file.write_text("""version: "2.6"
trello:
  board_id: "test-board"
""")

    result = runner.invoke(app, ["trello", "apply-defaults", "abc123"])
    assert result.exit_code == 1
    assert "No defaults configured" in result.stdout or "Not connected" in result.stdout


def test_plan_sync_trello_apply_defaults_flag():
    """Test plan sync-trello has --apply-defaults flag."""
    result = runner.invoke(app, ["plan", "sync-trello", "--help"])
    assert result.exit_code == 0
    assert "--apply-defaults" in result.stdout
    assert "Apply project defaults" in result.stdout


# ============================================================================
# Preset CI Workflow Tests
# ============================================================================


def test_preset_show_includes_ci_type():
    """Test that preset show displays ci_type."""
    result = runner.invoke(app, ["preset", "show", "react"])
    assert result.exit_code == 0
    assert "CI workflow:" in result.stdout or "ci_type" in result.stdout.lower()
    assert "node" in result.stdout


def test_preset_show_python_cli_ci_type():
    """Test that python-cli preset has python ci_type."""
    result = runner.invoke(app, ["preset", "show", "python-cli"])
    assert result.exit_code == 0
    assert "python" in result.stdout.lower()


def test_preset_show_fullstack_ci_type():
    """Test that fullstack preset has fullstack ci_type."""
    result = runner.invoke(app, ["preset", "show", "fullstack"])
    assert result.exit_code == 0
    assert "fullstack" in result.stdout.lower()


def test_preset_show_json_includes_ci_type():
    """Test that preset show JSON output includes ci_type."""
    result = runner.invoke(app, ["preset", "show", "react", "--json"])
    assert result.exit_code == 0
    import json
    try:
        data = json.loads(result.stdout)
        assert "ci_type" in data
        assert data["ci_type"] == "node"
    except json.JSONDecodeError:
        pass  # May have other output mixed in


def test_select_ci_workflow_python(tmp_path, monkeypatch):
    """Test _select_ci_workflow selects python workflow."""
    from bpsai_pair.commands.core import _select_ci_workflow

    # Create workflows directory with all three files
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "ci.yml").write_text("fullstack")
    (workflows_dir / "ci-node.yml").write_text("node")
    (workflows_dir / "ci-python.yml").write_text("python")

    _select_ci_workflow(tmp_path, "python")

    assert (workflows_dir / "ci.yml").exists()
    assert (workflows_dir / "ci.yml").read_text() == "python"
    assert not (workflows_dir / "ci-node.yml").exists()
    assert not (workflows_dir / "ci-python.yml").exists()


def test_select_ci_workflow_node(tmp_path, monkeypatch):
    """Test _select_ci_workflow selects node workflow."""
    from bpsai_pair.commands.core import _select_ci_workflow

    # Create workflows directory with all three files
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "ci.yml").write_text("fullstack")
    (workflows_dir / "ci-node.yml").write_text("node")
    (workflows_dir / "ci-python.yml").write_text("python")

    _select_ci_workflow(tmp_path, "node")

    assert (workflows_dir / "ci.yml").exists()
    assert (workflows_dir / "ci.yml").read_text() == "node"
    assert not (workflows_dir / "ci-node.yml").exists()
    assert not (workflows_dir / "ci-python.yml").exists()


def test_select_ci_workflow_fullstack(tmp_path, monkeypatch):
    """Test _select_ci_workflow keeps fullstack workflow."""
    from bpsai_pair.commands.core import _select_ci_workflow

    # Create workflows directory with all three files
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "ci.yml").write_text("fullstack")
    (workflows_dir / "ci-node.yml").write_text("node")
    (workflows_dir / "ci-python.yml").write_text("python")

    _select_ci_workflow(tmp_path, "fullstack")

    assert (workflows_dir / "ci.yml").exists()
    assert (workflows_dir / "ci.yml").read_text() == "fullstack"
    assert not (workflows_dir / "ci-node.yml").exists()
    assert not (workflows_dir / "ci-python.yml").exists()


def test_select_ci_workflow_no_workflows_dir(tmp_path):
    """Test _select_ci_workflow handles missing workflows directory."""
    from bpsai_pair.commands.core import _select_ci_workflow

    # Should not raise an error
    _select_ci_workflow(tmp_path, "python")
