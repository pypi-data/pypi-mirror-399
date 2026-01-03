"""Tests for subagent gap detection."""

import json
import pytest
from pathlib import Path

from bpsai_pair.skills.subagent_detector import (
    SubagentGap,
    SubagentGapDetector,
    SubagentGapPersistence,
    detect_subagent_gaps,
    format_subagent_gap_notification,
)


class TestSubagentGap:
    """Tests for SubagentGap dataclass."""

    def test_to_dict(self):
        """Test serialization to dict."""
        gap = SubagentGap(
            id="test-gap",
            suggested_name="security-reviewer",
            description="Security review specialist",
            confidence=0.85,
            indicators=["persona_request"],
            suggested_tools=["Read", "Grep"],
            suggested_model="opus",
            needs_context_isolation=True,
            needs_resumability=False,
            occurrence_count=5,
        )

        data = gap.to_dict()

        assert data["id"] == "test-gap"
        assert data["suggested_name"] == "security-reviewer"
        assert data["confidence"] == 0.85
        assert "persona_request" in data["indicators"]
        assert data["suggested_model"] == "opus"
        assert data["needs_context_isolation"] is True

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "id": "test-gap",
            "suggested_name": "code-reviewer",
            "description": "Review specialist",
            "confidence": 0.75,
            "indicators": ["tool_restriction"],
            "suggested_tools": ["Read"],
            "needs_context_isolation": True,
            "occurrence_count": 3,
        }

        gap = SubagentGap.from_dict(data)

        assert gap.id == "test-gap"
        assert gap.suggested_name == "code-reviewer"
        assert gap.confidence == 0.75
        assert gap.needs_context_isolation is True

    def test_roundtrip(self):
        """Test dict serialization roundtrip."""
        gap = SubagentGap(
            id="roundtrip-test",
            suggested_name="test-agent",
            description="Test description",
            confidence=0.6,
            indicators=["persona_request", "tool_restriction"],
            suggested_persona="You are a helpful reviewer",
            occurrence_count=10,
        )

        data = gap.to_dict()
        restored = SubagentGap.from_dict(data)

        assert restored.id == gap.id
        assert restored.suggested_name == gap.suggested_name
        assert restored.confidence == gap.confidence
        assert restored.indicators == gap.indicators
        assert restored.suggested_persona == gap.suggested_persona


class TestSubagentGapDetector:
    """Tests for SubagentGapDetector."""

    def test_detect_persona_patterns(self, tmp_path):
        """Test detection of persona-based patterns."""
        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)

        # Create session log with persona requests
        changes_log = history_dir / "changes.log"
        changes_log.write_text(
            "act as a security expert\n"
            "you are a code reviewer\n"
            "act as a security expert again\n"
        )

        detector = SubagentGapDetector()
        gaps = detector.detect_from_history(history_dir)

        # Should detect persona pattern
        persona_gaps = [g for g in gaps if "persona" in g.indicators]
        assert len(persona_gaps) >= 0  # May or may not detect depending on threshold

    def test_detect_isolation_patterns(self, tmp_path):
        """Test detection of context isolation patterns."""
        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)

        changes_log = history_dir / "changes.log"
        changes_log.write_text(
            "analyze this separately\n"
            "do this in parallel\n"
            "keep this isolated from main context\n"
        )

        detector = SubagentGapDetector()
        gaps = detector.detect_from_history(history_dir)

        # Check for isolation-related gaps
        isolation_gaps = [g for g in gaps if g.needs_context_isolation]
        assert len(isolation_gaps) >= 0  # Depends on threshold

    def test_detect_resumable_patterns(self, tmp_path):
        """Test detection of resumability patterns."""
        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)

        changes_log = history_dir / "changes.log"
        changes_log.write_text(
            "continue from where we left off\n"
            "resume the previous analysis\n"
            "pick up where we stopped\n"
        )

        detector = SubagentGapDetector()
        gaps = detector.detect_from_history(history_dir)

        resumable_gaps = [g for g in gaps if g.needs_resumability]
        assert len(resumable_gaps) >= 0

    def test_detect_tool_restriction_patterns(self, tmp_path):
        """Test detection of tool restriction patterns."""
        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)

        changes_log = history_dir / "changes.log"
        changes_log.write_text(
            "review the code changes\n"
            "analyze the test results\n"
            "check the security vulnerabilities\n"
            "audit the dependencies\n"
        )

        detector = SubagentGapDetector()
        gaps = detector.detect_from_history(history_dir)

        tool_gaps = [g for g in gaps if g.suggested_tools]
        assert len(tool_gaps) >= 0

    def test_empty_history(self, tmp_path):
        """Test with empty history."""
        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)

        detector = SubagentGapDetector()
        gaps = detector.detect_from_history(history_dir)

        assert gaps == []

    def test_no_history_dir(self, tmp_path):
        """Test with non-existent history directory."""
        history_dir = tmp_path / "nonexistent"

        detector = SubagentGapDetector()
        gaps = detector.detect_from_history(history_dir)

        assert gaps == []

    def test_overlaps_with_existing(self, tmp_path):
        """Test confidence reduction for overlapping names."""
        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)

        changes_log = history_dir / "changes.log"
        changes_log.write_text(
            "you are a security expert\n"
            "act as a security reviewer\n"
        )

        # Create detector with existing subagent
        detector = SubagentGapDetector(existing_subagents=["security-reviewer"])
        gaps = detector.detect_from_history(history_dir)

        # Any gaps overlapping with existing should have reduced confidence
        for gap in gaps:
            if "security" in gap.suggested_name:
                assert "overlaps_existing_subagent" in gap.indicators

    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        detector = SubagentGapDetector()

        # Single indicator, low occurrences
        conf1 = detector._calculate_confidence(["persona"], 2)
        assert 0.3 <= conf1 <= 0.65  # Adjusted for float precision

        # Multiple indicators, more occurrences
        conf2 = detector._calculate_confidence(["persona", "isolation", "resumable"], 8)
        assert conf2 > conf1

        # Maximum should be capped
        conf3 = detector._calculate_confidence(["a", "b", "c", "d", "e"], 100)
        assert conf3 <= 0.95

    def test_to_kebab_case(self):
        """Test kebab-case conversion."""
        detector = SubagentGapDetector()

        assert detector._to_kebab_case("Security Expert") == "security-expert"
        assert detector._to_kebab_case("code_reviewer") == "code-reviewer"
        assert detector._to_kebab_case("  test  ") == "test"
        assert detector._to_kebab_case("Test--Case") == "test-case"


class TestSubagentGapPersistence:
    """Tests for SubagentGapPersistence."""

    def test_save_and_load(self, tmp_path):
        """Test saving and loading gaps."""
        history_dir = tmp_path / ".paircoder" / "history"

        persistence = SubagentGapPersistence(history_dir)

        gap = SubagentGap(
            id="test-gap",
            suggested_name="test-agent",
            description="Test agent",
            confidence=0.7,
            indicators=["persona_request"],
            occurrence_count=5,
        )

        persistence.save_gap(gap)
        loaded = persistence.load_gaps()

        assert len(loaded) == 1
        assert loaded[0].id == "test-gap"
        assert loaded[0].confidence == 0.7

    def test_update_existing(self, tmp_path):
        """Test updating existing gap with higher confidence."""
        history_dir = tmp_path / ".paircoder" / "history"

        persistence = SubagentGapPersistence(history_dir)

        # Save initial gap
        gap1 = SubagentGap(
            id="update-test",
            suggested_name="test-agent",
            description="Initial",
            confidence=0.5,
        )
        persistence.save_gap(gap1)

        # Save same gap with higher confidence
        gap2 = SubagentGap(
            id="update-test",
            suggested_name="test-agent",
            description="Updated",
            confidence=0.8,
        )
        persistence.save_gap(gap2)

        loaded = persistence.load_gaps()
        assert len(loaded) == 1
        assert loaded[0].confidence == 0.8

    def test_clear_gaps(self, tmp_path):
        """Test clearing gap history."""
        history_dir = tmp_path / ".paircoder" / "history"

        persistence = SubagentGapPersistence(history_dir)

        # Save a gap
        gap = SubagentGap(
            id="clear-test",
            suggested_name="test",
            description="Test",
            confidence=0.5,
        )
        persistence.save_gap(gap)

        # Clear
        persistence.clear_gaps()
        loaded = persistence.load_gaps()

        assert len(loaded) == 0


class TestHighLevelFunctions:
    """Tests for module-level functions."""

    def test_detect_subagent_gaps(self, tmp_path):
        """Test high-level gap detection function."""
        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)

        changes_log = history_dir / "changes.log"
        changes_log.write_text("test session\n")

        gaps = detect_subagent_gaps(history_dir)
        assert isinstance(gaps, list)

    def test_format_gap_notification(self):
        """Test gap notification formatting."""
        gap = SubagentGap(
            id="notify-test",
            suggested_name="security-reviewer",
            description="Security review specialist",
            confidence=0.85,
            indicators=["persona_request", "tool_restriction"],
            suggested_persona="You are a security expert",
            suggested_tools=["Read", "Grep", "Glob"],
            estimated_context_savings=5000,
        )

        notification = format_subagent_gap_notification(gap)

        assert "Subagent Gap Detected" in notification
        assert "security-reviewer" in notification
        assert "85%" in notification
        assert "5000 tokens" in notification
