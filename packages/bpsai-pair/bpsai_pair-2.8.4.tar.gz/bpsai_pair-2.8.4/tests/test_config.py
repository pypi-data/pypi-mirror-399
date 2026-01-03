"""Tests for configuration module."""
from pathlib import Path
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bpsai_pair.core.config import Config, ContextTemplate


def test_default_config():
    """Test default configuration."""
    config = Config()
    assert config.project_name == "My Project"
    assert config.coverage_target == 80
    assert config.main_branch == "main"


def test_config_save_load(tmp_path):
    """Test saving and loading config."""
    config = Config(
        project_name="Test Project",
        primary_goal="Test Goal",
        coverage_target=90
    )
    config.save(tmp_path)

    assert (tmp_path / ".paircoder.yml").exists()

    loaded = Config.load(tmp_path)
    assert loaded.project_name == "Test Project"
    assert loaded.coverage_target == 90


def test_env_override(tmp_path, monkeypatch):
    """Test environment variable override."""
    monkeypatch.setenv("PAIRCODER_MAIN_BRANCH", "master")
    monkeypatch.setenv("PAIRCODER_PROJECT_NAME", "EnvProject")

    config = Config.load(tmp_path)
    assert config.main_branch == "master"
    assert config.project_name == "EnvProject"


def test_development_template():
    """Test template generation."""
    config = Config(project_name="Test", primary_goal="Build")
    template = ContextTemplate.development_md(config)

    assert "Test" in template
    assert "Build" in template
    assert "Context Sync" in template


# ============================================================================
# PCV2-013: .paircoder/ folder config support tests
# ============================================================================


class TestConfigV2:
    """Tests for v2 .paircoder/ folder config support."""

    def test_find_config_v2_preferred(self, tmp_path):
        """Test that .paircoder/config.yaml is preferred over .paircoder.yml."""
        # Create both config files
        v2_dir = tmp_path / ".paircoder"
        v2_dir.mkdir()
        (v2_dir / "config.yaml").write_text("version: 2\nproject:\n  name: V2Project\n")
        (tmp_path / ".paircoder.yml").write_text("version: 0.1.3\nproject:\n  name: LegacyProject\n")

        config_file = Config.find_config_file(tmp_path)
        assert config_file == v2_dir / "config.yaml"

    def test_find_config_v2_yml(self, tmp_path):
        """Test that .paircoder/config.yml is found."""
        v2_dir = tmp_path / ".paircoder"
        v2_dir.mkdir()
        (v2_dir / "config.yml").write_text("version: 2\nproject:\n  name: V2Project\n")

        config_file = Config.find_config_file(tmp_path)
        assert config_file == v2_dir / "config.yml"

    def test_find_config_legacy_fallback(self, tmp_path):
        """Test fallback to .paircoder.yml when no v2 config exists."""
        (tmp_path / ".paircoder.yml").write_text("version: 0.1.3\nproject:\n  name: LegacyProject\n")

        config_file = Config.find_config_file(tmp_path)
        assert config_file == tmp_path / ".paircoder.yml"

    def test_find_config_none(self, tmp_path):
        """Test returns None when no config exists."""
        config_file = Config.find_config_file(tmp_path)
        assert config_file is None

    def test_load_v2_config(self, tmp_path):
        """Test loading from .paircoder/config.yaml."""
        v2_dir = tmp_path / ".paircoder"
        v2_dir.mkdir()
        (v2_dir / "config.yaml").write_text("""
version: 2
project:
  name: V2TestProject
  primary_goal: Test v2 config
  coverage_target: 95
workflow:
  main_branch: develop
""")

        config = Config.load(tmp_path)
        assert config.project_name == "V2TestProject"
        assert config.primary_goal == "Test v2 config"
        assert config.coverage_target == 95
        assert config.main_branch == "develop"

    def test_load_legacy_config(self, tmp_path):
        """Test loading from .paircoder.yml (legacy)."""
        (tmp_path / ".paircoder.yml").write_text("""
version: 0.1.3
project:
  name: LegacyTestProject
  primary_goal: Test legacy config
workflow:
  main_branch: main
""")

        config = Config.load(tmp_path)
        assert config.project_name == "LegacyTestProject"
        assert config.primary_goal == "Test legacy config"
        assert config.main_branch == "main"

    def test_load_v2_over_legacy(self, tmp_path):
        """Test that v2 config takes precedence over legacy."""
        # Create legacy config
        (tmp_path / ".paircoder.yml").write_text("""
version: 0.1.3
project:
  name: LegacyProject
""")

        # Create v2 config
        v2_dir = tmp_path / ".paircoder"
        v2_dir.mkdir()
        (v2_dir / "config.yaml").write_text("""
version: 2
project:
  name: V2Project
""")

        config = Config.load(tmp_path)
        assert config.project_name == "V2Project"

    def test_save_v2_explicit(self, tmp_path):
        """Test saving to v2 location explicitly."""
        config = Config(project_name="V2Save")
        saved_path = config.save(tmp_path, use_v2=True)

        assert saved_path == tmp_path / ".paircoder" / "config.yaml"
        assert saved_path.exists()
        assert (tmp_path / ".paircoder").is_dir()

    def test_save_legacy_explicit(self, tmp_path):
        """Test saving to legacy location explicitly."""
        config = Config(project_name="LegacySave")
        saved_path = config.save(tmp_path, legacy=True)

        assert saved_path == tmp_path / ".paircoder.yml"
        assert saved_path.exists()

    def test_save_v2_when_folder_exists(self, tmp_path):
        """Test saving goes to v2 when .paircoder/ folder already exists."""
        (tmp_path / ".paircoder").mkdir()

        config = Config(project_name="AutoV2")
        saved_path = config.save(tmp_path)

        assert saved_path == tmp_path / ".paircoder" / "config.yaml"

    def test_save_legacy_default(self, tmp_path):
        """Test default save goes to legacy when no .paircoder/ folder."""
        config = Config(project_name="DefaultLegacy")
        saved_path = config.save(tmp_path)

        assert saved_path == tmp_path / ".paircoder.yml"

    def test_env_override_with_v2_config(self, tmp_path, monkeypatch):
        """Test environment variables override v2 config values."""
        v2_dir = tmp_path / ".paircoder"
        v2_dir.mkdir()
        (v2_dir / "config.yaml").write_text("""
version: 2
project:
  name: ConfigProject
workflow:
  main_branch: develop
""")

        monkeypatch.setenv("PAIRCODER_MAIN_BRANCH", "main-override")
        monkeypatch.setenv("PAIRCODER_PROJECT_NAME", "EnvProject")

        config = Config.load(tmp_path)
        assert config.project_name == "EnvProject"
        assert config.main_branch == "main-override"

    def test_roundtrip_v2(self, tmp_path):
        """Test save and load roundtrip with v2 config."""
        original = Config(
            project_name="RoundtripProject",
            primary_goal="Test roundtrip",
            coverage_target=85,
            main_branch="develop",
            default_branch_type="fix"
        )
        original.save(tmp_path, use_v2=True)

        loaded = Config.load(tmp_path)
        assert loaded.project_name == original.project_name
        assert loaded.primary_goal == original.primary_goal
        assert loaded.coverage_target == original.coverage_target
        assert loaded.main_branch == original.main_branch
        assert loaded.default_branch_type == original.default_branch_type

    def test_backward_compat_flat_config(self, tmp_path):
        """Test backward compatibility with old flat config structure."""
        # Old flat structure (pre-versioned)
        (tmp_path / ".paircoder.yml").write_text("""
project_name: FlatProject
primary_goal: Test flat config
coverage_target: 75
main_branch: master
""")

        config = Config.load(tmp_path)
        assert config.project_name == "FlatProject"
        assert config.primary_goal == "Test flat config"
        assert config.coverage_target == 75
        assert config.main_branch == "master"
