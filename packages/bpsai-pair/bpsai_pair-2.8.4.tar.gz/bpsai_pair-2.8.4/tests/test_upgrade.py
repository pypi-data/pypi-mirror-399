"""Tests for upgrade command and template resolution."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from bpsai_pair.commands.upgrade import (
    get_template_dir,
    get_bundled_skills,
    get_bundled_agents,
    get_bundled_commands,
    plan_upgrade,
    execute_upgrade,
    UpgradePlan,
)


class TestGetTemplateDir:
    """Tests for template directory resolution."""

    def test_finds_template_in_dev_mode(self):
        """Template is found via development fallback path."""
        template = get_template_dir()
        assert template is not None
        assert template.exists()
        assert "cookiecutter-paircoder" in str(template)
        assert "{{cookiecutter.project_slug}}" in str(template)

    def test_template_has_expected_structure(self):
        """Template directory has expected subdirectories."""
        template = get_template_dir()
        assert template is not None

        # Check for expected directories
        assert (template / ".claude").exists()
        assert (template / ".claude" / "skills").exists()
        assert (template / ".claude" / "agents").exists()
        assert (template / ".paircoder").exists()

    def test_returns_none_when_no_template(self, tmp_path, monkeypatch):
        """Returns None when template cannot be found."""
        import importlib.resources

        # Create a mock that raises ModuleNotFoundError
        def mock_files(package):
            raise ModuleNotFoundError(f"No module named '{package}'")

        # Patch importlib.resources.files to fail
        monkeypatch.setattr(importlib.resources, "files", mock_files)

        # Also patch __file__ in the upgrade module to point elsewhere
        import bpsai_pair.commands.upgrade as upgrade_module

        # Save original __file__
        original_file = upgrade_module.__file__

        try:
            # Temporarily set __file__ to a location without the template
            upgrade_module.__file__ = str(tmp_path / "fake" / "upgrade.py")

            result = get_template_dir()
            assert result is None
        finally:
            # Restore original __file__
            upgrade_module.__file__ = original_file


class TestGetBundledSkills:
    """Tests for bundled skills discovery."""

    def test_finds_skills_in_template(self):
        """Skills are discovered from template directory."""
        template = get_template_dir()
        assert template is not None

        skills = get_bundled_skills(template)
        assert isinstance(skills, dict)
        assert len(skills) > 0

        # Check for expected skills
        expected_skills = [
            "designing-and-implementing",
            "implementing-with-tdd",
            "reviewing-code",
            "finishing-branches",
            "managing-task-lifecycle",
            "planning-with-trello",
        ]

        for skill_name in expected_skills:
            assert skill_name in skills, f"Missing skill: {skill_name}"
            assert skills[skill_name].exists()
            assert skills[skill_name].name == "SKILL.md"

    def test_returns_empty_dict_for_missing_dir(self, tmp_path):
        """Returns empty dict when skills directory doesn't exist."""
        skills = get_bundled_skills(tmp_path)
        assert skills == {}


class TestGetBundledAgents:
    """Tests for bundled agents discovery."""

    def test_finds_agents_in_template(self):
        """Agents are discovered from template directory."""
        template = get_template_dir()
        assert template is not None

        agents = get_bundled_agents(template)
        assert isinstance(agents, dict)
        assert len(agents) > 0

        # Check for expected agents
        expected_agents = ["planner", "reviewer", "security"]

        for agent_name in expected_agents:
            assert agent_name in agents, f"Missing agent: {agent_name}"
            assert agents[agent_name].exists()

    def test_returns_empty_dict_for_missing_dir(self, tmp_path):
        """Returns empty dict when agents directory doesn't exist."""
        agents = get_bundled_agents(tmp_path)
        assert agents == {}


class TestGetBundledCommands:
    """Tests for bundled commands discovery."""

    def test_finds_commands_in_template(self):
        """Commands are discovered from template directory."""
        template = get_template_dir()
        assert template is not None

        commands = get_bundled_commands(template)
        assert isinstance(commands, dict)
        assert len(commands) > 0

        # Check for expected commands
        expected_commands = ["pc-plan", "start-task", "update-skills"]

        for cmd_name in expected_commands:
            assert cmd_name in commands, f"Missing command: {cmd_name}"
            assert commands[cmd_name].exists()

    def test_returns_empty_dict_for_missing_dir(self, tmp_path):
        """Returns empty dict when commands directory doesn't exist."""
        commands = get_bundled_commands(tmp_path)
        assert commands == {}


class TestPlanUpgrade:
    """Tests for upgrade planning."""

    def test_plan_detects_missing_skills(self, tmp_path):
        """Plan identifies skills that need to be added."""
        # Create minimal project structure
        (tmp_path / ".claude" / "skills").mkdir(parents=True)
        (tmp_path / ".paircoder").mkdir(parents=True)
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.1'")

        template = get_template_dir()
        assert template is not None

        plan = plan_upgrade(tmp_path, template)

        # All bundled skills should be in skills_to_add
        bundled_skills = get_bundled_skills(template)
        assert len(plan.skills_to_add) == len(bundled_skills)

    def test_plan_detects_outdated_skills(self, tmp_path):
        """Plan identifies skills that need to be updated."""
        # Create project with outdated skill
        skills_dir = tmp_path / ".claude" / "skills" / "reviewing-code"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("# Old content\n\nOutdated skill.")

        (tmp_path / ".paircoder").mkdir(parents=True)
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.1'")

        template = get_template_dir()
        assert template is not None

        plan = plan_upgrade(tmp_path, template)

        # reviewing-code should be in updates (content differs)
        assert "reviewing-code" in plan.skills_to_update

    def test_plan_detects_missing_agents(self, tmp_path):
        """Plan identifies agents that need to be added."""
        (tmp_path / ".claude" / "agents").mkdir(parents=True)
        (tmp_path / ".paircoder").mkdir(parents=True)
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.1'")

        template = get_template_dir()
        assert template is not None

        plan = plan_upgrade(tmp_path, template)

        bundled_agents = get_bundled_agents(template)
        assert len(plan.agents_to_add) == len(bundled_agents)

    def test_plan_detects_missing_commands(self, tmp_path):
        """Plan identifies commands that need to be added."""
        (tmp_path / ".claude" / "commands").mkdir(parents=True)
        (tmp_path / ".paircoder").mkdir(parents=True)
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.1'")

        template = get_template_dir()
        assert template is not None

        plan = plan_upgrade(tmp_path, template)

        bundled_commands = get_bundled_commands(template)
        assert len(plan.commands_to_add) == len(bundled_commands)

    def test_plan_detects_outdated_commands(self, tmp_path):
        """Plan identifies commands that need to be updated."""
        # Create project with outdated command
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "start-task.md").write_text("# Old content\n\nOutdated command.")

        (tmp_path / ".paircoder").mkdir(parents=True)
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.1'")

        template = get_template_dir()
        assert template is not None

        plan = plan_upgrade(tmp_path, template)

        # start-task should be in updates (content differs)
        assert "start-task" in plan.commands_to_update

    def test_plan_detects_missing_config_sections(self, tmp_path):
        """Plan identifies config sections that need to be added."""
        (tmp_path / ".claude").mkdir(parents=True)
        (tmp_path / ".paircoder").mkdir(parents=True)
        (tmp_path / ".paircoder" / "config.yaml").write_text(
            "version: '2.1'\nproject:\n  name: test\n"
        )

        template = get_template_dir()
        assert template is not None

        plan = plan_upgrade(tmp_path, template)

        # Required sections should be detected as missing
        assert "trello" in plan.config_sections_to_add
        assert "hooks" in plan.config_sections_to_add


class TestExecuteUpgrade:
    """Tests for upgrade execution."""

    def test_execute_copies_commands(self, tmp_path):
        """Execute upgrade copies commands to project."""
        # Create minimal project structure
        (tmp_path / ".claude" / "commands").mkdir(parents=True)
        (tmp_path / ".paircoder").mkdir(parents=True)
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.1'")

        template = get_template_dir()
        assert template is not None

        plan = plan_upgrade(tmp_path, template)
        results = execute_upgrade(tmp_path, template, plan)

        # Commands should have been added
        assert results["commands_added"] > 0

        # Verify files exist
        commands_dir = tmp_path / ".claude" / "commands"
        assert (commands_dir / "start-task.md").exists()
        assert (commands_dir / "pc-plan.md").exists()

    def test_execute_updates_commands(self, tmp_path):
        """Execute upgrade updates outdated commands."""
        # Create project with outdated command
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "start-task.md").write_text("# Outdated")

        (tmp_path / ".paircoder").mkdir(parents=True)
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.1'")

        template = get_template_dir()
        assert template is not None

        plan = plan_upgrade(tmp_path, template)
        results = execute_upgrade(tmp_path, template, plan)

        # Command should have been updated
        assert results["commands_updated"] >= 1

        # Verify file was updated (no longer just "# Outdated")
        content = (commands_dir / "start-task.md").read_text()
        assert content != "# Outdated"
        assert len(content) > 20  # Should have real content


class TestImportlibResourcesIntegration:
    """Tests for importlib.resources integration."""

    def test_template_accessible_via_importlib(self):
        """Template is accessible via importlib.resources API."""
        import importlib.resources as resources

        # This should work because bpsai_pair.data now has __init__.py
        data_dir = resources.files("bpsai_pair.data")
        assert data_dir is not None

        # Navigate to template
        template = data_dir.joinpath(
            "cookiecutter-paircoder", "{{cookiecutter.project_slug}}"
        )

        # Should be able to convert to string path
        template_str = str(template)
        assert "cookiecutter-paircoder" in template_str

    def test_data_package_has_init(self):
        """The data directory has __init__.py for package access."""
        import bpsai_pair.data

        # This import should succeed
        assert bpsai_pair.data is not None
