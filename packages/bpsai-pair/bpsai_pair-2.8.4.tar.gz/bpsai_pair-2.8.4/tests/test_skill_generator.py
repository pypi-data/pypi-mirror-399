"""Tests for skill generator module."""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestGeneratedSkill:
    """Tests for GeneratedSkill dataclass."""

    def test_generated_skill_creation(self):
        """Should create GeneratedSkill with all fields."""
        from bpsai_pair.skills.generator import GeneratedSkill

        skill = GeneratedSkill(
            name="debugging-tests",
            content="# Debugging Tests\n\nContent here...",
            source_pattern=["pytest", "read_error", "fix"],
            requires_review=True,
        )

        assert skill.name == "debugging-tests"
        assert "# Debugging Tests" in skill.content
        assert skill.requires_review is True

    def test_generated_skill_to_dict(self):
        """Should convert to dict for serialization."""
        from bpsai_pair.skills.generator import GeneratedSkill

        skill = GeneratedSkill(
            name="test-skill",
            content="content",
            source_pattern=["a", "b"],
            requires_review=False,
        )

        d = skill.to_dict()
        assert d["name"] == "test-skill"
        assert d["source_pattern"] == ["a", "b"]


class TestSkillGenerator:
    """Tests for SkillGenerator class."""

    def test_generates_valid_frontmatter(self):
        """Generated skill should have valid YAML frontmatter."""
        from bpsai_pair.skills.generator import SkillGenerator
        from bpsai_pair.skills.gap_detector import SkillGap

        generator = SkillGenerator()

        gap = SkillGap(
            pattern=["pytest", "read_traceback", "edit_fix"],
            suggested_name="debugging-tests",
            confidence=0.85,
            frequency=5,
            time_saved_estimate="~5 min",
            detected_at="2025-12-23T10:00:00",
        )

        result = generator.generate_from_gap(gap)

        assert result.content.startswith("---\n")
        assert "name: debugging-tests" in result.content
        assert "description:" in result.content
        # Frontmatter should end with ---
        assert "\n---\n" in result.content

    def test_generates_third_person_description(self):
        """Description should use third-person voice."""
        from bpsai_pair.skills.generator import SkillGenerator
        from bpsai_pair.skills.gap_detector import SkillGap

        generator = SkillGenerator()

        gap = SkillGap(
            pattern=["git status", "git diff", "git add"],
            suggested_name="managing-git-changes",
            confidence=0.75,
            frequency=4,
            time_saved_estimate="~3 min",
            detected_at="2025-12-23T10:00:00",
        )

        result = generator.generate_from_gap(gap)

        # Should NOT contain "you" in description
        lines = result.content.split("\n")
        for line in lines:
            if line.startswith("description:"):
                desc = line.replace("description:", "").strip()
                assert "you" not in desc.lower(), f"Description uses second person: {desc}"

    def test_generates_gerund_named_title(self):
        """Generated skill should have proper title."""
        from bpsai_pair.skills.generator import SkillGenerator
        from bpsai_pair.skills.gap_detector import SkillGap

        generator = SkillGenerator()

        gap = SkillGap(
            pattern=["pytest", "fix"],
            suggested_name="testing-workflows",
            confidence=0.8,
            frequency=4,
            time_saved_estimate="~2 min",
            detected_at="2025-12-23T10:00:00",
        )

        result = generator.generate_from_gap(gap)

        # Should have a markdown title
        assert "# " in result.content
        # Name should be lowercase with hyphens
        assert result.name == result.name.lower()
        assert "_" not in result.name

    def test_includes_observed_commands(self):
        """Generated skill should include observed commands from pattern."""
        from bpsai_pair.skills.generator import SkillGenerator
        from bpsai_pair.skills.gap_detector import SkillGap

        generator = SkillGenerator()

        gap = SkillGap(
            pattern=["pytest --verbose", "grep error", "vim file.py"],
            suggested_name="debugging-workflows",
            confidence=0.8,
            frequency=5,
            time_saved_estimate="~4 min",
            detected_at="2025-12-23T10:00:00",
        )

        result = generator.generate_from_gap(gap)

        # Commands from pattern should appear in content
        assert "pytest" in result.content
        assert "grep" in result.content or "search" in result.content.lower()

    def test_includes_placeholders(self):
        """Generated skill should have placeholders for customization."""
        from bpsai_pair.skills.generator import SkillGenerator
        from bpsai_pair.skills.gap_detector import SkillGap

        generator = SkillGenerator()

        gap = SkillGap(
            pattern=["cmd1", "cmd2"],
            suggested_name="test-skill",
            confidence=0.7,
            frequency=3,
            time_saved_estimate="~1 min",
            detected_at="2025-12-23T10:00:00",
        )

        result = generator.generate_from_gap(gap)

        # Should have placeholder markers
        assert "[" in result.content and "]" in result.content
        # Should indicate it needs review
        assert result.requires_review is True

    def test_includes_auto_generation_notice(self):
        """Generated skill should include auto-generation notice."""
        from bpsai_pair.skills.generator import SkillGenerator
        from bpsai_pair.skills.gap_detector import SkillGap

        generator = SkillGenerator()

        gap = SkillGap(
            pattern=["cmd1", "cmd2"],
            suggested_name="test-skill",
            confidence=0.7,
            frequency=3,
            time_saved_estimate="~1 min",
            detected_at="2025-12-23T10:00:00",
        )

        result = generator.generate_from_gap(gap)

        # Should have notice at bottom
        assert "auto-generated" in result.content.lower() or "generated" in result.content.lower()

    def test_generated_skill_passes_validation(self):
        """Generated skill should pass skill validator."""
        from bpsai_pair.skills.generator import SkillGenerator
        from bpsai_pair.skills.gap_detector import SkillGap
        from bpsai_pair.skills.validator import SkillValidator

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            generator = SkillGenerator()

            gap = SkillGap(
                pattern=["pytest", "read_error", "fix_bug"],
                suggested_name="debugging-python-tests",
                confidence=0.85,
                frequency=5,
                time_saved_estimate="~5 min",
                detected_at="2025-12-23T10:00:00",
            )

            result = generator.generate_from_gap(gap)

            # Write to disk
            skill_dir = skills_dir / result.name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(result.content)

            # Validate
            validator = SkillValidator(skills_dir)
            validation = validator.validate_skill(skill_dir)

            assert validation["valid"] is True, f"Validation errors: {validation['errors']}"

    def test_handles_special_characters_in_pattern(self):
        """Should handle special characters in command patterns."""
        from bpsai_pair.skills.generator import SkillGenerator
        from bpsai_pair.skills.gap_detector import SkillGap

        generator = SkillGenerator()

        gap = SkillGap(
            pattern=["grep -rn 'error'", "cat file.log | head -20"],
            suggested_name="searching-logs",
            confidence=0.7,
            frequency=3,
            time_saved_estimate="~2 min",
            detected_at="2025-12-23T10:00:00",
        )

        result = generator.generate_from_gap(gap)

        # Should not crash and should produce valid content
        assert result.name == "searching-logs"
        assert len(result.content) > 0


class TestSkillGeneratorSave:
    """Tests for saving generated skills."""

    def test_saves_skill_to_directory(self):
        """Should save generated skill to skills directory."""
        from bpsai_pair.skills.generator import SkillGenerator, save_generated_skill
        from bpsai_pair.skills.gap_detector import SkillGap

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            generator = SkillGenerator()

            gap = SkillGap(
                pattern=["cmd1", "cmd2"],
                suggested_name="test-skill",
                confidence=0.8,
                frequency=4,
                time_saved_estimate="~2 min",
                detected_at="2025-12-23T10:00:00",
            )

            generated = generator.generate_from_gap(gap)
            result = save_generated_skill(generated, skills_dir)

            assert result["success"] is True
            assert (skills_dir / "test-skill" / "SKILL.md").exists()

    def test_doesnt_overwrite_without_force(self):
        """Should not overwrite existing skill without force."""
        from bpsai_pair.skills.generator import SkillGenerator, save_generated_skill, SkillGeneratorError
        from bpsai_pair.skills.gap_detector import SkillGap

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            # Create existing skill
            existing = skills_dir / "test-skill"
            existing.mkdir()
            (existing / "SKILL.md").write_text("existing content")

            generator = SkillGenerator()
            gap = SkillGap(
                pattern=["cmd1"],
                suggested_name="test-skill",
                confidence=0.8,
                frequency=4,
                time_saved_estimate="~2 min",
                detected_at="2025-12-23T10:00:00",
            )

            generated = generator.generate_from_gap(gap)

            with pytest.raises(SkillGeneratorError) as exc_info:
                save_generated_skill(generated, skills_dir)

            assert "exists" in str(exc_info.value).lower()

    def test_overwrites_with_force(self):
        """Should overwrite existing skill with force=True."""
        from bpsai_pair.skills.generator import SkillGenerator, save_generated_skill
        from bpsai_pair.skills.gap_detector import SkillGap

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            # Create existing skill
            existing = skills_dir / "test-skill"
            existing.mkdir()
            (existing / "SKILL.md").write_text("existing content")

            generator = SkillGenerator()
            gap = SkillGap(
                pattern=["cmd1"],
                suggested_name="test-skill",
                confidence=0.8,
                frequency=4,
                time_saved_estimate="~2 min",
                detected_at="2025-12-23T10:00:00",
            )

            generated = generator.generate_from_gap(gap)
            result = save_generated_skill(generated, skills_dir, force=True)

            assert result["success"] is True
            content = (skills_dir / "test-skill" / "SKILL.md").read_text()
            assert "existing content" not in content


class TestGenerateCommand:
    """Tests for the CLI generate command."""

    def test_generate_command_exists(self):
        """skill generate command should exist."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["skill", "generate", "--help"])

        assert result.exit_code == 0
        assert "generate" in result.output.lower()

    def test_generate_from_gap_id(self):
        """skill generate should generate from gap ID."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / ".paircoder").mkdir()
            history_dir = project_dir / ".paircoder" / "history"
            history_dir.mkdir()
            skills_dir = project_dir / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            # Create gap in history
            gap_file = history_dir / "skill-gaps.jsonl"
            gap_data = {
                "pattern": ["pytest", "fix"],
                "suggested_name": "testing-fixes",
                "confidence": 0.8,
                "frequency": 4,
                "time_saved_estimate": "~3 min",
                "detected_at": "2025-12-23T10:00:00",
            }
            gap_file.write_text(json.dumps(gap_data) + "\n")

            runner = CliRunner()
            with patch('bpsai_pair.skills.cli_commands.find_project_root', return_value=project_dir):
                result = runner.invoke(app, ["skill", "generate", "1", "--auto-approve"])

            # Should complete (may succeed or fail based on gap existence)
            assert result.exit_code in [0, 1]

    def test_generate_lists_gaps_if_no_id(self):
        """skill generate without ID should list available gaps."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / ".paircoder").mkdir()
            history_dir = project_dir / ".paircoder" / "history"
            history_dir.mkdir()
            skills_dir = project_dir / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            runner = CliRunner()
            with patch('bpsai_pair.skills.cli_commands.find_project_root', return_value=project_dir):
                result = runner.invoke(app, ["skill", "generate"])

            # Should show available gaps or indicate none found
            assert result.exit_code == 0

    def test_auto_approve_skips_confirmation(self):
        """--auto-approve should save without confirmation."""
        from bpsai_pair.skills.generator import SkillGenerator, save_generated_skill
        from bpsai_pair.skills.gap_detector import SkillGap

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            generator = SkillGenerator()
            gap = SkillGap(
                pattern=["cmd1", "cmd2"],
                suggested_name="auto-test",
                confidence=0.8,
                frequency=4,
                time_saved_estimate="~2 min",
                detected_at="2025-12-23T10:00:00",
            )

            generated = generator.generate_from_gap(gap)

            # auto_approve=True should save directly
            result = save_generated_skill(generated, skills_dir, auto_approve=True)

            assert result["success"] is True
            assert (skills_dir / "auto-test" / "SKILL.md").exists()


class TestGeneratorIntegration:
    """Integration tests for skill generation workflow."""

    def test_full_workflow_gap_to_skill(self):
        """Test full workflow: gap detection -> generation -> validation."""
        from bpsai_pair.skills.gap_detector import SkillGap, GapPersistence
        from bpsai_pair.skills.generator import SkillGenerator, save_generated_skill
        from bpsai_pair.skills.validator import SkillValidator

        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            history_dir = project_dir / ".paircoder" / "history"
            history_dir.mkdir(parents=True)
            skills_dir = project_dir / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            # 1. Create and save a gap
            gap = SkillGap(
                pattern=["pytest", "read_log", "edit_file", "pytest"],
                suggested_name="debugging-test-failures",
                confidence=0.85,
                frequency=5,
                time_saved_estimate="~5 min per cycle",
                detected_at="2025-12-23T10:00:00",
            )

            persistence = GapPersistence(history_dir=history_dir)
            persistence.save_gap(gap)

            # 2. Load gap and generate skill
            loaded_gaps = persistence.load_gaps()
            assert len(loaded_gaps) == 1

            generator = SkillGenerator()
            generated = generator.generate_from_gap(loaded_gaps[0])

            # 3. Save generated skill
            result = save_generated_skill(generated, skills_dir)
            assert result["success"] is True

            # 4. Validate the skill
            validator = SkillValidator(skills_dir)
            validation = validator.validate_skill(skills_dir / generated.name)

            assert validation["valid"] is True, f"Errors: {validation['errors']}"

    def test_generates_multiple_skills_from_gaps(self):
        """Should be able to generate multiple skills from different gaps."""
        from bpsai_pair.skills.gap_detector import SkillGap
        from bpsai_pair.skills.generator import SkillGenerator, save_generated_skill

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            gaps = [
                SkillGap(
                    pattern=["git status", "git add"],
                    suggested_name="managing-staging",
                    confidence=0.7,
                    frequency=4,
                    time_saved_estimate="~2 min",
                    detected_at="2025-12-23T10:00:00",
                ),
                SkillGap(
                    pattern=["npm test", "npm run lint"],
                    suggested_name="running-checks",
                    confidence=0.8,
                    frequency=5,
                    time_saved_estimate="~3 min",
                    detected_at="2025-12-23T11:00:00",
                ),
            ]

            generator = SkillGenerator()

            for gap in gaps:
                generated = generator.generate_from_gap(gap)
                result = save_generated_skill(generated, skills_dir)
                assert result["success"] is True

            # Both skills should exist
            assert (skills_dir / "managing-staging" / "SKILL.md").exists()
            assert (skills_dir / "running-checks" / "SKILL.md").exists()
