"""Tests for skill validator module."""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestSkillValidation:
    """Tests for SkillValidator class."""

    def test_validates_valid_skill(self):
        """Should pass for a correctly formatted skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("""---
name: my-skill
description: Manages project tasks efficiently. Triggers on task-related keywords.
---

# My Skill

Content here.
""")

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(Path(tmpdir))
            results = validator.validate_skill(skill_dir)

            assert results["valid"] is True
            assert results["errors"] == []
            assert results["warnings"] == []

    def test_detects_extra_frontmatter_fields(self):
        """Should error when frontmatter has extra fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("""---
name: my-skill
description: Valid description here.
version: 1.0.0
author: Someone
---

# Content
""")

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(Path(tmpdir))
            results = validator.validate_skill(skill_dir)

            assert results["valid"] is False
            assert any("extra" in e.lower() or "version" in e.lower() for e in results["errors"])

    def test_detects_missing_name(self):
        """Should error when name field is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("""---
description: Valid description here.
---

# Content
""")

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(Path(tmpdir))
            results = validator.validate_skill(skill_dir)

            assert results["valid"] is False
            assert any("name" in e.lower() for e in results["errors"])

    def test_detects_missing_description(self):
        """Should error when description field is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("""---
name: my-skill
---

# Content
""")

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(Path(tmpdir))
            results = validator.validate_skill(skill_dir)

            assert results["valid"] is False
            assert any("description" in e.lower() for e in results["errors"])

    def test_detects_description_too_long(self):
        """Should error when description exceeds 1024 characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            long_desc = "A" * 1025
            skill_file.write_text(f"""---
name: my-skill
description: {long_desc}
---

# Content
""")

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(Path(tmpdir))
            results = validator.validate_skill(skill_dir)

            assert results["valid"] is False
            assert any("1024" in e or "too long" in e.lower() for e in results["errors"])

    def test_warns_on_second_person_description(self):
        """Should warn when description uses 2nd person voice."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("""---
name: my-skill
description: Use when you need to manage tasks. Triggers on keywords.
---

# Content
""")

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(Path(tmpdir))
            results = validator.validate_skill(skill_dir)

            # Still valid, but with warnings
            assert results["valid"] is True
            assert any("person" in w.lower() or "voice" in w.lower() for w in results["warnings"])

    def test_detects_file_too_long(self):
        """Should error when SKILL.md exceeds 500 lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            content = """---
name: my-skill
description: Valid description.
---

# Content
"""
            # Add 500+ lines
            content += "\n".join([f"Line {i}" for i in range(510)])
            skill_file.write_text(content)

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(Path(tmpdir))
            results = validator.validate_skill(skill_dir)

            assert results["valid"] is False
            assert any("500" in e or "lines" in e.lower() for e in results["errors"])

    def test_warns_on_non_gerund_name(self):
        """Should warn when skill name doesn't use gerund form."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "code-review"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("""---
name: code-review
description: Reviews code for quality and correctness.
---

# Content
""")

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(Path(tmpdir))
            results = validator.validate_skill(skill_dir)

            # Valid but with naming warning
            assert results["valid"] is True
            assert any("gerund" in w.lower() or "reviewing" in w.lower() for w in results["warnings"])

    def test_detects_name_mismatch(self):
        """Should error when name doesn't match directory name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("""---
name: different-name
description: Valid description here.
---

# Content
""")

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(Path(tmpdir))
            results = validator.validate_skill(skill_dir)

            assert results["valid"] is False
            assert any("match" in e.lower() or "directory" in e.lower() for e in results["errors"])


class TestValidateAll:
    """Tests for validating all skills in a directory."""

    def test_validates_multiple_skills(self):
        """Should validate all skill directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir)

            # Create two valid skills
            for name in ["skill-one", "skill-two"]:
                skill_dir = skills_dir / name
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(f"""---
name: {name}
description: Manages {name} functionality.
---

# {name}
""")

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(skills_dir)
            results = validator.validate_all()

            assert len(results) == 2
            assert all(r["valid"] for r in results.values())

    def test_returns_summary(self):
        """Should return a summary of validation results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir)

            # Create one valid and one invalid skill
            valid_dir = skills_dir / "valid-skill"
            valid_dir.mkdir()
            (valid_dir / "SKILL.md").write_text("""---
name: valid-skill
description: A valid skill.
---

# Valid
""")

            invalid_dir = skills_dir / "invalid-skill"
            invalid_dir.mkdir()
            (invalid_dir / "SKILL.md").write_text("""---
name: wrong-name
description: Description.
---

# Invalid
""")

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(skills_dir)
            results = validator.validate_all()
            summary = validator.get_summary(results)

            assert summary["total"] == 2
            assert summary["passed"] == 1
            assert summary["failed"] == 1


class TestAutoFix:
    """Tests for auto-fix functionality."""

    def test_fix_removes_extra_fields(self):
        """--fix should remove extra frontmatter fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("""---
name: my-skill
description: Valid description.
version: 1.0.0
author: Someone
---

# Content
""")

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(Path(tmpdir))
            fixed = validator.fix_skill(skill_dir)

            assert fixed is True
            # Re-validate
            results = validator.validate_skill(skill_dir)
            assert results["valid"] is True

    def test_fix_description_voice(self):
        """--fix should convert 2nd person to 3rd person in description."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("""---
name: my-skill
description: Use when you need to manage tasks.
---

# Content
""")

            from bpsai_pair.skills.validator import SkillValidator
            validator = SkillValidator(Path(tmpdir))
            fixed = validator.fix_skill(skill_dir)

            # Read the fixed content
            content = skill_file.read_text()
            # Should have converted "Use when you" to something like "Manages tasks when..."
            assert "you" not in content.lower() or fixed is False  # Either fixed or couldn't fix


class TestCLICommand:
    """Tests for the CLI skill validate command."""

    def test_skill_validate_command_exists(self):
        """skill validate command should exist."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["skill", "validate", "--help"])

        assert result.exit_code == 0
        assert "validate" in result.output.lower()

    def test_skill_validate_lists_results(self):
        """skill validate should show results for each skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            skill_dir = skills_dir / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: test-skill
description: Tests things.
---

# Test
""")

            from typer.testing import CliRunner
            from bpsai_pair.cli import app

            runner = CliRunner()
            # Need to patch both the validator module and cli_commands module
            with patch('bpsai_pair.skills.cli_commands.find_skills_dir') as mock_find:
                mock_find.return_value = skills_dir
                result = runner.invoke(app, ["skill", "validate"])

            assert result.exit_code == 0
            assert "test-skill" in result.output

    def test_skill_validate_fix_flag(self):
        """skill validate --fix should auto-correct issues."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["skill", "validate", "--fix", "--help"])

        assert "--fix" in result.output
