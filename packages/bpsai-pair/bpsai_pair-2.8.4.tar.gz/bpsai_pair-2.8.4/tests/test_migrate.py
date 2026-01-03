"""Tests for the migrate command."""
import pytest
from pathlib import Path

from bpsai_pair.migrate import (
    LegacyVersion,
    MigrationPlan,
    detect_version,
    plan_migration,
    create_backup,
    execute_migration,
)


class TestDetectVersion:
    """Tests for version detection."""

    def test_detect_v1_legacy_with_yml(self, tmp_path):
        """Detect v1.x structure with .paircoder.yml."""
        (tmp_path / ".paircoder.yml").write_text("version: 1.0")
        assert detect_version(tmp_path) == LegacyVersion.V1_LEGACY

    def test_detect_v1_legacy_with_root_context(self, tmp_path):
        """Detect v1.x structure with root context/ directory."""
        (tmp_path / "context").mkdir()
        (tmp_path / "context" / "project.md").write_text("# Project")
        assert detect_version(tmp_path) == LegacyVersion.V1_LEGACY

    def test_detect_v2_early_no_config(self, tmp_path):
        """Detect v2.0-2.1 structure without config.yaml."""
        (tmp_path / ".paircoder").mkdir()
        assert detect_version(tmp_path) == LegacyVersion.V2_EARLY

    def test_detect_v2_early_old_version(self, tmp_path):
        """Detect v2.0-2.1 structure with old version number."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.0'")
        assert detect_version(tmp_path) == LegacyVersion.V2_EARLY

    def test_detect_v2_partial(self, tmp_path):
        """Detect v2.2-2.3 structure."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.2'")
        assert detect_version(tmp_path) == LegacyVersion.V2_PARTIAL

    def test_detect_v2_partial_23(self, tmp_path):
        """Detect v2.3 structure."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.3'")
        assert detect_version(tmp_path) == LegacyVersion.V2_PARTIAL

    def test_detect_v2_current_24(self, tmp_path):
        """Detect current v2.4+ structure."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.4'")
        assert detect_version(tmp_path) == LegacyVersion.V2_CURRENT

    def test_detect_v2_current_25(self, tmp_path):
        """Detect current v2.5 structure."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.5'")
        assert detect_version(tmp_path) == LegacyVersion.V2_CURRENT

    def test_detect_v2_current_26(self, tmp_path):
        """Detect current v2.6 structure."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.6'")
        assert detect_version(tmp_path) == LegacyVersion.V2_CURRENT

    def test_detect_unknown_empty(self, tmp_path):
        """Detect unknown when no PairCoder structure exists."""
        assert detect_version(tmp_path) == LegacyVersion.UNKNOWN

    def test_detect_handles_malformed_yaml(self, tmp_path):
        """Handle malformed config.yaml gracefully."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text("{ invalid yaml: [")
        # Should return V2_EARLY since config exists but can't be parsed
        assert detect_version(tmp_path) == LegacyVersion.V2_EARLY


class TestPlanMigration:
    """Tests for migration planning."""

    def test_plan_v1_migration_creates_dirs(self, tmp_path):
        """V1 migration plans to create all necessary directories."""
        (tmp_path / ".paircoder.yml").write_text("version: 1.0")
        (tmp_path / "context").mkdir()

        plan = plan_migration(tmp_path)

        assert plan.source_version == LegacyVersion.V1_LEGACY
        assert tmp_path / ".paircoder" in plan.dirs_to_create
        assert tmp_path / ".paircoder" / "context" in plan.dirs_to_create
        assert tmp_path / ".paircoder" / "flows" in plan.dirs_to_create
        assert tmp_path / ".paircoder" / "tasks" in plan.dirs_to_create
        assert tmp_path / ".claude" in plan.dirs_to_create

    def test_plan_v1_migration_moves_files(self, tmp_path):
        """V1 migration plans to move context files."""
        (tmp_path / ".paircoder.yml").write_text("version: 1.0")
        (tmp_path / "context").mkdir()
        (tmp_path / "context" / "development.md").write_text("# Dev")
        (tmp_path / "context" / "project.md").write_text("# Project")

        plan = plan_migration(tmp_path)

        # Check file moves are planned
        src_files = [src for src, _ in plan.file_moves]
        assert tmp_path / "context" / "development.md" in src_files
        assert tmp_path / "context" / "project.md" in src_files

    def test_plan_v1_migration_marks_deletions(self, tmp_path):
        """V1 migration plans to delete old structure."""
        (tmp_path / ".paircoder.yml").write_text("version: 1.0")
        (tmp_path / "context").mkdir()
        (tmp_path / "prompts").mkdir()

        plan = plan_migration(tmp_path)

        assert tmp_path / ".paircoder.yml" in plan.files_to_delete
        assert tmp_path / "context" in plan.files_to_delete
        assert tmp_path / "prompts" in plan.files_to_delete

    def test_plan_v2_early_adds_missing_dirs(self, tmp_path):
        """V2 early migration adds missing directories."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.0'")

        plan = plan_migration(tmp_path)

        assert plan.source_version == LegacyVersion.V2_EARLY
        # Should add missing subdirs
        assert tmp_path / ".paircoder" / "flows" in plan.dirs_to_create
        assert tmp_path / ".paircoder" / "plans" in plan.dirs_to_create
        assert tmp_path / ".paircoder" / "tasks" in plan.dirs_to_create

    def test_plan_v2_early_adds_config_sections(self, tmp_path):
        """V2 early migration adds missing config sections."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text(
            "version: '2.0'\nproject:\n  name: test"
        )

        plan = plan_migration(tmp_path)

        assert "trello" in plan.config_additions
        assert "hooks" in plan.config_additions
        assert "metrics" in plan.config_additions
        assert "estimation" in plan.config_additions

    def test_plan_v2_partial_only_adds_missing_sections(self, tmp_path):
        """V2 partial migration only adds sections that are missing."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text(
            "version: '2.2'\nproject:\n  name: test\ntrello:\n  enabled: true"
        )

        plan = plan_migration(tmp_path)

        # trello exists, should not be in additions
        assert "trello" not in plan.config_additions
        # hooks missing, should be in additions
        assert "hooks" in plan.config_additions

    def test_plan_v2_current_empty_plan(self, tmp_path):
        """V2 current version returns minimal plan."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.5'")

        plan = plan_migration(tmp_path)

        assert plan.source_version == LegacyVersion.V2_CURRENT
        assert len(plan.dirs_to_create) == 0
        assert len(plan.file_moves) == 0
        assert len(plan.config_additions) == 0

    def test_plan_warns_missing_claude_md(self, tmp_path):
        """Plan includes warning if CLAUDE.md is missing."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.0'")

        plan = plan_migration(tmp_path)

        warning_texts = " ".join(plan.warnings)
        assert "CLAUDE.md" in warning_texts

    def test_plan_warns_missing_agents_md(self, tmp_path):
        """Plan includes warning if AGENTS.md is missing."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.0'")

        plan = plan_migration(tmp_path)

        warning_texts = " ".join(plan.warnings)
        assert "AGENTS.md" in warning_texts


class TestCreateBackup:
    """Tests for backup creation."""

    def test_backup_creates_timestamped_dir(self, tmp_path):
        """Backup creates a timestamped directory."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.2'")

        backup_path = create_backup(tmp_path)

        assert backup_path.exists()
        assert backup_path.name.startswith(".paircoder_backup_")
        assert (backup_path / ".paircoder" / "config.yaml").exists()

    def test_backup_includes_claude_dir(self, tmp_path):
        """Backup includes .claude/ if it exists."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "settings.json").write_text("{}")

        backup_path = create_backup(tmp_path)

        assert (backup_path / ".claude" / "settings.json").exists()

    def test_backup_includes_v1_files(self, tmp_path):
        """Backup includes v1.x files if they exist."""
        (tmp_path / ".paircoder.yml").write_text("version: 1.0")
        (tmp_path / "context").mkdir()
        (tmp_path / "context" / "project.md").write_text("# Project")

        backup_path = create_backup(tmp_path)

        assert (backup_path / ".paircoder.yml").exists()
        assert (backup_path / "context" / "project.md").exists()


class TestExecuteMigration:
    """Tests for migration execution."""

    def test_execute_creates_directories(self, tmp_path):
        """Execute migration creates planned directories."""
        plan = MigrationPlan(
            source_version=LegacyVersion.V2_EARLY,
            dirs_to_create=[
                tmp_path / ".paircoder" / "flows",
                tmp_path / ".paircoder" / "plans",
            ]
        )

        execute_migration(tmp_path, plan)

        assert (tmp_path / ".paircoder" / "flows").exists()
        assert (tmp_path / ".paircoder" / "plans").exists()

    def test_execute_moves_files(self, tmp_path):
        """Execute migration moves files as planned."""
        (tmp_path / "context").mkdir()
        (tmp_path / "context" / "dev.md").write_text("# Dev")

        plan = MigrationPlan(
            source_version=LegacyVersion.V1_LEGACY,
            file_moves=[
                (tmp_path / "context" / "dev.md", tmp_path / ".paircoder" / "context" / "state.md")
            ]
        )

        execute_migration(tmp_path, plan)

        assert not (tmp_path / "context" / "dev.md").exists()
        assert (tmp_path / ".paircoder" / "context" / "state.md").exists()
        assert (tmp_path / ".paircoder" / "context" / "state.md").read_text() == "# Dev"

    def test_execute_updates_config(self, tmp_path):
        """Execute migration updates config with new sections."""
        (tmp_path / ".paircoder").mkdir()
        (tmp_path / ".paircoder" / "config.yaml").write_text(
            "version: '2.0'\nproject:\n  name: test"
        )

        plan = MigrationPlan(
            source_version=LegacyVersion.V2_EARLY,
            config_additions={"trello": {"enabled": False}}
        )

        execute_migration(tmp_path, plan)

        import yaml
        config = yaml.safe_load((tmp_path / ".paircoder" / "config.yaml").read_text())
        assert config["trello"] == {"enabled": False}
        assert config["version"] == "2.5"  # Updated to target version

    def test_execute_deletes_old_files(self, tmp_path):
        """Execute migration deletes old files."""
        (tmp_path / ".paircoder.yml").write_text("version: 1.0")
        (tmp_path / "context").mkdir()
        (tmp_path / "context" / "project.md").write_text("# Project")

        plan = MigrationPlan(
            source_version=LegacyVersion.V1_LEGACY,
            files_to_delete=[
                tmp_path / ".paircoder.yml",
                tmp_path / "context",
            ]
        )

        execute_migration(tmp_path, plan)

        assert not (tmp_path / ".paircoder.yml").exists()
        assert not (tmp_path / "context").exists()


class TestMigrateCLI:
    """Tests for migrate CLI command."""

    def test_migrate_command_exists(self):
        """Verify migrate_app exists and is callable."""
        from bpsai_pair.migrate import migrate_app
        assert migrate_app is not None

    def test_migrate_status_command_exists(self):
        """Verify migrate status subcommand exists."""
        from bpsai_pair.migrate import migrate_status
        assert migrate_status is not None
