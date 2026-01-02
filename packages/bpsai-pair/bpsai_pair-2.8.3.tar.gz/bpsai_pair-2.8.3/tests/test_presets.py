"""Tests for configuration presets."""
import pytest
from pathlib import Path
import yaml

from bpsai_pair.core.presets import (
    Preset,
    PRESETS,
    COMMON_EXCLUDES,
    get_preset,
    list_presets,
    get_preset_names,
    PresetManager,
)


class TestPreset:
    """Tests for Preset dataclass."""

    def test_basic_preset_creation(self):
        """Test creating a basic preset."""
        preset = Preset(
            name="test",
            description="Test preset",
            project_type="Test Project",
        )
        assert preset.name == "test"
        assert preset.description == "Test preset"
        assert preset.project_type == "Test Project"
        assert preset.coverage_target == 80  # default

    def test_preset_with_custom_values(self):
        """Test preset with custom values."""
        preset = Preset(
            name="custom",
            description="Custom preset",
            project_type="Custom",
            coverage_target=90,
            default_branch_type="develop",
            main_branch="master",
        )
        assert preset.coverage_target == 90
        assert preset.default_branch_type == "develop"
        assert preset.main_branch == "master"

    def test_to_config_dict(self):
        """Test converting preset to config dictionary."""
        preset = Preset(
            name="test",
            description="Test preset",
            project_type="Test",
            coverage_target=85,
        )

        config = preset.to_config_dict("My App", "Build something great")

        assert config["version"] == "2.6"
        assert config["project"]["name"] == "My App"
        assert config["project"]["primary_goal"] == "Build something great"
        assert config["project"]["coverage_target"] == 85
        assert config["workflow"]["default_branch_type"] == "feature"
        assert config["workflow"]["main_branch"] == "main"

    def test_to_config_dict_has_all_sections(self):
        """Test config dict includes all required sections."""
        preset = Preset(
            name="test",
            description="Test preset",
            project_type="Test",
        )

        config = preset.to_config_dict("Test", "Test goal")

        # All required sections must be present
        required_sections = [
            "version", "project", "workflow", "pack", "flows",
            "routing", "trello", "estimation", "metrics", "hooks", "security"
        ]
        for section in required_sections:
            assert section in config, f"Missing required section: {section}"

    def test_to_config_dict_trello_defaults(self):
        """Test config dict has Trello defaults."""
        preset = Preset(
            name="test",
            description="Test",
            project_type="Test",
        )

        config = preset.to_config_dict("Test", "Test")

        assert "trello" in config
        assert config["trello"]["board_id"] == ""
        assert "sync" in config["trello"]
        assert "list_mappings" in config["trello"]

    def test_to_config_dict_estimation_defaults(self):
        """Test config dict has estimation defaults."""
        preset = Preset(
            name="test",
            description="Test",
            project_type="Test",
        )

        config = preset.to_config_dict("Test", "Test")

        assert "estimation" in config
        assert "complexity_to_hours" in config["estimation"]
        assert "token_estimates" in config["estimation"]
        # Check size mappings exist
        assert "XS" in config["estimation"]["complexity_to_hours"]
        assert "XL" in config["estimation"]["complexity_to_hours"]

    def test_to_config_dict_hooks_defaults(self):
        """Test config dict has hooks defaults with Sprint 17 hooks."""
        preset = Preset(
            name="test",
            description="Test",
            project_type="Test",
        )

        config = preset.to_config_dict("Test", "Test")

        assert "hooks" in config
        assert config["hooks"]["enabled"] is True
        assert "on_task_start" in config["hooks"]
        assert "on_task_complete" in config["hooks"]
        # Check Sprint 17 hooks are present
        assert "record_velocity" in config["hooks"]["on_task_complete"]
        assert "record_token_usage" in config["hooks"]["on_task_complete"]

    def test_to_config_dict_security_defaults(self):
        """Test config dict has security defaults."""
        preset = Preset(
            name="test",
            description="Test",
            project_type="Test",
        )

        config = preset.to_config_dict("Test", "Test")

        assert "security" in config
        assert "allowlist_path" in config["security"]
        assert "sandbox" in config["security"]
        assert config["security"]["sandbox"]["enabled"] is False

    def test_to_config_dict_metrics_defaults(self):
        """Test config dict has metrics defaults."""
        preset = Preset(
            name="test",
            description="Test",
            project_type="Test",
        )

        config = preset.to_config_dict("Test", "Test")

        assert "metrics" in config
        assert config["metrics"]["enabled"] is True
        assert "store_path" in config["metrics"]

    def test_to_config_dict_with_routing(self):
        """Test config dict includes model routing when specified."""
        preset = Preset(
            name="test",
            description="Test",
            project_type="Test",
            model_routing={"by_complexity": {"simple": {"model": "test-model"}}},
        )

        config = preset.to_config_dict("Test", "Test")

        assert "routing" in config
        assert config["routing"]["by_complexity"]["simple"]["model"] == "test-model"

    def test_to_yaml(self):
        """Test YAML generation."""
        preset = Preset(
            name="test",
            description="Test",
            project_type="Test",
        )

        yaml_str = preset.to_yaml("My Project", "Build things")

        # Should be valid YAML
        parsed = yaml.safe_load(yaml_str)
        assert parsed["project"]["name"] == "My Project"
        assert parsed["project"]["primary_goal"] == "Build things"


class TestBuiltInPresets:
    """Tests for built-in presets."""

    def test_python_cli_preset_exists(self):
        """Test python-cli preset exists and has expected values."""
        preset = PRESETS.get("python-cli")
        assert preset is not None
        assert preset.project_type == "Python CLI"
        assert ".pytest_cache" in preset.pack_excludes

    def test_python_api_preset_exists(self):
        """Test python-api preset exists."""
        preset = PRESETS.get("python-api")
        assert preset is not None
        assert preset.coverage_target == 85
        assert "*.db" in preset.pack_excludes

    def test_react_preset_exists(self):
        """Test react preset exists."""
        preset = PRESETS.get("react")
        assert preset is not None
        assert ".next" in preset.pack_excludes
        assert preset.node_formatter == "prettier"

    def test_fullstack_preset_exists(self):
        """Test fullstack preset exists."""
        preset = PRESETS.get("fullstack")
        assert preset is not None
        # Should have both Python and Node excludes
        assert ".pytest_cache" in preset.pack_excludes
        assert ".next" in preset.pack_excludes

    def test_library_preset_exists(self):
        """Test library preset exists."""
        preset = PRESETS.get("library")
        assert preset is not None
        assert preset.coverage_target == 90  # Higher for libraries
        assert "*.whl" in preset.pack_excludes

    def test_minimal_preset_exists(self):
        """Test minimal preset exists."""
        preset = PRESETS.get("minimal")
        assert preset is not None
        assert len(preset.enabled_flows) < len(PRESETS["python-cli"].enabled_flows)

    def test_autonomous_preset_exists(self):
        """Test autonomous preset exists."""
        preset = PRESETS.get("autonomous")
        assert preset is not None
        assert preset.model_routing is not None
        assert "by_complexity" in preset.model_routing

    def test_all_presets_have_common_excludes(self):
        """Test all presets include common excludes."""
        for name, preset in PRESETS.items():
            for exclude in COMMON_EXCLUDES:
                assert exclude in preset.pack_excludes, \
                    f"{name} missing common exclude: {exclude}"

    def test_all_presets_generate_complete_config(self):
        """Test all presets generate configs with all required sections."""
        required_sections = [
            "version", "project", "workflow", "pack", "flows",
            "routing", "trello", "estimation", "metrics", "hooks", "security"
        ]

        for name, preset in PRESETS.items():
            config = preset.to_config_dict("Test Project", "Test goal")
            for section in required_sections:
                assert section in config, \
                    f"Preset '{name}' missing required section: {section}"

    def test_bps_preset_has_custom_trello_config(self):
        """Test BPS preset has its custom Trello configuration."""
        preset = PRESETS.get("bps")
        assert preset is not None
        assert preset.trello_config is not None
        assert "lists" in preset.trello_config
        assert "labels" in preset.trello_config
        assert "automation" in preset.trello_config

    def test_bps_preset_has_custom_hooks(self):
        """Test BPS preset has custom hooks configuration."""
        preset = PRESETS.get("bps")
        assert preset is not None
        assert preset.hooks_config is not None
        assert "on_task_complete" in preset.hooks_config
        # Verify Sprint 17 hooks are present
        assert "record_velocity" in preset.hooks_config["on_task_complete"]
        assert "record_token_usage" in preset.hooks_config["on_task_complete"]


class TestPresetFunctions:
    """Tests for preset utility functions."""

    def test_get_preset_returns_preset(self):
        """Test get_preset returns correct preset."""
        preset = get_preset("python-cli")
        assert preset is not None
        assert preset.name == "python-cli"

    def test_get_preset_returns_none_for_unknown(self):
        """Test get_preset returns None for unknown preset."""
        preset = get_preset("nonexistent")
        assert preset is None

    def test_list_presets_returns_all(self):
        """Test list_presets returns all presets."""
        presets = list_presets()
        assert len(presets) == len(PRESETS)
        assert all(isinstance(p, Preset) for p in presets)

    def test_get_preset_names_returns_strings(self):
        """Test get_preset_names returns list of strings."""
        names = get_preset_names()
        assert len(names) == len(PRESETS)
        assert all(isinstance(n, str) for n in names)
        assert "python-cli" in names


class TestPresetManager:
    """Tests for PresetManager class."""

    def test_init_with_defaults(self):
        """Test manager initializes with default presets."""
        manager = PresetManager()
        assert len(manager.presets) == len(PRESETS)

    def test_init_with_custom_presets(self):
        """Test manager with custom presets."""
        custom = Preset(name="custom", description="Custom", project_type="Custom")
        manager = PresetManager(custom_presets={"custom": custom})

        assert "custom" in manager.presets
        assert len(manager.presets) == len(PRESETS) + 1

    def test_get_returns_preset(self):
        """Test manager.get returns preset."""
        manager = PresetManager()
        preset = manager.get("python-cli")
        assert preset is not None
        assert preset.name == "python-cli"

    def test_list_returns_all(self):
        """Test manager.list returns all presets."""
        manager = PresetManager()
        presets = manager.list()
        assert len(presets) == len(PRESETS)

    def test_names_returns_names(self):
        """Test manager.names returns preset names."""
        manager = PresetManager()
        names = manager.names()
        assert "python-cli" in names

    def test_add_preset(self):
        """Test adding a custom preset."""
        manager = PresetManager()
        custom = Preset(name="new-preset", description="New", project_type="New")

        manager.add(custom)

        assert "new-preset" in manager.presets
        assert manager.get("new-preset") == custom

    def test_remove_preset(self):
        """Test removing a preset."""
        manager = PresetManager()

        result = manager.remove("python-cli")

        assert result is True
        assert "python-cli" not in manager.presets

    def test_remove_nonexistent_returns_false(self):
        """Test removing nonexistent preset returns False."""
        manager = PresetManager()

        result = manager.remove("nonexistent")

        assert result is False

    def test_describe_returns_formatted_string(self):
        """Test describe returns formatted description."""
        manager = PresetManager()

        desc = manager.describe("python-cli")

        assert desc is not None
        assert "python-cli" in desc
        assert "Python CLI" in desc
        assert "Coverage Target" in desc

    def test_describe_nonexistent_returns_none(self):
        """Test describe returns None for unknown preset."""
        manager = PresetManager()

        desc = manager.describe("nonexistent")

        assert desc is None
