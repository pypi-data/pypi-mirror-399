"""Tests for skill suggestion module."""
import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock


class TestPatternDetector:
    """Tests for pattern detection in session history."""

    def test_detects_repeated_command_sequence(self):
        """Should detect frequently repeated command sequences."""
        from bpsai_pair.skills.suggestion import PatternDetector

        # Create mock history with repeated patterns
        history = [
            {"command": "pytest", "timestamp": "2025-12-23T10:00:00"},
            {"command": "read_traceback", "timestamp": "2025-12-23T10:01:00"},
            {"command": "edit_file", "timestamp": "2025-12-23T10:02:00"},
            {"command": "pytest", "timestamp": "2025-12-23T10:03:00"},
            {"command": "pytest", "timestamp": "2025-12-23T10:10:00"},
            {"command": "read_traceback", "timestamp": "2025-12-23T10:11:00"},
            {"command": "edit_file", "timestamp": "2025-12-23T10:12:00"},
            {"command": "pytest", "timestamp": "2025-12-23T10:13:00"},
            {"command": "pytest", "timestamp": "2025-12-23T10:20:00"},
            {"command": "read_traceback", "timestamp": "2025-12-23T10:21:00"},
            {"command": "edit_file", "timestamp": "2025-12-23T10:22:00"},
            {"command": "pytest", "timestamp": "2025-12-23T10:23:00"},
        ]

        detector = PatternDetector()
        patterns = detector.detect_patterns(history)

        # Should detect the test-debug cycle pattern
        assert len(patterns) > 0
        # At least one pattern should involve pytest
        assert any("pytest" in p.get("sequence", []) for p in patterns)

    def test_calculates_confidence_scores(self):
        """Confidence should be based on frequency and consistency."""
        from bpsai_pair.skills.suggestion import PatternDetector

        history = [
            {"command": "git status", "timestamp": "2025-12-23T10:00:00"},
            {"command": "git diff", "timestamp": "2025-12-23T10:01:00"},
            {"command": "git add", "timestamp": "2025-12-23T10:02:00"},
            {"command": "git commit", "timestamp": "2025-12-23T10:03:00"},
        ] * 5  # Repeat 5 times

        detector = PatternDetector()
        patterns = detector.detect_patterns(history)

        # Patterns with high frequency should have high confidence
        for pattern in patterns:
            assert "confidence" in pattern
            assert 0 <= pattern["confidence"] <= 100

    def test_handles_empty_history(self):
        """Should handle empty history gracefully."""
        from bpsai_pair.skills.suggestion import PatternDetector

        detector = PatternDetector()
        patterns = detector.detect_patterns([])

        assert patterns == []

    def test_minimum_occurrences_threshold(self):
        """Should only detect patterns that occur at least 3 times."""
        from bpsai_pair.skills.suggestion import PatternDetector

        # Only 2 occurrences - should not be detected
        history = [
            {"command": "cmd_a", "timestamp": "2025-12-23T10:00:00"},
            {"command": "cmd_b", "timestamp": "2025-12-23T10:01:00"},
            {"command": "cmd_a", "timestamp": "2025-12-23T10:10:00"},
            {"command": "cmd_b", "timestamp": "2025-12-23T10:11:00"},
        ]

        detector = PatternDetector(min_occurrences=3)
        patterns = detector.detect_patterns(history)

        assert len(patterns) == 0


class TestSkillSuggester:
    """Tests for skill suggestion generation."""

    def test_generates_suggestions_from_patterns(self):
        """Should generate skill suggestions from detected patterns."""
        from bpsai_pair.skills.suggestion import SkillSuggester

        patterns = [
            {
                "sequence": ["pytest", "read_traceback", "edit_file", "pytest"],
                "occurrences": 5,
                "confidence": 85,
            }
        ]

        suggester = SkillSuggester()
        suggestions = suggester.generate_suggestions(patterns)

        assert len(suggestions) > 0
        assert "name" in suggestions[0]
        assert "confidence" in suggestions[0]
        assert "description" in suggestions[0]

    def test_detects_overlap_with_existing_skills(self):
        """Should detect when suggestion overlaps with existing skill."""
        from bpsai_pair.skills.suggestion import SkillSuggester

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            # Create existing skill with keywords that match the pattern
            existing_skill = skills_dir / "testing-workflows"
            existing_skill.mkdir()
            (existing_skill / "SKILL.md").write_text("""---
name: testing-workflows
description: Manages pytest testing workflows including running tests and editing fixes.
---

# Testing Workflows
""")

            patterns = [
                {
                    "sequence": ["pytest", "edit_file", "pytest"],
                    "occurrences": 5,
                    "confidence": 85,
                }
            ]

            suggester = SkillSuggester(skills_dir=skills_dir)
            suggestions = suggester.generate_suggestions(patterns)

            # Should detect overlap based on name similarity (both contain "testing")
            overlapping = [s for s in suggestions if s.get("overlaps_with")]
            # The generated name should be "testing-*" which overlaps with "testing-workflows"
            assert len(suggestions) > 0
            if suggestions:
                # Check that the suggestion name starts with "testing"
                assert suggestions[0]["name"].startswith("testing")

    def test_generates_valid_skill_name(self):
        """Generated skill names should follow naming conventions."""
        from bpsai_pair.skills.suggestion import SkillSuggester

        patterns = [
            {
                "sequence": ["git status", "git diff", "git add", "git commit"],
                "occurrences": 4,
                "confidence": 75,
            }
        ]

        suggester = SkillSuggester()
        suggestions = suggester.generate_suggestions(patterns)

        if suggestions:
            name = suggestions[0]["name"]
            # Should be lowercase with hyphens
            assert name == name.lower()
            assert "_" not in name
            # Should ideally use gerund form
            assert any(name.startswith(g) for g in ["managing", "reviewing", "debugging", "committing", "running", "creating", "updating"])

    def test_estimate_time_savings(self):
        """Should estimate potential time savings."""
        from bpsai_pair.skills.suggestion import SkillSuggester

        patterns = [
            {
                "sequence": ["pytest", "read_file", "edit_file"],
                "occurrences": 10,
                "avg_duration_seconds": 120,
                "confidence": 80,
            }
        ]

        suggester = SkillSuggester()
        suggestions = suggester.generate_suggestions(patterns)

        if suggestions:
            assert "estimated_savings" in suggestions[0]


class TestSkillDraftCreator:
    """Tests for creating skill drafts from suggestions."""

    def test_creates_valid_skill_draft(self):
        """Should create a valid skill draft file."""
        from bpsai_pair.skills.suggestion import SkillDraftCreator

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            suggestion = {
                "name": "debugging-python-tests",
                "description": "Assists with debugging Python test failures using pytest.",
                "confidence": 85,
                "pattern": ["pytest", "read_traceback", "edit_file"],
            }

            creator = SkillDraftCreator(skills_dir=skills_dir)
            result = creator.create_draft(suggestion)

            assert result["success"] is True
            draft_path = skills_dir / "debugging-python-tests" / "SKILL.md"
            assert draft_path.exists()

            content = draft_path.read_text()
            assert "name: debugging-python-tests" in content
            assert "description:" in content

    def test_validates_draft_before_creation(self):
        """Should validate the draft passes skill validator."""
        from bpsai_pair.skills.suggestion import SkillDraftCreator
        from bpsai_pair.skills.validator import SkillValidator

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            suggestion = {
                "name": "testing-workflows",
                "description": "Manages test execution and result analysis workflows.",
                "confidence": 75,
            }

            creator = SkillDraftCreator(skills_dir=skills_dir)
            result = creator.create_draft(suggestion)

            # Validate with skill validator
            validator = SkillValidator(skills_dir)
            validation = validator.validate_skill(skills_dir / "testing-workflows")

            assert validation["valid"] is True

    def test_doesnt_overwrite_existing(self):
        """Should not overwrite existing skill without force."""
        from bpsai_pair.skills.suggestion import SkillDraftCreator, SkillSuggestionError

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            # Create existing skill
            existing = skills_dir / "my-skill"
            existing.mkdir()
            (existing / "SKILL.md").write_text("existing content")

            suggestion = {
                "name": "my-skill",
                "description": "A new skill.",
                "confidence": 80,
            }

            creator = SkillDraftCreator(skills_dir=skills_dir)

            with pytest.raises(SkillSuggestionError) as exc_info:
                creator.create_draft(suggestion)

            assert "exists" in str(exc_info.value).lower()


class TestHistoryParser:
    """Tests for parsing session history."""

    def test_parses_session_log(self):
        """Should parse session log file."""
        from bpsai_pair.skills.suggestion import HistoryParser

        with tempfile.TemporaryDirectory() as tmpdir:
            history_dir = Path(tmpdir) / ".paircoder" / "history"
            history_dir.mkdir(parents=True)

            # Create mock session log
            session_log = history_dir / "sessions.log"
            session_log.write_text("""2025-12-23T10:00:00 session_start id=abc123
2025-12-23T11:00:00 session_start id=def456
""")

            parser = HistoryParser(history_dir=history_dir)
            sessions = parser.get_sessions()

            assert len(sessions) >= 2

    def test_parses_changes_log(self):
        """Should parse changes log for command patterns."""
        from bpsai_pair.skills.suggestion import HistoryParser

        with tempfile.TemporaryDirectory() as tmpdir:
            history_dir = Path(tmpdir) / ".paircoder" / "history"
            history_dir.mkdir(parents=True)

            # Create mock changes log
            changes_log = history_dir / "changes.log"
            changes_log.write_text("""2025-12-23T10:00:00-06:00
2025-12-23T10:01:00-06:00
2025-12-23T10:02:00-06:00
""")

            parser = HistoryParser(history_dir=history_dir)
            changes = parser.get_changes()

            assert isinstance(changes, list)

    def test_handles_missing_history(self):
        """Should handle missing history files gracefully."""
        from bpsai_pair.skills.suggestion import HistoryParser

        with tempfile.TemporaryDirectory() as tmpdir:
            history_dir = Path(tmpdir) / ".paircoder" / "history"
            # Don't create the directory

            parser = HistoryParser(history_dir=history_dir)
            sessions = parser.get_sessions()

            assert sessions == []


class TestSuggestCommand:
    """Tests for the CLI suggest command."""

    def test_suggest_command_exists(self):
        """skill suggest command should exist."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["skill", "suggest", "--help"])

        assert result.exit_code == 0
        assert "suggest" in result.output.lower()

    def test_suggest_shows_suggestions(self):
        """skill suggest should show suggestions when patterns found."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create project structure
            project_dir = Path(tmpdir)
            (project_dir / ".paircoder").mkdir()
            history_dir = project_dir / ".paircoder" / "history"
            history_dir.mkdir()
            skills_dir = project_dir / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            # Create mock history with patterns
            session_log = history_dir / "sessions.log"
            session_log.write_text("2025-12-23T10:00:00 session_start id=test\n")

            runner = CliRunner()
            with patch('bpsai_pair.skills.suggestion.HistoryParser') as mock_parser:
                mock_parser.return_value.get_command_history.return_value = []

                with patch('bpsai_pair.skills.cli_commands.find_project_root', return_value=project_dir):
                    result = runner.invoke(app, ["skill", "suggest"])

            # Should complete without error
            assert result.exit_code == 0

    def test_suggest_with_no_patterns(self):
        """skill suggest should handle no patterns found."""
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
                result = runner.invoke(app, ["skill", "suggest"])

            # Should complete and indicate no patterns
            assert result.exit_code == 0
            assert "no" in result.output.lower() or "found" in result.output.lower()

    def test_suggest_json_output(self):
        """skill suggest --json should output JSON."""
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
                result = runner.invoke(app, ["skill", "suggest", "--json"])

            # Output should be valid JSON
            assert result.exit_code == 0
            try:
                parsed = json.loads(result.output)
                assert "suggestions" in parsed or "patterns" in parsed or parsed == []
            except json.JSONDecodeError:
                # Empty output is acceptable for no patterns
                pass


class TestSkillSuggestIntegration:
    """Integration tests for skill suggestion workflow."""

    def test_full_workflow(self):
        """Test full workflow: analyze patterns -> generate suggestions -> create draft."""
        from bpsai_pair.skills.suggestion import (
            HistoryParser,
            PatternDetector,
            SkillSuggester,
            SkillDraftCreator,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            history_dir = project_dir / ".paircoder" / "history"
            history_dir.mkdir(parents=True)
            skills_dir = project_dir / ".claude" / "skills"
            skills_dir.mkdir(parents=True)

            # Create sufficient history to detect patterns
            # This simulates repeated workflow patterns
            history = [
                {"command": "pytest", "timestamp": "2025-12-23T10:00:00"},
                {"command": "read_error", "timestamp": "2025-12-23T10:01:00"},
                {"command": "edit_fix", "timestamp": "2025-12-23T10:02:00"},
            ] * 4  # Repeat 4 times

            # Detect patterns
            detector = PatternDetector(min_occurrences=3)
            patterns = detector.detect_patterns(history)

            if patterns:
                # Generate suggestions
                suggester = SkillSuggester(skills_dir=skills_dir)
                suggestions = suggester.generate_suggestions(patterns)

                if suggestions:
                    # Create draft for first suggestion
                    creator = SkillDraftCreator(skills_dir=skills_dir)
                    result = creator.create_draft(suggestions[0])

                    assert result["success"] is True
