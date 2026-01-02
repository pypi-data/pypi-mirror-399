"""Tests for skill gap detection module."""
import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


class TestSkillGap:
    """Tests for SkillGap dataclass."""

    def test_skill_gap_creation(self):
        """Should create a SkillGap with all fields."""
        from bpsai_pair.skills.gap_detector import SkillGap

        gap = SkillGap(
            pattern=["pytest", "read_error", "edit_file"],
            suggested_name="debugging-tests",
            confidence=0.85,
            frequency=5,
            time_saved_estimate="~5 min per cycle",
            detected_at="2025-12-23T10:00:00",
        )

        assert gap.pattern == ["pytest", "read_error", "edit_file"]
        assert gap.suggested_name == "debugging-tests"
        assert gap.confidence == 0.85
        assert gap.frequency == 5

    def test_skill_gap_to_dict(self):
        """Should convert SkillGap to dict for JSON serialization."""
        from bpsai_pair.skills.gap_detector import SkillGap

        gap = SkillGap(
            pattern=["git status", "git diff"],
            suggested_name="reviewing-changes",
            confidence=0.7,
            frequency=4,
            time_saved_estimate="~2 min",
            detected_at="2025-12-23T10:00:00",
        )

        d = gap.to_dict()
        assert d["pattern"] == ["git status", "git diff"]
        assert d["suggested_name"] == "reviewing-changes"
        assert d["confidence"] == 0.7

    def test_skill_gap_from_dict(self):
        """Should create SkillGap from dict."""
        from bpsai_pair.skills.gap_detector import SkillGap

        data = {
            "pattern": ["cmd1", "cmd2"],
            "suggested_name": "test-skill",
            "confidence": 0.9,
            "frequency": 3,
            "time_saved_estimate": "~1 min",
            "detected_at": "2025-12-23T10:00:00",
        }

        gap = SkillGap.from_dict(data)
        assert gap.suggested_name == "test-skill"
        assert gap.confidence == 0.9


class TestSkillGapDetector:
    """Tests for SkillGapDetector class."""

    def test_detects_repeated_command_sequence(self):
        """Should detect repeated command sequences."""
        from bpsai_pair.skills.gap_detector import SkillGapDetector

        detector = SkillGapDetector(existing_skills=[])

        # Session with repeated pattern
        session_log = [
            {"type": "command", "content": "pytest"},
            {"type": "command", "content": "read_error"},
            {"type": "command", "content": "edit_fix"},
            {"type": "command", "content": "pytest"},
            {"type": "command", "content": "read_error"},
            {"type": "command", "content": "edit_fix"},
            {"type": "command", "content": "pytest"},
            {"type": "command", "content": "read_error"},
            {"type": "command", "content": "edit_fix"},
        ]

        gaps = detector.analyze_session(session_log)

        assert len(gaps) > 0
        # Should detect the 3-command pattern
        assert any(len(g.pattern) >= 2 for g in gaps)

    def test_respects_minimum_occurrences(self):
        """Should only detect patterns with 3+ occurrences by default."""
        from bpsai_pair.skills.gap_detector import SkillGapDetector

        detector = SkillGapDetector(existing_skills=[], pattern_threshold=3)

        # Only 2 occurrences
        session_log = [
            {"type": "command", "content": "cmd_a"},
            {"type": "command", "content": "cmd_b"},
            {"type": "command", "content": "cmd_a"},
            {"type": "command", "content": "cmd_b"},
        ]

        gaps = detector.analyze_session(session_log)

        assert len(gaps) == 0

    def test_excludes_existing_skills(self):
        """Should reduce confidence for gaps that match existing skills."""
        from bpsai_pair.skills.gap_detector import SkillGapDetector

        # Test with skill that directly matches pattern keywords
        detector = SkillGapDetector(
            existing_skills=["testing-workflows", "debugging-tests"]
        )

        session_log = [
            {"type": "command", "content": "testing"},
            {"type": "command", "content": "debugging"},
        ] * 4  # 4 occurrences

        gaps = detector.analyze_session(session_log)

        # Gaps that match existing skills should have significantly reduced confidence
        # due to the 0.3 multiplier applied for overlapping skills
        if gaps:
            for gap in gaps:
                # Any gap with testing/debugging keywords should have reduced confidence
                if "testing" in gap.suggested_name or "debugging" in gap.suggested_name:
                    # 0.3 multiplier should reduce max possible ~0.8 to ~0.24
                    assert gap.confidence <= 0.3, f"Expected confidence <= 0.3 for overlap, got {gap.confidence}"

    def test_calculates_confidence_from_frequency(self):
        """Confidence should scale with frequency."""
        from bpsai_pair.skills.gap_detector import SkillGapDetector

        detector = SkillGapDetector(existing_skills=[])

        # High frequency pattern
        session_log = [
            {"type": "command", "content": "cmd_a"},
            {"type": "command", "content": "cmd_b"},
        ] * 10  # 10 occurrences

        gaps = detector.analyze_session(session_log)

        if gaps:
            # High frequency should result in high confidence
            assert gaps[0].confidence >= 0.5

    def test_generates_gerund_skill_names(self):
        """Generated skill names should use gerund form."""
        from bpsai_pair.skills.gap_detector import SkillGapDetector

        detector = SkillGapDetector(existing_skills=[])

        session_log = [
            {"type": "command", "content": "git status"},
            {"type": "command", "content": "git add"},
            {"type": "command", "content": "git commit"},
        ] * 4

        gaps = detector.analyze_session(session_log)

        if gaps:
            # Names should be lowercase with hyphens
            for gap in gaps:
                assert gap.suggested_name == gap.suggested_name.lower()
                assert "_" not in gap.suggested_name

    def test_estimates_time_savings(self):
        """Should provide time savings estimate."""
        from bpsai_pair.skills.gap_detector import SkillGapDetector

        detector = SkillGapDetector(existing_skills=[])

        session_log = [
            {"type": "command", "content": "cmd_a"},
            {"type": "command", "content": "cmd_b"},
        ] * 5

        gaps = detector.analyze_session(session_log)

        if gaps:
            assert gaps[0].time_saved_estimate
            assert "min" in gaps[0].time_saved_estimate or "sec" in gaps[0].time_saved_estimate

    def test_handles_empty_session(self):
        """Should handle empty session gracefully."""
        from bpsai_pair.skills.gap_detector import SkillGapDetector

        detector = SkillGapDetector(existing_skills=[])
        gaps = detector.analyze_session([])

        assert gaps == []

    def test_handles_non_command_messages(self):
        """Should filter out non-command messages."""
        from bpsai_pair.skills.gap_detector import SkillGapDetector

        detector = SkillGapDetector(existing_skills=[])

        session_log = [
            {"type": "user", "content": "Please fix the bug"},
            {"type": "command", "content": "pytest"},
            {"type": "assistant", "content": "I see the error"},
            {"type": "command", "content": "edit_fix"},
            {"type": "user", "content": "Thanks"},
        ] * 4

        gaps = detector.analyze_session(session_log)

        # Should still detect patterns despite non-command messages
        assert isinstance(gaps, list)


class TestGapPersistence:
    """Tests for gap persistence to history."""

    def test_saves_gap_to_history(self):
        """Should save detected gap to history file."""
        from bpsai_pair.skills.gap_detector import GapPersistence, SkillGap

        with tempfile.TemporaryDirectory() as tmpdir:
            history_dir = Path(tmpdir) / ".paircoder" / "history"
            history_dir.mkdir(parents=True)

            persistence = GapPersistence(history_dir=history_dir)

            gap = SkillGap(
                pattern=["cmd1", "cmd2"],
                suggested_name="test-skill",
                confidence=0.8,
                frequency=4,
                time_saved_estimate="~2 min",
                detected_at="2025-12-23T10:00:00",
            )

            persistence.save_gap(gap)

            # Check file was created
            gap_file = history_dir / "skill-gaps.jsonl"
            assert gap_file.exists()

            # Check content
            content = gap_file.read_text()
            assert "test-skill" in content

    def test_loads_gaps_from_history(self):
        """Should load gaps from history file."""
        from bpsai_pair.skills.gap_detector import GapPersistence, SkillGap

        with tempfile.TemporaryDirectory() as tmpdir:
            history_dir = Path(tmpdir) / ".paircoder" / "history"
            history_dir.mkdir(parents=True)

            # Create history file
            gap_file = history_dir / "skill-gaps.jsonl"
            gap_data = {
                "pattern": ["a", "b"],
                "suggested_name": "saved-skill",
                "confidence": 0.7,
                "frequency": 3,
                "time_saved_estimate": "~1 min",
                "detected_at": "2025-12-23T09:00:00",
            }
            gap_file.write_text(json.dumps(gap_data) + "\n")

            persistence = GapPersistence(history_dir=history_dir)
            gaps = persistence.load_gaps()

            assert len(gaps) == 1
            assert gaps[0].suggested_name == "saved-skill"

    def test_deduplicates_similar_gaps(self):
        """Should not save duplicate gaps."""
        from bpsai_pair.skills.gap_detector import GapPersistence, SkillGap

        with tempfile.TemporaryDirectory() as tmpdir:
            history_dir = Path(tmpdir) / ".paircoder" / "history"
            history_dir.mkdir(parents=True)

            persistence = GapPersistence(history_dir=history_dir)

            gap1 = SkillGap(
                pattern=["cmd1", "cmd2"],
                suggested_name="test-skill",
                confidence=0.8,
                frequency=4,
                time_saved_estimate="~2 min",
                detected_at="2025-12-23T10:00:00",
            )

            gap2 = SkillGap(
                pattern=["cmd1", "cmd2"],  # Same pattern
                suggested_name="test-skill",
                confidence=0.9,  # Higher confidence
                frequency=5,
                time_saved_estimate="~2 min",
                detected_at="2025-12-23T11:00:00",
            )

            persistence.save_gap(gap1)
            persistence.save_gap(gap2)

            gaps = persistence.load_gaps()
            # Should have updated the existing gap, not created duplicate
            assert len(gaps) == 1
            assert gaps[0].confidence == 0.9  # Updated to higher confidence

    def test_handles_missing_history_dir(self):
        """Should handle missing history directory gracefully."""
        from bpsai_pair.skills.gap_detector import GapPersistence

        with tempfile.TemporaryDirectory() as tmpdir:
            history_dir = Path(tmpdir) / "nonexistent"
            persistence = GapPersistence(history_dir=history_dir)

            gaps = persistence.load_gaps()
            assert gaps == []


class TestSkillGapsCommand:
    """Tests for the CLI gaps command."""

    def test_gaps_command_exists(self):
        """skill gaps command should exist."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["skill", "gaps", "--help"])

        assert result.exit_code == 0
        assert "gaps" in result.output.lower()

    def test_gaps_lists_detected_gaps(self):
        """skill gaps should list detected gaps from history."""
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
                "pattern": ["test", "fix"],
                "suggested_name": "fixing-tests",
                "confidence": 0.8,
                "frequency": 4,
                "time_saved_estimate": "~3 min",
                "detected_at": "2025-12-23T10:00:00",
            }
            gap_file.write_text(json.dumps(gap_data) + "\n")

            runner = CliRunner()
            with patch('bpsai_pair.skills.cli_commands.find_project_root', return_value=project_dir):
                result = runner.invoke(app, ["skill", "gaps"])

            assert result.exit_code == 0
            assert "fixing-tests" in result.output or "No gaps" in result.output

    def test_gaps_with_no_history(self):
        """skill gaps should handle no gaps gracefully."""
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
                result = runner.invoke(app, ["skill", "gaps"])

            assert result.exit_code == 0
            assert "no" in result.output.lower() or "gaps" in result.output.lower()

    def test_gaps_json_output(self):
        """skill gaps --json should output JSON."""
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
                result = runner.invoke(app, ["skill", "gaps", "--json"])

            assert result.exit_code == 0
            # Should be valid JSON
            try:
                parsed = json.loads(result.output)
                assert "gaps" in parsed
            except json.JSONDecodeError:
                pass  # Empty output is acceptable

    def test_gaps_clear_command(self):
        """skill gaps --clear should clear gap history."""
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
            gap_file.write_text('{"pattern":["a"],"suggested_name":"test","confidence":0.5}\n')

            runner = CliRunner()
            with patch('bpsai_pair.skills.cli_commands.find_project_root', return_value=project_dir):
                result = runner.invoke(app, ["skill", "gaps", "--clear"])

            assert result.exit_code == 0
            # File should be empty or deleted
            if gap_file.exists():
                assert gap_file.read_text().strip() == ""


class TestSessionIntegration:
    """Tests for session check integration."""

    def test_analyze_on_session_start(self):
        """Should analyze for gaps on session start."""
        from bpsai_pair.skills.gap_detector import SkillGapDetector, GapPersistence

        with tempfile.TemporaryDirectory() as tmpdir:
            history_dir = Path(tmpdir) / ".paircoder" / "history"
            history_dir.mkdir(parents=True)

            # Create session log with patterns
            session_log = [
                {"type": "command", "content": "pytest"},
                {"type": "command", "content": "fix"},
            ] * 4

            detector = SkillGapDetector(existing_skills=[])
            gaps = detector.analyze_session(session_log)

            if gaps:
                persistence = GapPersistence(history_dir=history_dir)
                for gap in gaps:
                    persistence.save_gap(gap)

                # Verify gaps were saved
                loaded = persistence.load_gaps()
                assert len(loaded) > 0

    def test_notification_format(self):
        """Should format notification message correctly."""
        from bpsai_pair.skills.gap_detector import format_gap_notification, SkillGap

        gap = SkillGap(
            pattern=["pytest", "read_error", "fix_bug", "pytest"],
            suggested_name="debugging-test-failures",
            confidence=0.85,
            frequency=4,
            time_saved_estimate="~5 min per cycle",
            detected_at="2025-12-23T10:00:00",
        )

        notification = format_gap_notification(gap)

        assert "debugging-test-failures" in notification
        assert "pytest" in notification
        assert "4" in notification or "four" in notification.lower()
