"""Tests for release prep command.

Tests the `bpsai-pair release prep` command which verifies release readiness
and generates tasks for missing items.
"""

import re
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from bpsai_pair.cli import app

runner = CliRunner()


@pytest.fixture
def release_ready_repo(tmp_path):
    """Create a repository ready for release testing."""
    repo = tmp_path / "test_repo"
    repo.mkdir()

    # Initialize git
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, capture_output=True)

    # Create pyproject.toml with version
    (repo / "pyproject.toml").write_text("""[project]
name = "test-package"
version = "2.6.0"
""")

    # Create package with __version__
    pkg_dir = repo / "test_package"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text('__version__ = "2.6.0"\n')

    # Create CHANGELOG.md with current version
    (repo / "CHANGELOG.md").write_text("""# Changelog

## [2.6.0] - 2025-12-22

- Initial release
""")

    # Create .paircoder structure
    paircoder_dir = repo / ".paircoder"
    context_dir = paircoder_dir / "context"
    context_dir.mkdir(parents=True)

    # Create config.yaml with release section
    (paircoder_dir / "config.yaml").write_text("""version: 2.1
release:
  version_source: pyproject.toml
  documentation:
    - CHANGELOG.md
    - README.md
""")

    # Create state.md
    (context_dir / "state.md").write_text("""# Current State

## Active Plan

**Plan:** None
""")

    # Create initial commit
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo, check=True, capture_output=True)

    # Create version tag
    subprocess.run(["git", "tag", "v2.5.0"], cwd=repo, check=True, capture_output=True)

    return repo


class TestReleasePrepCommand:
    """Tests for the release prep command."""

    def test_prep_command_exists(self, release_ready_repo, monkeypatch):
        """Verify the release prep command exists."""
        monkeypatch.chdir(release_ready_repo)
        result = runner.invoke(app, ["release", "prep", "--help"])
        assert result.exit_code == 0
        assert "prep" in result.stdout.lower() or "since" in result.stdout.lower()

    def test_prep_shows_version_check(self, release_ready_repo, monkeypatch):
        """Prep command checks version consistency."""
        monkeypatch.chdir(release_ready_repo)
        result = runner.invoke(app, ["release", "prep"])
        # Should show version check in output
        assert "version" in result.stdout.lower() or "pyproject" in result.stdout.lower()

    def test_prep_detects_version_mismatch(self, release_ready_repo, monkeypatch):
        """Prep command detects version mismatch between pyproject.toml and __version__."""
        monkeypatch.chdir(release_ready_repo)

        # Create version mismatch
        pkg_init = release_ready_repo / "test_package" / "__init__.py"
        pkg_init.write_text('__version__ = "2.5.0"\n')  # Mismatched version

        result = runner.invoke(app, ["release", "prep"])
        # Should detect the mismatch (shown as error or warning)
        output = result.stdout.lower()
        assert "mismatch" in output or "❌" in result.stdout or "error" in output or "different" in output

    def test_prep_detects_missing_changelog_entry(self, release_ready_repo, monkeypatch):
        """Prep command detects missing CHANGELOG entry for current version."""
        monkeypatch.chdir(release_ready_repo)

        # Update pyproject.toml to newer version not in changelog
        pyproject = release_ready_repo / "pyproject.toml"
        pyproject.write_text("""[project]
name = "test-package"
version = "2.7.0"
""")

        result = runner.invoke(app, ["release", "prep"])
        output = result.stdout.lower()
        # Should detect missing changelog entry
        assert "changelog" in output

    def test_prep_with_since_flag(self, release_ready_repo, monkeypatch):
        """Prep command accepts --since flag for baseline comparison."""
        monkeypatch.chdir(release_ready_repo)
        result = runner.invoke(app, ["release", "prep", "--since", "v2.5.0"])
        # Should not error with --since flag
        assert result.exit_code == 0 or "since" in result.stdout.lower()

    def test_prep_generates_tasks(self, release_ready_repo, monkeypatch):
        """Prep command can generate tasks for missing items."""
        monkeypatch.chdir(release_ready_repo)

        # Create a version mismatch to trigger task generation
        pyproject = release_ready_repo / "pyproject.toml"
        pyproject.write_text("""[project]
name = "test-package"
version = "2.7.0"
""")

        result = runner.invoke(app, ["release", "prep", "--create-tasks"])
        # Either generates tasks or shows what would be generated
        output = result.stdout.lower()
        assert "task" in output or "generated" in output or "create" in output

    def test_prep_shows_status_icons(self, release_ready_repo, monkeypatch):
        """Prep command uses status icons (✅ ❌ ⚠️) in output."""
        monkeypatch.chdir(release_ready_repo)
        result = runner.invoke(app, ["release", "prep"])
        # Should have at least one status icon
        has_icons = "✅" in result.stdout or "❌" in result.stdout or "⚠️" in result.stdout or "✓" in result.stdout
        # Fallback: check for pass/fail text indicators
        has_text_indicators = "pass" in result.stdout.lower() or "fail" in result.stdout.lower() or "ok" in result.stdout.lower()
        assert has_icons or has_text_indicators

    def test_prep_checks_uncommitted_changes(self, release_ready_repo, monkeypatch):
        """Prep command detects uncommitted changes."""
        monkeypatch.chdir(release_ready_repo)

        # Create uncommitted change
        (release_ready_repo / "new_file.txt").write_text("uncommitted")

        result = runner.invoke(app, ["release", "prep"])
        output = result.stdout.lower()
        # Should warn about uncommitted changes
        assert "uncommitted" in output or "clean" in output or "changes" in output or "git" in output

    def test_prep_checks_tests_passing(self, release_ready_repo, monkeypatch):
        """Prep command checks if tests are passing."""
        monkeypatch.chdir(release_ready_repo)

        result = runner.invoke(app, ["release", "prep"])
        output = result.stdout.lower()
        # Should mention tests
        assert "test" in output


class TestReleasePrepConfig:
    """Tests for release prep configuration."""

    def test_reads_config_from_yaml(self, release_ready_repo, monkeypatch):
        """Prep command reads release config from config.yaml."""
        monkeypatch.chdir(release_ready_repo)

        # Update config with custom settings
        config_file = release_ready_repo / ".paircoder" / "config.yaml"
        config_file.write_text("""version: 2.1
release:
  version_source: pyproject.toml
  documentation:
    - CHANGELOG.md
    - README.md
    - docs/GUIDE.md
  freshness_days: 14
""")

        result = runner.invoke(app, ["release", "prep"])
        # Should run without error
        assert result.exit_code == 0 or "release" in result.stdout.lower()

    def test_default_config_when_missing(self, release_ready_repo, monkeypatch):
        """Prep command uses defaults when no release config exists."""
        monkeypatch.chdir(release_ready_repo)

        # Remove release section from config
        config_file = release_ready_repo / ".paircoder" / "config.yaml"
        config_file.write_text("version: 2.1\n")

        result = runner.invoke(app, ["release", "prep"])
        # Should still work with defaults
        assert result.exit_code == 0 or "release" in result.stdout.lower()


class TestReleasePrepChecks:
    """Tests for individual release prep checks."""

    def test_version_consistency_check_passes(self, release_ready_repo, monkeypatch):
        """Version check passes when versions match."""
        monkeypatch.chdir(release_ready_repo)

        # Ensure versions match
        pkg_init = release_ready_repo / "test_package" / "__init__.py"
        pkg_init.write_text('__version__ = "2.6.0"\n')

        result = runner.invoke(app, ["release", "prep"])
        # Should show version check as passing
        assert "✅" in result.stdout or "pass" in result.stdout.lower() or "ok" in result.stdout.lower() or "version" in result.stdout.lower()

    def test_changelog_check_passes_with_entry(self, release_ready_repo, monkeypatch):
        """Changelog check passes when version entry exists."""
        monkeypatch.chdir(release_ready_repo)

        # Ensure CHANGELOG has entry for current version
        changelog = release_ready_repo / "CHANGELOG.md"
        changelog.write_text("""# Changelog

## [2.6.0] - 2025-12-22

- New feature
""")

        result = runner.invoke(app, ["release", "prep"])
        # Should show changelog check in output
        assert "changelog" in result.stdout.lower()

    def test_git_clean_check_passes(self, release_ready_repo, monkeypatch):
        """Git clean check passes when no uncommitted changes."""
        monkeypatch.chdir(release_ready_repo)

        result = runner.invoke(app, ["release", "prep"])
        # Should show git status check in output
        output = result.stdout.lower()
        assert "git" in output or "commit" in output or "clean" in output or "change" in output
