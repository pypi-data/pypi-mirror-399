"""Tests for cookie cutter template generation and structure."""
import os
from pathlib import Path

import pytest
import yaml


# Path to the cookiecutter template
TEMPLATE_DIR = Path(__file__).parent.parent / "bpsai_pair" / "data" / "cookiecutter-paircoder"
PROJECT_TEMPLATE = TEMPLATE_DIR / "{{cookiecutter.project_slug}}"


class TestTemplateStructure:
    """Tests for template directory structure."""

    def test_template_exists(self):
        """Verify the template directory exists."""
        assert TEMPLATE_DIR.exists()
        assert PROJECT_TEMPLATE.exists()

    def test_cookiecutter_json_exists(self):
        """Verify cookiecutter.json exists and is valid."""
        json_file = TEMPLATE_DIR / "cookiecutter.json"
        assert json_file.exists()

        import json
        with open(json_file) as f:
            data = json.load(f)

        # Check required fields
        assert "project_name" in data
        assert "project_slug" in data
        assert "primary_goal" in data
        assert "coverage_target" in data
        assert "owner_gh_handle" in data

    def test_paircoder_structure(self):
        """Verify .paircoder/ directory structure."""
        paircoder_dir = PROJECT_TEMPLATE / ".paircoder"
        assert paircoder_dir.exists()

        # Required directories (v2.8+ uses skills instead of flows)
        assert (paircoder_dir / "context").exists()
        assert (paircoder_dir / "plans").exists()
        assert (paircoder_dir / "tasks").exists()
        assert (paircoder_dir / "security").exists()
        # Note: flows directory is deprecated in v2.8+, skills are in .claude/skills/

    def test_claude_structure(self):
        """Verify .claude/ directory structure."""
        claude_dir = PROJECT_TEMPLATE / ".claude"
        assert claude_dir.exists()

        # Required directories
        assert (claude_dir / "agents").exists()
        assert (claude_dir / "skills").exists()

        # Required files
        assert (claude_dir / "settings.json").exists()

    def test_github_workflows_exist(self):
        """Verify GitHub workflows exist."""
        workflows_dir = PROJECT_TEMPLATE / ".github" / "workflows"
        assert workflows_dir.exists()
        assert (workflows_dir / "ci.yml").exists()


class TestContextFiles:
    """Tests for .paircoder/context/ files."""

    def test_state_md_format(self):
        """Verify state.md has correct format."""
        state_file = PROJECT_TEMPLATE / ".paircoder" / "context" / "state.md"
        assert state_file.exists()

        content = state_file.read_text()

        # Must have required sections
        assert "# Current State" in content
        assert "## Active Plan" in content
        assert "**Current Sprint:**" in content  # New format
        assert "## Task Status" in content
        assert "### Active Sprint" in content  # New format
        assert "## What Was Just Done" in content
        assert "## What's Next" in content
        assert "## Blockers" in content

        # Should include quick commands
        assert "## Quick Commands" in content
        assert "bpsai-pair status" in content

    def test_project_md_format(self):
        """Verify project.md has correct format."""
        project_file = PROJECT_TEMPLATE / ".paircoder" / "context" / "project.md"
        assert project_file.exists()

        content = project_file.read_text()

        # Must have required sections
        assert "## What Is This Project?" in content
        assert "## Repository Structure" in content
        assert "## Tech Stack" in content
        assert "## Key Constraints" in content
        assert "## How to Work Here" in content

        # Should include directory structure
        assert ".paircoder/" in content
        assert ".claude/" in content

    def test_workflow_md_format(self):
        """Verify workflow.md has correct format."""
        workflow_file = PROJECT_TEMPLATE / ".paircoder" / "context" / "workflow.md"
        assert workflow_file.exists()

        content = workflow_file.read_text()

        # Must have required sections
        assert "## Branch Strategy" in content
        assert "## Development Cycle" in content
        assert "## Commit Messages" in content
        assert "## Testing Requirements" in content

        # Must have NON-NEGOTIABLE requirement
        assert "NON-NEGOTIABLE" in content
        assert "state.md" in content.lower()

        # Must have Definition of Done
        assert "## Definition of Done" in content


class TestCapabilitiesYaml:
    """Tests for capabilities.yaml template."""

    def test_capabilities_yaml_exists(self):
        """Verify capabilities.yaml exists."""
        caps_file = PROJECT_TEMPLATE / ".paircoder" / "capabilities.yaml"
        assert caps_file.exists()

    def test_capabilities_has_required_sections(self):
        """Verify capabilities.yaml has required sections (as text since it contains template vars)."""
        caps_file = PROJECT_TEMPLATE / ".paircoder" / "capabilities.yaml"
        content = caps_file.read_text()

        # Check version (v2.8+) - must start with 2.8
        assert 'version: "2.8' in content  # Allows 2.8, 2.8.1, 2.8.3, etc.

        # Required top-level sections (as text patterns)
        assert "context_files:" in content
        assert "directories:" in content
        assert "capabilities:" in content
        assert "Skill_triggers:" in content  # v2.8 uses skills instead of flows
        assert "roles:" in content
        assert "notes:" in content

    def test_capabilities_has_critical_notes(self):
        """Verify capabilities.yaml includes CRITICAL notes."""
        caps_file = PROJECT_TEMPLATE / ".paircoder" / "capabilities.yaml"
        content = caps_file.read_text()

        # Must include CRITICAL notes
        assert "CRITICAL" in content
        assert "state.md" in content


class TestConfigYaml:
    """Tests for config.yaml template."""

    def test_config_yaml_exists(self):
        """Verify config.yaml exists."""
        config_file = PROJECT_TEMPLATE / ".paircoder" / "config.yaml"
        assert config_file.exists()

    def test_config_has_all_sections(self):
        """Verify config.yaml has all required sections (as text since it contains template vars)."""
        config_file = PROJECT_TEMPLATE / ".paircoder" / "config.yaml"
        content = config_file.read_text()

        # Check version present
        assert "version:" in content

        # Required sections (as text patterns)
        assert "project:" in content
        assert "workflow:" in content
        assert "pack:" in content
        assert "skills:" in content  # v2.8 uses skills instead of flows
        assert "routing:" in content
        assert "trello:" in content
        assert "estimation:" in content
        assert "hooks:" in content
        assert "security:" in content


class TestCIWorkflows:
    """Tests for GitHub Actions workflows."""

    def test_ci_yml_has_proper_quoting(self):
        """Verify ci.yml has proper quoting for conditionals."""
        ci_file = PROJECT_TEMPLATE / ".github" / "workflows" / "ci.yml"
        content = ci_file.read_text()

        # Should use quoted 'true' in conditionals
        assert "== 'true'" in content

        # Should NOT have unquoted true comparisons
        assert "== true" not in content or "== 'true'" in content


class TestCodeowners:
    """Tests for CODEOWNERS file."""

    def test_codeowners_has_paircoder_paths(self):
        """Verify CODEOWNERS includes .paircoder/ paths."""
        codeowners_file = PROJECT_TEMPLATE / "CODEOWNERS"
        assert codeowners_file.exists()

        content = codeowners_file.read_text()

        # Must include .paircoder and .claude paths
        assert "/.paircoder/" in content
        assert "/.claude/" in content

        # Should have clear comments
        assert "# CODEOWNERS" in content


class TestSkillFiles:
    """Tests for skill template files."""

    def test_required_skills_exist(self):
        """Verify all required skills exist."""
        skills_dir = PROJECT_TEMPLATE / ".claude" / "skills"

        required_skills = [
            "designing-and-implementing",
            "implementing-with-tdd",
            "reviewing-code",
            "finishing-branches",
            "managing-task-lifecycle",
            "planning-with-trello",
        ]

        for skill_name in required_skills:
            skill_file = skills_dir / skill_name / "SKILL.md"
            assert skill_file.exists(), f"Missing required skill: {skill_name}"


class TestAgentFiles:
    """Tests for agent template files."""

    def test_required_agents_exist(self):
        """Verify all required agents exist."""
        agents_dir = PROJECT_TEMPLATE / ".claude" / "agents"

        required_agents = [
            "planner.md",
            "reviewer.md",
            "security.md",
        ]

        for agent_name in required_agents:
            agent_file = agents_dir / agent_name
            assert agent_file.exists(), f"Missing required agent: {agent_name}"


class TestSecurityFiles:
    """Tests for security template files."""

    def test_security_files_exist(self):
        """Verify security configuration files exist."""
        security_dir = PROJECT_TEMPLATE / ".paircoder" / "security"

        required_files = [
            "allowlist.yaml",
            "secret-allowlist.yaml",
            "sandbox.yaml",
        ]

        for filename in required_files:
            file_path = security_dir / filename
            assert file_path.exists(), f"Missing security file: {filename}"
