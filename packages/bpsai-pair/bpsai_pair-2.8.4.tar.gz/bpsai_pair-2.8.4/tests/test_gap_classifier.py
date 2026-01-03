"""Tests for unified gap classification."""

import json
import pytest
from pathlib import Path

from bpsai_pair.skills.gap_detector import SkillGap
from bpsai_pair.skills.subagent_detector import SubagentGap
from bpsai_pair.skills.classifier import (
    GapType,
    ClassifiedGap,
    ClassificationScores,
    SkillRecommendation,
    SubagentRecommendation,
    AllGaps,
    GapClassifier,
    detect_and_classify_all,
    format_classification_report,
)


class TestGapType:
    """Tests for GapType enum."""

    def test_values(self):
        """Test enum values."""
        assert GapType.SKILL.value == "skill"
        assert GapType.SUBAGENT.value == "subagent"
        assert GapType.AMBIGUOUS.value == "ambiguous"


class TestClassifiedGap:
    """Tests for ClassifiedGap dataclass."""

    def test_to_dict(self):
        """Test serialization to dict."""
        gap = ClassifiedGap(
            id="test-gap",
            gap_type=GapType.SKILL,
            confidence=0.85,
            reasoning="Pattern would be useful across tools",
            suggested_name="testing-workflows",
            description="Test workflow automation",
            source_commands=["pytest", "git commit"],
            occurrence_count=5,
            portability_score=0.8,
            simplicity_score=0.7,
            skill_recommendation=SkillRecommendation(
                suggested_name="testing-workflows",
                estimated_portability=["claude-code", "cursor"],
            ),
        )

        data = gap.to_dict()

        assert data["id"] == "test-gap"
        assert data["gap_type"] == "skill"
        assert data["confidence"] == 0.85
        assert "scores" in data
        assert data["scores"]["portability"] == 0.8
        assert "skill_recommendation" in data

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "id": "test-gap",
            "gap_type": "subagent",
            "confidence": 0.75,
            "reasoning": "Needs context isolation",
            "suggested_name": "security-reviewer",
            "description": "Security review",
            "scores": {
                "isolation": 0.8,
                "persona": 0.7,
            },
            "subagent_recommendation": {
                "suggested_name": "security-reviewer",
                "suggested_model": "opus",
                "persona_hint": "You are a security expert",
            },
        }

        gap = ClassifiedGap.from_dict(data)

        assert gap.id == "test-gap"
        assert gap.gap_type == GapType.SUBAGENT
        assert gap.confidence == 0.75
        assert gap.isolation_score == 0.8
        assert gap.subagent_recommendation is not None
        assert gap.subagent_recommendation.suggested_model == "opus"

    def test_roundtrip(self):
        """Test dict serialization roundtrip."""
        gap = ClassifiedGap(
            id="roundtrip-test",
            gap_type=GapType.AMBIGUOUS,
            confidence=0.6,
            reasoning="Could be either",
            suggested_name="testing",
            description="Test",
            skill_recommendation=SkillRecommendation(
                suggested_name="testing",
                allowed_tools=["Read", "Grep"],
            ),
            subagent_recommendation=SubagentRecommendation(
                suggested_name="testing",
                suggested_model="sonnet",
            ),
        )

        data = gap.to_dict()
        restored = ClassifiedGap.from_dict(data)

        assert restored.id == gap.id
        assert restored.gap_type == gap.gap_type
        assert restored.confidence == gap.confidence
        assert restored.skill_recommendation is not None
        assert restored.subagent_recommendation is not None


class TestGapClassifier:
    """Tests for GapClassifier."""

    def test_classify_skill_gap(self):
        """Test classifying a skill gap."""
        skill_gap = SkillGap(
            pattern=["pytest", "git commit", "git push"],
            suggested_name="testing-workflows",
            confidence=0.8,
            frequency=5,
            time_saved_estimate="~5 min",
        )

        classifier = GapClassifier()
        result = classifier.classify(skill_gap)

        assert isinstance(result, ClassifiedGap)
        assert result.gap_type == GapType.SKILL
        assert result.portability_score > 0.5

    def test_classify_subagent_gap(self):
        """Test classifying a subagent gap."""
        subagent_gap = SubagentGap(
            id="persona-security",
            suggested_name="security-reviewer",
            description="Security expert reviewer",
            confidence=0.85,
            indicators=["persona_request"],
            suggested_persona="You are a security expert",
            needs_context_isolation=True,
            occurrence_count=3,
        )

        classifier = GapClassifier()
        result = classifier.classify(subagent_gap)

        assert isinstance(result, ClassifiedGap)
        assert result.gap_type == GapType.SUBAGENT
        assert result.isolation_score > 0.5
        assert result.persona_score > 0.5

    def test_classify_all(self):
        """Test classifying multiple gaps."""
        skill_gap = SkillGap(
            pattern=["lint", "format"],
            suggested_name="linting-code",
            confidence=0.7,
            frequency=4,
            time_saved_estimate="~2 min",
        )

        subagent_gap = SubagentGap(
            id="persona-analyst",
            suggested_name="code-analyst",
            description="Code analysis specialist",
            confidence=0.75,
            indicators=["persona_request", "context_isolation"],
            needs_context_isolation=True,
            occurrence_count=3,
        )

        all_gaps = AllGaps(skills=[skill_gap], subagents=[subagent_gap])

        classifier = GapClassifier()
        results = classifier.classify_all(all_gaps)

        assert len(results) == 2
        assert any(g.gap_type == GapType.SKILL for g in results)
        assert any(g.gap_type == GapType.SUBAGENT for g in results)

    def test_determine_type_skill(self):
        """Test type determination for skill-like scores."""
        classifier = GapClassifier()

        scores = ClassificationScores(
            portability=0.8,
            simplicity=0.7,
            isolation=0.2,
            persona=0.1,
            resumability=0.0,
        )

        gap_type = classifier._determine_type(scores)
        assert gap_type == GapType.SKILL

    def test_determine_type_subagent(self):
        """Test type determination for subagent-like scores."""
        classifier = GapClassifier()

        scores = ClassificationScores(
            portability=0.2,
            simplicity=0.3,
            isolation=0.8,
            persona=0.7,
            resumability=0.6,
        )

        gap_type = classifier._determine_type(scores)
        assert gap_type == GapType.SUBAGENT

    def test_determine_type_ambiguous(self):
        """Test type determination for ambiguous scores."""
        classifier = GapClassifier()

        scores = ClassificationScores(
            portability=0.5,
            simplicity=0.5,
            isolation=0.5,
            persona=0.5,
            resumability=0.5,
        )

        gap_type = classifier._determine_type(scores)
        # Should be ambiguous due to close scores
        assert gap_type in [GapType.SKILL, GapType.SUBAGENT, GapType.AMBIGUOUS]

    def test_generate_reasoning(self):
        """Test reasoning generation."""
        classifier = GapClassifier()

        skill_gap = SkillGap(
            pattern=["test", "build"],
            suggested_name="testing",
            confidence=0.7,
            frequency=5,
            time_saved_estimate="~3 min",
        )

        scores = ClassificationScores(portability=0.8, simplicity=0.7)
        reasoning = classifier._generate_reasoning(skill_gap, scores, GapType.SKILL)

        assert "SKILL" in reasoning
        assert "useful across" in reasoning or "simple" in reasoning

    def test_merge_overlapping_gaps(self):
        """Test merging overlapping skill and subagent gaps."""
        classifier = GapClassifier()

        # Same name in both
        skill_gap = SkillGap(
            pattern=["review"],
            suggested_name="reviewing-code",
            confidence=0.6,
            frequency=3,
            time_saved_estimate="~2 min",
        )

        subagent_gap = SubagentGap(
            id="review",
            suggested_name="reviewing-code",
            description="Code reviewer",
            confidence=0.8,
            indicators=["persona_request"],
            occurrence_count=5,
        )

        all_gaps = AllGaps(skills=[skill_gap], subagents=[subagent_gap])
        merged = classifier._merge_overlapping_gaps(all_gaps)

        # Should keep only one (higher confidence)
        assert len(merged) == 1
        assert isinstance(merged[0], SubagentGap)

    def test_build_skill_recommendation(self):
        """Test skill recommendation building."""
        classifier = GapClassifier()

        skill_gap = SkillGap(
            pattern=["test", "lint"],
            suggested_name="testing-linting",
            confidence=0.8,
            frequency=5,
            time_saved_estimate="~3 min",
        )

        scores = ClassificationScores(portability=0.8)
        rec = classifier._build_skill_recommendation(skill_gap, scores)

        assert rec is not None
        assert rec.suggested_name == "testing-linting"
        assert "claude-code" in rec.estimated_portability

    def test_build_subagent_recommendation(self):
        """Test subagent recommendation building."""
        classifier = GapClassifier()

        subagent_gap = SubagentGap(
            id="test",
            suggested_name="test-agent",
            description="Test agent",
            confidence=0.7,
            indicators=["persona_request"],
            suggested_model="opus",
            suggested_persona="You are a tester",
            occurrence_count=3,
        )

        scores = ClassificationScores(persona=0.8)
        rec = classifier._build_subagent_recommendation(subagent_gap, scores)

        assert rec is not None
        assert rec.suggested_model == "opus"
        assert rec.persona_hint == "You are a tester"


class TestHighLevelFunctions:
    """Tests for module-level functions."""

    def test_detect_and_classify_all(self, tmp_path):
        """Test high-level detection and classification."""
        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)

        changes_log = history_dir / "changes.log"
        changes_log.write_text("test session\n")

        results = detect_and_classify_all(history_dir)
        assert isinstance(results, list)

    def test_format_classification_report_empty(self):
        """Test report formatting with no gaps."""
        report = format_classification_report([])
        assert "No gaps" in report

    def test_format_classification_report_with_gaps(self):
        """Test report formatting with gaps."""
        gaps = [
            ClassifiedGap(
                id="skill-1",
                gap_type=GapType.SKILL,
                confidence=0.8,
                reasoning="Test",
                suggested_name="test-skill",
                description="Test skill",
            ),
            ClassifiedGap(
                id="subagent-1",
                gap_type=GapType.SUBAGENT,
                confidence=0.7,
                reasoning="Test",
                suggested_name="test-agent",
                description="Test agent",
            ),
        ]

        report = format_classification_report(gaps)

        assert "Gap Classification Report" in report
        assert "SKILLS" in report
        assert "SUBAGENTS" in report
        assert "test-skill" in report
        assert "test-agent" in report
        assert "Total: 2" in report


class TestClassificationScores:
    """Tests for ClassificationScores."""

    def test_default_values(self):
        """Test default score values."""
        scores = ClassificationScores()

        assert scores.portability == 0.0
        assert scores.isolation == 0.0
        assert scores.persona == 0.0
        assert scores.resumability == 0.0
        assert scores.simplicity == 0.0

    def test_custom_values(self):
        """Test custom score values."""
        scores = ClassificationScores(
            portability=0.8,
            isolation=0.3,
            persona=0.5,
        )

        assert scores.portability == 0.8
        assert scores.isolation == 0.3
        assert scores.persona == 0.5
