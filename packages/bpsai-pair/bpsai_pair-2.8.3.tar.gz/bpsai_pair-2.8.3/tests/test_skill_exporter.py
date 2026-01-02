"""Tests for skill exporter module."""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestExportFormat:
    """Tests for export format enum."""

    def test_cursor_format_exists(self):
        """Should have Cursor export format."""
        from bpsai_pair.skills.exporter import ExportFormat

        assert ExportFormat.CURSOR.value == "cursor"

    def test_continue_format_exists(self):
        """Should have Continue.dev export format."""
        from bpsai_pair.skills.exporter import ExportFormat

        assert ExportFormat.CONTINUE.value == "continue"

    def test_windsurf_format_exists(self):
        """Should have Windsurf export format."""
        from bpsai_pair.skills.exporter import ExportFormat

        assert ExportFormat.WINDSURF.value == "windsurf"

    def test_codex_format_exists(self):
        """Should have Codex CLI export format."""
        from bpsai_pair.skills.exporter import ExportFormat

        assert ExportFormat.CODEX.value == "codex"

    def test_chatgpt_format_exists(self):
        """Should have ChatGPT export format."""
        from bpsai_pair.skills.exporter import ExportFormat

        assert ExportFormat.CHATGPT.value == "chatgpt"

    def test_all_format_exists(self):
        """Should have ALL export format for bulk export."""
        from bpsai_pair.skills.exporter import ExportFormat

        assert ExportFormat.ALL.value == "all"


class TestExportToCursor:
    """Tests for Cursor export format."""

    def test_exports_skill_to_cursor_rules(self):
        """Should export skill to .cursor/rules/ directory."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create skill
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A helpful skill for coding.
---

# My Skill

## Instructions

Follow these steps:
1. Do something
2. Do something else
""")

            project_dir = Path(tmpdir)
            result = export_skill(
                skill_name="my-skill",
                format=ExportFormat.CURSOR,
                skills_dir=skills_dir,
                project_dir=project_dir,
            )

            assert result["success"] is True
            cursor_file = project_dir / ".cursor" / "rules" / "my-skill.md"
            assert cursor_file.exists()

    def test_cursor_export_strips_frontmatter(self):
        """Should strip YAML frontmatter from Cursor export."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A helpful skill.
---

# My Skill

Content here.
""")

            project_dir = Path(tmpdir)
            export_skill(
                skill_name="my-skill",
                format=ExportFormat.CURSOR,
                skills_dir=skills_dir,
                project_dir=project_dir,
            )

            cursor_file = project_dir / ".cursor" / "rules" / "my-skill.md"
            content = cursor_file.read_text()

            # Should not contain frontmatter delimiters
            assert "---" not in content or content.count("---") == 0
            assert "name: my-skill" not in content
            # Should contain the actual content
            assert "# My Skill" in content
            assert "Content here." in content

    def test_cursor_export_adds_metadata_comment(self):
        """Should add metadata comment to Cursor export."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: Test skill.
---

# Content
""")

            project_dir = Path(tmpdir)
            export_skill(
                skill_name="my-skill",
                format=ExportFormat.CURSOR,
                skills_dir=skills_dir,
                project_dir=project_dir,
            )

            cursor_file = project_dir / ".cursor" / "rules" / "my-skill.md"
            content = cursor_file.read_text()

            # Should have metadata comment
            assert "Exported from" in content or "bpsai-pair" in content.lower()


class TestExportToContinue:
    """Tests for Continue.dev export format."""

    def test_exports_skill_to_continue_context(self):
        """Should export skill to .continue/context/ directory."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A helpful skill.
---

# My Skill

Instructions here.
""")

            project_dir = Path(tmpdir)
            result = export_skill(
                skill_name="my-skill",
                format=ExportFormat.CONTINUE,
                skills_dir=skills_dir,
                project_dir=project_dir,
            )

            assert result["success"] is True
            continue_file = project_dir / ".continue" / "context" / "my-skill.md"
            assert continue_file.exists()


class TestExportToWindsurf:
    """Tests for Windsurf export format."""

    def test_exports_skill_to_windsurfrules(self):
        """Should append skill to .windsurfrules file."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A helpful skill.
---

# My Skill

Instructions here.
""")

            project_dir = Path(tmpdir)
            result = export_skill(
                skill_name="my-skill",
                format=ExportFormat.WINDSURF,
                skills_dir=skills_dir,
                project_dir=project_dir,
            )

            assert result["success"] is True
            windsurf_file = project_dir / ".windsurfrules"
            assert windsurf_file.exists()
            content = windsurf_file.read_text()
            assert "my-skill" in content.lower()

    def test_windsurf_export_uses_section_markers(self):
        """Should use section markers for organization in Windsurf."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A helpful skill.
---

# Content
""")

            project_dir = Path(tmpdir)
            export_skill(
                skill_name="my-skill",
                format=ExportFormat.WINDSURF,
                skills_dir=skills_dir,
                project_dir=project_dir,
            )

            windsurf_file = project_dir / ".windsurfrules"
            content = windsurf_file.read_text()

            # Should have section markers
            assert "BEGIN" in content or "---" in content or "##" in content

    def test_windsurf_export_appends_to_existing(self):
        """Should append to existing .windsurfrules file."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A helpful skill.
---

# Content
""")

            project_dir = Path(tmpdir)
            # Create existing .windsurfrules
            existing_rules = project_dir / ".windsurfrules"
            existing_rules.write_text("# Existing rules\n\nDo something.\n")

            export_skill(
                skill_name="my-skill",
                format=ExportFormat.WINDSURF,
                skills_dir=skills_dir,
                project_dir=project_dir,
            )

            content = existing_rules.read_text()
            # Should contain both existing and new content
            assert "Existing rules" in content
            assert "my-skill" in content.lower()


class TestExportToCodex:
    """Tests for Codex CLI export format."""

    def test_exports_skill_to_codex_directory(self):
        """Should export skill to ~/.codex/skills/ directory."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A helpful skill for coding.
---

# My Skill

## Instructions

Follow these steps.
""")

            project_dir = Path(tmpdir)
            # Mock home directory to avoid writing to real home
            with patch('pathlib.Path.home', return_value=Path(tmpdir)):
                result = export_skill(
                    skill_name="my-skill",
                    format=ExportFormat.CODEX,
                    skills_dir=skills_dir,
                    project_dir=project_dir,
                )

            assert result["success"] is True
            assert "codex" in result["path"].lower()
            codex_file = Path(tmpdir) / ".codex" / "skills" / "my-skill" / "SKILL.md"
            assert codex_file.exists()

    def test_codex_export_preserves_content(self):
        """Codex export should preserve original content (same format as Claude)."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            original_content = """---
name: my-skill
description: Test skill.
---

# My Skill

Content preserved exactly.
"""
            (skill_dir / "SKILL.md").write_text(original_content)

            project_dir = Path(tmpdir)
            with patch('pathlib.Path.home', return_value=Path(tmpdir)):
                export_skill(
                    skill_name="my-skill",
                    format=ExportFormat.CODEX,
                    skills_dir=skills_dir,
                    project_dir=project_dir,
                )

            codex_file = Path(tmpdir) / ".codex" / "skills" / "my-skill" / "SKILL.md"
            exported_content = codex_file.read_text()
            # Codex uses same format as Claude Code
            assert exported_content == original_content


class TestExportToChatGPT:
    """Tests for ChatGPT export format."""

    def test_exports_skill_to_chatgpt_directory(self):
        """Should export skill to ./chatgpt-skills/ directory."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A helpful skill for coding.
---

# My Skill

Instructions here.
""")

            project_dir = Path(tmpdir)
            result = export_skill(
                skill_name="my-skill",
                format=ExportFormat.CHATGPT,
                skills_dir=skills_dir,
                project_dir=project_dir,
            )

            assert result["success"] is True
            chatgpt_file = project_dir / "chatgpt-skills" / "my-skill" / "skill.md"
            assert chatgpt_file.exists()

    def test_chatgpt_export_strips_frontmatter(self):
        """ChatGPT export should strip YAML frontmatter."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A helpful skill.
---

# My Skill

Content here.
""")

            project_dir = Path(tmpdir)
            export_skill(
                skill_name="my-skill",
                format=ExportFormat.CHATGPT,
                skills_dir=skills_dir,
                project_dir=project_dir,
            )

            chatgpt_file = project_dir / "chatgpt-skills" / "my-skill" / "skill.md"
            content = chatgpt_file.read_text()

            # Should not contain YAML frontmatter delimiters
            assert "name: my-skill" not in content
            # Should contain the content
            assert "Content here" in content

    def test_chatgpt_export_uses_title_case_name(self):
        """ChatGPT export should convert skill name to title case."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-test-skill
description: Test skill.
---

# Content
""")

            project_dir = Path(tmpdir)
            export_skill(
                skill_name="my-test-skill",
                format=ExportFormat.CHATGPT,
                skills_dir=skills_dir,
                project_dir=project_dir,
            )

            chatgpt_file = project_dir / "chatgpt-skills" / "my-test-skill" / "skill.md"
            content = chatgpt_file.read_text()

            # Should have title-cased name as heading
            assert "# My Test Skill" in content

    def test_chatgpt_export_adds_export_footer(self):
        """ChatGPT export should add footer noting export source."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: Test skill.
---

# Content
""")

            project_dir = Path(tmpdir)
            export_skill(
                skill_name="my-skill",
                format=ExportFormat.CHATGPT,
                skills_dir=skills_dir,
                project_dir=project_dir,
            )

            chatgpt_file = project_dir / "chatgpt-skills" / "my-skill" / "skill.md"
            content = chatgpt_file.read_text()

            # Should have export footer
            assert "Exported from PairCoder" in content


class TestExportToAllFormats:
    """Tests for exporting to all formats at once."""

    def test_exports_to_all_formats(self):
        """--format all should export to all supported formats."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A helpful skill.
---

# My Skill

Content.
""")

            project_dir = Path(tmpdir)
            with patch('pathlib.Path.home', return_value=Path(tmpdir)):
                result = export_skill(
                    skill_name="my-skill",
                    format=ExportFormat.ALL,
                    skills_dir=skills_dir,
                    project_dir=project_dir,
                )

            assert result["success"] is True
            assert result["format"] == "all"
            assert "exported_to" in result
            # Should have exported to multiple formats
            assert len(result["exported_to"]) > 1

    def test_all_format_returns_summary(self):
        """ALL format should return a summary of exports."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: Test.
---

# Content
""")

            project_dir = Path(tmpdir)
            with patch('pathlib.Path.home', return_value=Path(tmpdir)):
                result = export_skill(
                    skill_name="my-skill",
                    format=ExportFormat.ALL,
                    skills_dir=skills_dir,
                    project_dir=project_dir,
                )

            assert "summary" in result
            assert "Exported to" in result["summary"]


class TestExportAll:
    """Tests for exporting all skills."""

    def test_exports_all_skills(self):
        """Should export all skills in directory."""
        from bpsai_pair.skills.exporter import export_all_skills, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            # Create two skills
            for name in ["skill-one", "skill-two"]:
                skill_dir = skills_dir / name
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(f"""---
name: {name}
description: Skill {name}.
---

# {name}

Content.
""")

            project_dir = Path(tmpdir)
            results = export_all_skills(
                format=ExportFormat.CURSOR,
                skills_dir=skills_dir,
                project_dir=project_dir,
            )

            assert len(results) == 2
            assert all(r["success"] for r in results)
            assert (project_dir / ".cursor" / "rules" / "skill-one.md").exists()
            assert (project_dir / ".cursor" / "rules" / "skill-two.md").exists()


class TestDryRun:
    """Tests for dry-run mode."""

    def test_dry_run_does_not_create_files(self):
        """--dry-run should not create any files."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A helpful skill.
---

# Content
""")

            project_dir = Path(tmpdir)
            result = export_skill(
                skill_name="my-skill",
                format=ExportFormat.CURSOR,
                skills_dir=skills_dir,
                project_dir=project_dir,
                dry_run=True,
            )

            assert result["success"] is True
            assert result.get("dry_run") is True
            # Should not create any files
            assert not (project_dir / ".cursor").exists()

    def test_dry_run_shows_what_would_be_created(self):
        """--dry-run should show what would be created."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A helpful skill.
---

# Content
""")

            project_dir = Path(tmpdir)
            result = export_skill(
                skill_name="my-skill",
                format=ExportFormat.CURSOR,
                skills_dir=skills_dir,
                project_dir=project_dir,
                dry_run=True,
            )

            # Should include path that would be created
            assert "would_create" in result or "path" in result


class TestErrorHandling:
    """Tests for error handling."""

    def test_skill_not_found_error(self):
        """Should error when skill doesn't exist."""
        from bpsai_pair.skills.exporter import export_skill, ExportFormat, SkillExporterError

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            with pytest.raises(SkillExporterError) as exc_info:
                export_skill(
                    skill_name="nonexistent",
                    format=ExportFormat.CURSOR,
                    skills_dir=skills_dir,
                    project_dir=Path(tmpdir),
                )

            assert "not found" in str(exc_info.value).lower()

    def test_invalid_format_error(self):
        """Should error for invalid export format."""
        from bpsai_pair.skills.exporter import export_skill, SkillExporterError

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: Test.
---

# Content
""")

            with pytest.raises((SkillExporterError, ValueError)):
                export_skill(
                    skill_name="my-skill",
                    format="invalid_format",
                    skills_dir=skills_dir,
                    project_dir=Path(tmpdir),
                )


class TestPortabilityWarnings:
    """Tests for portability warnings."""

    def test_warns_for_skills_with_scripts(self):
        """Should warn when skill has scripts directory."""
        from bpsai_pair.skills.exporter import check_portability

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: Test.
---

# Content
""")
            # Add scripts directory
            (skill_dir / "scripts").mkdir()
            (skill_dir / "scripts" / "run.py").write_text("print('hello')")

            warnings = check_portability(skill_dir)

            assert len(warnings) > 0
            assert any("script" in w.lower() for w in warnings)

    def test_no_warnings_for_portable_skill(self):
        """Should have no warnings for simple portable skill."""
        from bpsai_pair.skills.exporter import check_portability

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: Simple portable skill.
---

# My Skill

Just instructions, no scripts.
""")

            warnings = check_portability(skill_dir)

            assert len(warnings) == 0


class TestCLIExportCommand:
    """Tests for CLI export command."""

    def test_export_command_exists(self):
        """skill export command should exist."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["skill", "export", "--help"])

        assert result.exit_code == 0
        assert "export" in result.output.lower()

    def test_export_requires_skill_or_all(self):
        """skill export should require skill name or --all flag."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["skill", "export", "--format", "cursor"])

        # Should fail without skill name and without --all
        assert result.exit_code != 0

    def test_export_with_format_flag(self):
        """skill export should accept --format flag."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create project structure
            project_dir = Path(tmpdir)
            (project_dir / ".paircoder").mkdir()
            skills_dir = project_dir / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: Test skill.
---

# Content
""")

            runner = CliRunner()
            with patch('bpsai_pair.skills.exporter.find_project_root', return_value=project_dir):
                with patch('bpsai_pair.skills.cli_commands.find_project_root', return_value=project_dir):
                    with patch('bpsai_pair.skills.cli_commands.find_skills_dir', return_value=skills_dir):
                        result = runner.invoke(app, ["skill", "export", "my-skill", "--format", "cursor"])

            assert result.exit_code == 0

    def test_export_all_flag(self):
        """skill export --all should export all skills."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / ".paircoder").mkdir()
            skills_dir = project_dir / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            for name in ["skill-a", "skill-b"]:
                skill_dir = skills_dir / name
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(f"""---
name: {name}
description: Test.
---

# Content
""")

            runner = CliRunner()
            with patch('bpsai_pair.skills.exporter.find_project_root', return_value=project_dir):
                with patch('bpsai_pair.skills.cli_commands.find_project_root', return_value=project_dir):
                    with patch('bpsai_pair.skills.cli_commands.find_skills_dir', return_value=skills_dir):
                        result = runner.invoke(app, ["skill", "export", "--all", "--format", "cursor"])

            assert result.exit_code == 0

    def test_export_dry_run_flag(self):
        """skill export --dry-run should not create files."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / ".paircoder").mkdir()
            skills_dir = project_dir / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            skill_dir = skills_dir / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: Test.
---

# Content
""")

            runner = CliRunner()
            with patch('bpsai_pair.skills.exporter.find_project_root', return_value=project_dir):
                with patch('bpsai_pair.skills.cli_commands.find_project_root', return_value=project_dir):
                    with patch('bpsai_pair.skills.cli_commands.find_skills_dir', return_value=skills_dir):
                        result = runner.invoke(app, ["skill", "export", "my-skill", "--format", "cursor", "--dry-run"])

            assert result.exit_code == 0
            assert not (project_dir / ".cursor").exists()
