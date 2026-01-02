"""Test Claude Code native file parsing (skills, agents)."""
import tempfile
from pathlib import Path

import pytest
import yaml


def parse_skill_frontmatter(skill_path: Path) -> dict:
    """Parse YAML frontmatter from a SKILL.md file."""
    content = skill_path.read_text()
    if not content.startswith("---"):
        raise ValueError("Skill file must start with YAML frontmatter")

    # Find end of frontmatter
    end_idx = content.find("---", 3)
    if end_idx == -1:
        raise ValueError("Skill file must have closing --- for frontmatter")

    frontmatter = content[3:end_idx].strip()
    return yaml.safe_load(frontmatter)


def parse_agent_frontmatter(agent_path: Path) -> dict:
    """Parse YAML frontmatter from an agent .md file."""
    content = agent_path.read_text()
    if not content.startswith("---"):
        raise ValueError("Agent file must start with YAML frontmatter")

    end_idx = content.find("---", 3)
    if end_idx == -1:
        raise ValueError("Agent file must have closing --- for frontmatter")

    frontmatter = content[3:end_idx].strip()
    return yaml.safe_load(frontmatter)


class TestSkillParsing:
    """Test skill YAML frontmatter parsing."""

    def test_parse_skill_frontmatter(self, tmp_path):
        """Test parsing valid skill frontmatter."""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: test-skill
description: A test skill for validation
allowed-tools: Read, Grep, Glob
---

# Test Skill

Instructions here.
""")

        data = parse_skill_frontmatter(skill_file)
        assert data["name"] == "test-skill"
        assert "test skill" in data["description"].lower()
        assert data["allowed-tools"] == "Read, Grep, Glob"

    def test_skill_missing_frontmatter(self, tmp_path):
        """Test skill without frontmatter raises error."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("# No frontmatter\n\nJust content.")

        with pytest.raises(ValueError, match="must start with YAML frontmatter"):
            parse_skill_frontmatter(skill_file)

    def test_skill_required_fields(self, tmp_path):
        """Test skill with required fields."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: my-skill
description: Does something useful
---

# My Skill
""")

        data = parse_skill_frontmatter(skill_file)
        assert "name" in data
        assert "description" in data


class TestAgentParsing:
    """Test agent YAML frontmatter parsing."""

    def test_parse_agent_frontmatter(self, tmp_path):
        """Test parsing valid agent frontmatter."""
        agent_file = tmp_path / "planner.md"
        agent_file.write_text("""---
name: planner
description: Design and planning agent
tools: Read, Grep, Glob
model: sonnet
permissionMode: plan
---

# Planner Agent

Instructions here.
""")

        data = parse_agent_frontmatter(agent_file)
        assert data["name"] == "planner"
        assert data["permissionMode"] == "plan"
        assert "Read" in data["tools"]

    def test_agent_permission_mode(self, tmp_path):
        """Test agent permission mode validation."""
        agent_file = tmp_path / "reviewer.md"
        agent_file.write_text("""---
name: reviewer
description: Code review agent
permissionMode: plan
---

# Reviewer
""")

        data = parse_agent_frontmatter(agent_file)
        # Read-only agents should have permissionMode: plan
        assert data["permissionMode"] == "plan"


class TestSkillTriggerMatching:
    """Test skill trigger word matching."""

    def test_trigger_words_in_description(self, tmp_path):
        """Test that skill descriptions contain trigger words."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: design-plan-implement
description: Turn feature requests into plans. Use when user describes a feature, asks "how should we approach", or mentions planning. Triggers on design, plan, approach, feature.
---

# Design Plan Implement
""")

        data = parse_skill_frontmatter(skill_file)
        desc = data["description"].lower()

        # Check trigger words are in description
        trigger_words = ["design", "plan", "approach", "feature"]
        for word in trigger_words:
            assert word in desc, f"Trigger word '{word}' not in description"

    def test_multiple_skill_triggers(self, tmp_path):
        """Test multiple skills have distinct triggers."""
        skills = {
            "tdd-implement": "fix, bug, test, TDD, implement",
            "code-review": "review, check, PR, evaluate",
            "finish-branch": "finish, merge, complete, ship",
        }

        for skill_name, triggers in skills.items():
            skill_dir = tmp_path / skill_name
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(f"""---
name: {skill_name}
description: Triggers on {triggers}
---

# {skill_name}
""")

            data = parse_skill_frontmatter(skill_file)
            assert data["name"] == skill_name
            # Verify at least first trigger word is in description
            first_trigger = triggers.split(",")[0].strip()
            assert first_trigger in data["description"]
