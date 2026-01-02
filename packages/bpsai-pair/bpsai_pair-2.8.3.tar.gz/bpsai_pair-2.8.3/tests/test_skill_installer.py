"""Tests for skill installer module."""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
import json


class TestParseSource:
    """Tests for source parsing."""

    def test_parses_local_path(self):
        """Should detect local path source."""
        from bpsai_pair.skills.installer import parse_source, SkillSource

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("---\nname: my-skill\n---\n")

            source_type, path = parse_source(str(skill_dir))

            assert source_type == SkillSource.PATH
            assert path == str(skill_dir)

    def test_parses_github_tree_url(self):
        """Should detect GitHub tree URL source."""
        from bpsai_pair.skills.installer import parse_source, SkillSource

        url = "https://github.com/user/repo/tree/main/.claude/skills/my-skill"
        source_type, parsed = parse_source(url)

        assert source_type == SkillSource.URL
        assert "github.com" in parsed

    def test_parses_github_blob_url(self):
        """Should detect GitHub blob URL and convert to tree URL."""
        from bpsai_pair.skills.installer import parse_source, SkillSource

        url = "https://github.com/user/repo/blob/main/.claude/skills/my-skill/SKILL.md"
        source_type, parsed = parse_source(url)

        assert source_type == SkillSource.URL

    def test_invalid_source_raises_error(self):
        """Should raise error for invalid source."""
        from bpsai_pair.skills.installer import parse_source, SkillInstallerError

        with pytest.raises(SkillInstallerError):
            parse_source("/nonexistent/path/to/skill")


class TestInstallFromPath:
    """Tests for installing from local path."""

    def test_installs_valid_skill(self):
        """Should install a valid skill from local path."""
        from bpsai_pair.skills.installer import install_from_path

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source skill
            source_dir = Path(tmpdir) / "source" / "my-skill"
            source_dir.mkdir(parents=True)
            (source_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill for installation.
---

# My Skill

Content here.
""")
            (source_dir / "reference").mkdir()
            (source_dir / "reference" / "doc.md").write_text("# Reference doc")

            # Create target directory
            target_dir = Path(tmpdir) / "target" / ".claude" / "skills"
            target_dir.mkdir(parents=True)

            result = install_from_path(source_dir, target_dir)

            assert result["success"] is True
            assert (target_dir / "my-skill" / "SKILL.md").exists()
            assert (target_dir / "my-skill" / "reference" / "doc.md").exists()

    def test_validates_skill_before_install(self):
        """Should reject invalid skill during installation."""
        from bpsai_pair.skills.installer import install_from_path, SkillInstallerError

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create invalid skill (missing description)
            source_dir = Path(tmpdir) / "source" / "bad-skill"
            source_dir.mkdir(parents=True)
            (source_dir / "SKILL.md").write_text("""---
name: bad-skill
---

# Bad Skill
""")

            target_dir = Path(tmpdir) / "target" / ".claude" / "skills"
            target_dir.mkdir(parents=True)

            with pytest.raises(SkillInstallerError) as exc_info:
                install_from_path(source_dir, target_dir)

            assert "validation" in str(exc_info.value).lower()

    def test_detects_naming_conflict(self):
        """Should detect when skill name already exists."""
        from bpsai_pair.skills.installer import install_from_path, SkillInstallerError

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source skill
            source_dir = Path(tmpdir) / "source" / "my-skill"
            source_dir.mkdir(parents=True)
            (source_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill.
---

# My Skill
""")

            # Create target with existing skill
            target_dir = Path(tmpdir) / "target" / ".claude" / "skills"
            target_dir.mkdir(parents=True)
            existing_skill = target_dir / "my-skill"
            existing_skill.mkdir()
            (existing_skill / "SKILL.md").write_text("existing")

            with pytest.raises(SkillInstallerError) as exc_info:
                install_from_path(source_dir, target_dir)

            assert "conflict" in str(exc_info.value).lower() or "exists" in str(exc_info.value).lower()

    def test_force_overwrites_existing(self):
        """--force should overwrite existing skill."""
        from bpsai_pair.skills.installer import install_from_path

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source skill
            source_dir = Path(tmpdir) / "source" / "my-skill"
            source_dir.mkdir(parents=True)
            (source_dir / "SKILL.md").write_text("""---
name: my-skill
description: New version of skill.
---

# My Skill - New
""")

            # Create target with existing skill
            target_dir = Path(tmpdir) / "target" / ".claude" / "skills"
            target_dir.mkdir(parents=True)
            existing_skill = target_dir / "my-skill"
            existing_skill.mkdir()
            (existing_skill / "SKILL.md").write_text("""---
name: my-skill
description: Old version.
---

# Old
""")

            result = install_from_path(source_dir, target_dir, force=True)

            assert result["success"] is True
            content = (target_dir / "my-skill" / "SKILL.md").read_text()
            assert "New version" in content

    def test_rename_with_name_flag(self):
        """--name should install skill with different name."""
        from bpsai_pair.skills.installer import install_from_path

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source skill
            source_dir = Path(tmpdir) / "source" / "my-skill"
            source_dir.mkdir(parents=True)
            (source_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill.
---

# My Skill
""")

            target_dir = Path(tmpdir) / "target" / ".claude" / "skills"
            target_dir.mkdir(parents=True)

            result = install_from_path(source_dir, target_dir, name="renamed-skill")

            assert result["success"] is True
            assert (target_dir / "renamed-skill" / "SKILL.md").exists()
            # Check that frontmatter name was updated
            content = (target_dir / "renamed-skill" / "SKILL.md").read_text()
            assert "name: renamed-skill" in content


class TestInstallFromURL:
    """Tests for installing from GitHub URL."""

    def test_downloads_and_installs_skill(self):
        """Should download skill from GitHub and install it."""
        from bpsai_pair.skills.installer import install_from_url

        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / ".claude" / "skills"
            target_dir.mkdir(parents=True)

            # Mock the GitHub API responses
            skill_content = """---
name: remote-skill
description: A skill from GitHub.
---

# Remote Skill

Content.
"""
            with patch('bpsai_pair.skills.installer._download_github_skill') as mock_download:
                mock_download.return_value = {
                    "SKILL.md": skill_content,
                }

                result = install_from_url(
                    "https://github.com/user/repo/tree/main/.claude/skills/remote-skill",
                    target_dir
                )

            assert result["success"] is True
            assert (target_dir / "remote-skill" / "SKILL.md").exists()

    def test_handles_download_error(self):
        """Should handle network errors gracefully."""
        from bpsai_pair.skills.installer import install_from_url, SkillInstallerError

        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / ".claude" / "skills"
            target_dir.mkdir(parents=True)

            with patch('bpsai_pair.skills.installer._download_github_skill') as mock_download:
                mock_download.side_effect = Exception("Network error")

                with pytest.raises(SkillInstallerError) as exc_info:
                    install_from_url(
                        "https://github.com/user/repo/tree/main/.claude/skills/my-skill",
                        target_dir
                    )

                assert "download" in str(exc_info.value).lower() or "network" in str(exc_info.value).lower()


class TestCheckConflicts:
    """Tests for conflict detection."""

    def test_no_conflict_with_empty_target(self):
        """Should return no conflict when target is empty."""
        from bpsai_pair.skills.installer import check_conflicts

        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)

            has_conflict = check_conflicts("new-skill", target_dir)

            assert has_conflict is False

    def test_detects_existing_skill(self):
        """Should detect existing skill with same name."""
        from bpsai_pair.skills.installer import check_conflicts

        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)
            existing = target_dir / "my-skill"
            existing.mkdir()
            (existing / "SKILL.md").write_text("existing")

            has_conflict = check_conflicts("my-skill", target_dir)

            assert has_conflict is True


class TestGetTargetDir:
    """Tests for target directory selection."""

    def test_project_target(self):
        """Should return project .claude/skills directory."""
        from bpsai_pair.skills.installer import get_target_dir

        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / ".paircoder").mkdir()

            with patch('bpsai_pair.skills.installer.find_project_root', return_value=project_dir):
                target = get_target_dir(project=True, personal=False)

            assert ".claude/skills" in str(target)

    def test_personal_target(self):
        """Should return ~/.claude/skills directory."""
        from bpsai_pair.skills.installer import get_target_dir

        target = get_target_dir(project=False, personal=True)

        assert ".claude/skills" in str(target)
        assert str(Path.home()) in str(target)


class TestCLIInstallCommand:
    """Tests for the CLI skill install command."""

    def test_install_command_exists(self):
        """skill install command should exist."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["skill", "install", "--help"])

        assert result.exit_code == 0
        assert "install" in result.output.lower()

    def test_install_requires_source(self):
        """skill install should require source argument."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["skill", "install"])

        # Should fail without source argument
        assert result.exit_code != 0

    def test_install_with_project_flag(self):
        """skill install --project should skip prompt."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source skill
            source_dir = Path(tmpdir) / "my-skill"
            source_dir.mkdir()
            (source_dir / "SKILL.md").write_text("""---
name: my-skill
description: Test skill for CLI.
---

# My Skill
""")

            # Create project structure
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()
            (project_dir / ".paircoder").mkdir()
            skills_dir = project_dir / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            runner = CliRunner()
            with patch('bpsai_pair.skills.installer.find_project_root', return_value=project_dir):
                with patch('bpsai_pair.skills.cli_commands.find_project_root', return_value=project_dir):
                    result = runner.invoke(app, ["skill", "install", str(source_dir), "--project"])

            assert result.exit_code == 0
            assert "installed" in result.output.lower() or "success" in result.output.lower()

    def test_install_with_name_flag(self):
        """skill install --name should rename skill."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source skill
            source_dir = Path(tmpdir) / "original-skill"
            source_dir.mkdir()
            (source_dir / "SKILL.md").write_text("""---
name: original-skill
description: Test skill for CLI.
---

# Original Skill
""")

            # Create project structure
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()
            (project_dir / ".paircoder").mkdir()
            skills_dir = project_dir / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            runner = CliRunner()
            with patch('bpsai_pair.skills.installer.find_project_root', return_value=project_dir):
                with patch('bpsai_pair.skills.cli_commands.find_project_root', return_value=project_dir):
                    result = runner.invoke(app, ["skill", "install", str(source_dir), "--project", "--name", "new-name"])

            assert result.exit_code == 0
            assert (skills_dir / "new-name" / "SKILL.md").exists()

    def test_install_with_force_flag(self):
        """skill install --force should overwrite existing."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source skill
            source_dir = Path(tmpdir) / "my-skill"
            source_dir.mkdir()
            (source_dir / "SKILL.md").write_text("""---
name: my-skill
description: New version.
---

# New
""")

            # Create project structure with existing skill
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()
            (project_dir / ".paircoder").mkdir()
            skills_dir = project_dir / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            existing = skills_dir / "my-skill"
            existing.mkdir()
            (existing / "SKILL.md").write_text("""---
name: my-skill
description: Old version.
---

# Old
""")

            runner = CliRunner()
            with patch('bpsai_pair.skills.installer.find_project_root', return_value=project_dir):
                with patch('bpsai_pair.skills.cli_commands.find_project_root', return_value=project_dir):
                    result = runner.invoke(app, ["skill", "install", str(source_dir), "--project", "--force"])

            assert result.exit_code == 0
            content = (skills_dir / "my-skill" / "SKILL.md").read_text()
            assert "New version" in content


class TestGitHubURLParsing:
    """Tests for GitHub URL parsing."""

    def test_parses_tree_url(self):
        """Should parse GitHub tree URL correctly."""
        from bpsai_pair.skills.installer import parse_github_url

        url = "https://github.com/BPSAI/paircoder/tree/main/.claude/skills/reviewing-code"
        result = parse_github_url(url)

        assert result["owner"] == "BPSAI"
        assert result["repo"] == "paircoder"
        assert result["branch"] == "main"
        assert result["path"] == ".claude/skills/reviewing-code"

    def test_parses_blob_url(self):
        """Should parse GitHub blob URL and extract skill path."""
        from bpsai_pair.skills.installer import parse_github_url

        url = "https://github.com/user/repo/blob/main/.claude/skills/my-skill/SKILL.md"
        result = parse_github_url(url)

        assert result["owner"] == "user"
        assert result["repo"] == "repo"
        assert result["branch"] == "main"
        # Should extract skill directory path, not file path
        assert "SKILL.md" not in result["path"]

    def test_handles_different_branches(self):
        """Should handle different branch names."""
        from bpsai_pair.skills.installer import parse_github_url

        url = "https://github.com/user/repo/tree/feature/branch/.claude/skills/skill"
        result = parse_github_url(url)

        assert result["branch"] == "feature/branch"


class TestExtractSkillName:
    """Tests for skill name extraction."""

    def test_extracts_from_directory(self):
        """Should extract skill name from directory path."""
        from bpsai_pair.skills.installer import extract_skill_name

        name = extract_skill_name("/path/to/.claude/skills/my-skill")
        assert name == "my-skill"

    def test_extracts_from_url(self):
        """Should extract skill name from GitHub URL."""
        from bpsai_pair.skills.installer import extract_skill_name

        name = extract_skill_name("https://github.com/user/repo/tree/main/.claude/skills/remote-skill")
        assert name == "remote-skill"
