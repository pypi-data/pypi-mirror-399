"""Tests for skill quality gates."""

import pytest

from bpsai_pair.skills.gates import (
    GateStatus,
    GateResult,
    QualityGateResult,
    GapQualityGate,
    GENERIC_COMMANDS,
    evaluate_gap_quality,
    format_gate_result,
)
from bpsai_pair.skills.classifier import ClassifiedGap, GapType


def make_gap(
    name: str = "test-skill",
    description: str = "Test skill description",
    source_commands: list[str] | None = None,
    occurrence_count: int = 5,
    gap_type: GapType = GapType.SKILL,
    confidence: float = 0.7,
) -> ClassifiedGap:
    """Create a test ClassifiedGap."""
    return ClassifiedGap(
        id=f"GAP-{name}",
        gap_type=gap_type,
        confidence=confidence,
        reasoning="Test reasoning",
        suggested_name=name,
        description=description,
        source_commands=source_commands or ["git status", "pytest", "git diff"],
        occurrence_count=occurrence_count,
        portability_score=0.5,
        isolation_score=0.3,
        persona_score=0.2,
        resumability_score=0.1,
        simplicity_score=0.6,
    )


class TestGateStatus:
    """Tests for GateStatus enum."""

    def test_gate_status_values(self):
        """Test that all expected status values exist."""
        assert GateStatus.PASS.value == "pass"
        assert GateStatus.WARN.value == "warn"
        assert GateStatus.BLOCK.value == "block"


class TestGateResult:
    """Tests for GateResult dataclass."""

    def test_create_gate_result(self):
        """Test creating a gate result."""
        result = GateResult(
            gate_name="redundancy",
            status=GateStatus.PASS,
            score=0.8,
            reason="No redundancy detected",
        )
        assert result.gate_name == "redundancy"
        assert result.status == GateStatus.PASS
        assert result.score == 0.8
        assert result.reason == "No redundancy detected"

    def test_gate_result_to_dict(self):
        """Test converting gate result to dict."""
        result = GateResult(
            gate_name="novelty",
            status=GateStatus.WARN,
            score=0.4,
            reason="Some generic commands",
            details="Consider adding more specialized commands",
        )
        d = result.to_dict()
        assert d["gate_name"] == "novelty"
        assert d["status"] == "warn"
        assert d["score"] == 0.4
        assert d["details"] == "Consider adding more specialized commands"


class TestQualityGateResult:
    """Tests for QualityGateResult dataclass."""

    def test_can_generate_when_all_pass(self):
        """Test that can_generate is True when all gates pass."""
        result = QualityGateResult(
            gap_id="GAP-001",
            gap_name="test-skill",
            overall_status=GateStatus.PASS,
            gate_results=[
                GateResult("gate1", GateStatus.PASS, 0.8, "OK"),
                GateResult("gate2", GateStatus.PASS, 0.9, "OK"),
            ],
            recommendation="Ready to generate",
            can_generate=True,
        )
        assert result.can_generate is True

    def test_cannot_generate_when_blocked(self):
        """Test that can_generate is False when any gate blocks."""
        result = QualityGateResult(
            gap_id="GAP-001",
            gap_name="test-skill",
            overall_status=GateStatus.BLOCK,
            gate_results=[
                GateResult("gate1", GateStatus.PASS, 0.8, "OK"),
                GateResult("gate2", GateStatus.BLOCK, 0.1, "Failed"),
            ],
            recommendation="Blocked",
            can_generate=False,
        )
        assert result.can_generate is False

    def test_to_dict(self):
        """Test converting quality gate result to dict."""
        result = QualityGateResult(
            gap_id="GAP-001",
            gap_name="test-skill",
            overall_status=GateStatus.PASS,
            gate_results=[],
            recommendation="Ready",
            can_generate=True,
        )
        d = result.to_dict()
        assert d["gap_id"] == "GAP-001"
        assert d["overall_status"] == "pass"
        assert d["can_generate"] is True


class TestGenericCommands:
    """Tests for GENERIC_COMMANDS blocklist."""

    def test_contains_basic_commands(self):
        """Test that common generic commands are in blocklist."""
        assert "pytest" in GENERIC_COMMANDS
        assert "npm test" in GENERIC_COMMANDS
        assert "git add" in GENERIC_COMMANDS
        assert "git commit" in GENERIC_COMMANDS
        assert "pip install" in GENERIC_COMMANDS

    def test_contains_edit_commands(self):
        """Test that generic edit commands are in blocklist."""
        assert "fix" in GENERIC_COMMANDS
        assert "edit" in GENERIC_COMMANDS
        assert "update" in GENERIC_COMMANDS
        assert "change" in GENERIC_COMMANDS


class TestGapQualityGate:
    """Tests for GapQualityGate class."""

    def test_init_default_thresholds(self):
        """Test default thresholds are set."""
        gate = GapQualityGate()
        assert gate.REDUNDANCY_THRESHOLD == 0.3
        assert gate.NOVELTY_THRESHOLD == 0.3
        assert gate.COMPLEXITY_THRESHOLD == 0.3
        assert gate.TIME_VALUE_THRESHOLD == 0.3

    def test_init_with_existing_skills(self):
        """Test initialization with existing skills."""
        gate = GapQualityGate(existing_skills=["testing", "debugging"])
        assert "testing" in gate.existing_skills
        assert "debugging" in gate.existing_skills

    def test_evaluate_passes_good_gap(self):
        """Test that a well-formed gap passes all gates."""
        gate = GapQualityGate()
        gap = make_gap(
            name="debugging-from-logs",
            description="Analyze logs, find errors, suggest fixes",
            source_commands=[
                "grep error logs.txt",
                "analyze stack trace",
                "suggest fix for TypeError",
                "apply recommended patch",
            ],
            occurrence_count=10,
        )
        result = gate.evaluate(gap)
        # Should pass - not generic, complex enough
        assert result.can_generate or result.overall_status == GateStatus.WARN

    def test_evaluate_blocks_generic_commands(self):
        """Test that patterns with only generic commands are blocked."""
        gate = GapQualityGate()
        gap = make_gap(
            name="testing-fixes",
            description="Run pytest and fix errors",
            source_commands=["pytest", "fix", "pytest"],
            occurrence_count=5,
        )
        result = gate.evaluate(gap)
        # Should be blocked due to low novelty (generic commands)
        blocked_gates = [r for r in result.gate_results if r.status == GateStatus.BLOCK]
        assert len(blocked_gates) > 0 or not result.can_generate

    def test_evaluate_blocks_single_command(self):
        """Test that single-command patterns are blocked."""
        gate = GapQualityGate()
        gap = make_gap(
            name="run-tests",
            description="Run tests",
            source_commands=["pytest"],
            occurrence_count=20,
        )
        result = gate.evaluate(gap)
        # Should be blocked due to low complexity
        assert not result.can_generate

    def test_redundancy_check_no_existing_skills(self):
        """Test redundancy check with no existing skills."""
        gate = GapQualityGate()
        result = gate._check_redundancy("debugging", ["analyze logs", "find error"])
        assert result.status == GateStatus.PASS
        assert result.score == 1.0

    def test_redundancy_check_with_overlap(self):
        """Test redundancy check detects name overlap."""
        gate = GapQualityGate(existing_skills=["testing", "debugging"])
        result = gate._check_redundancy("testing-fixes", ["run tests"])
        # "testing" overlaps with existing "testing" skill
        assert result.score < 1.0

    def test_novelty_gate_generic_commands(self):
        """Test novelty gate detects generic commands."""
        gate = GapQualityGate()
        result = gate._check_novelty(["pytest", "git add", "pip install"])
        # All generic commands = low novelty
        assert result.score < 0.5
        assert result.status in [GateStatus.BLOCK, GateStatus.WARN]

    def test_novelty_gate_novel_commands(self):
        """Test novelty gate passes novel commands."""
        gate = GapQualityGate()
        result = gate._check_novelty([
            "analyze_dependencies.py",
            "generate_report.py",
            "send_notification.py",
        ])
        # Novel commands = high novelty
        assert result.score >= 0.5 or result.status == GateStatus.PASS

    def test_novelty_gate_mixed_commands(self):
        """Test novelty gate with mix of generic and novel commands."""
        gate = GapQualityGate()
        result = gate._check_novelty([
            "pytest",  # generic
            "analyze custom report",  # novel
            "git commit",  # generic
            "process special data",  # novel
        ])
        # Mixed = moderate novelty
        assert 0.2 <= result.score <= 0.8

    def test_complexity_gate_simple_pattern(self):
        """Test complexity gate blocks simple patterns."""
        gate = GapQualityGate()
        result = gate._check_complexity(["ls"])
        # Too simple (1 command < MIN_COMMANDS of 3)
        assert result.status in [GateStatus.BLOCK, GateStatus.WARN]

    def test_complexity_gate_complex_pattern(self):
        """Test complexity gate passes complex patterns."""
        gate = GapQualityGate()
        result = gate._check_complexity([
            "analyze logs",
            "find patterns",
            "generate report",
            "send notification",
            "archive results",
        ])
        # Complex enough (5 distinct commands)
        assert result.status == GateStatus.PASS

    def test_complexity_gate_borderline(self):
        """Test complexity gate with borderline complexity."""
        gate = GapQualityGate()
        result = gate._check_complexity(["cmd1", "cmd2", "cmd3"])
        # Exactly at MIN_COMMANDS threshold
        assert result.score >= 0.3  # Should pass threshold

    def test_time_value_gate_high_frequency(self):
        """Test time value gate with high frequency pattern."""
        gate = GapQualityGate()
        result = gate._check_time_value(["cmd1", "cmd2", "cmd3"], occurrence_count=20)
        # High occurrence = high value
        assert result.score > 0.3

    def test_time_value_gate_low_frequency(self):
        """Test time value gate with low frequency pattern."""
        gate = GapQualityGate()
        result = gate._check_time_value(["cmd"], occurrence_count=1)
        # Low occurrence and few commands = low value
        assert result.score < 0.5

    def test_evaluate_returns_recommendation(self):
        """Test that evaluate returns a recommendation."""
        gate = GapQualityGate()
        gap = make_gap()
        result = gate.evaluate(gap)
        assert result.recommendation is not None
        assert len(result.recommendation) > 0


class TestEvaluateGapQuality:
    """Tests for evaluate_gap_quality function."""

    def test_evaluate_gap_quality_returns_result(self):
        """Test that evaluate_gap_quality returns a result."""
        gap = make_gap()
        result = evaluate_gap_quality(gap)
        assert isinstance(result, QualityGateResult)
        assert result.gap_id == gap.id

    def test_evaluate_gap_quality_with_skills_dir(self, tmp_path):
        """Test evaluation with skills directory."""
        # Create a skill directory
        skill_dir = tmp_path / "debugging"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Debugging Skill\nHelps debug issues.")

        gap = make_gap(name="debugging-extended")
        result = evaluate_gap_quality(gap, skills_dir=tmp_path)
        assert isinstance(result, QualityGateResult)


class TestFormatGateResult:
    """Tests for format_gate_result function."""

    def test_format_passed_result(self):
        """Test formatting a passed result."""
        result = QualityGateResult(
            gap_id="GAP-001",
            gap_name="test-skill",
            overall_status=GateStatus.PASS,
            gate_results=[
                GateResult("gate1", GateStatus.PASS, 0.8, "OK"),
            ],
            recommendation="Ready to generate",
            can_generate=True,
        )
        output = format_gate_result(result)
        assert "PASS" in output
        assert "test-skill" in output

    def test_format_blocked_result(self):
        """Test formatting a blocked result."""
        result = QualityGateResult(
            gap_id="GAP-001",
            gap_name="test-skill",
            overall_status=GateStatus.BLOCK,
            gate_results=[
                GateResult("novelty", GateStatus.BLOCK, 0.1, "Too generic"),
            ],
            recommendation="BLOCKED: Too generic",
            can_generate=False,
        )
        output = format_gate_result(result)
        assert "BLOCKED" in output
        assert "novelty" in output

    def test_format_warning_result(self):
        """Test formatting a warning result."""
        result = QualityGateResult(
            gap_id="GAP-001",
            gap_name="test-skill",
            overall_status=GateStatus.WARN,
            gate_results=[
                GateResult("complexity", GateStatus.WARN, 0.4, "Simple pattern"),
            ],
            recommendation="WARNINGS: Simple pattern",
            can_generate=True,
        )
        output = format_gate_result(result)
        assert "WARN" in output

    def test_format_includes_score_bars(self):
        """Test that format includes visual score bars."""
        result = QualityGateResult(
            gap_id="GAP-001",
            gap_name="test-skill",
            overall_status=GateStatus.PASS,
            gate_results=[
                GateResult("novelty", GateStatus.PASS, 0.8, "Good novelty"),
            ],
            recommendation="Ready",
            can_generate=True,
        )
        output = format_gate_result(result)
        # Should include block characters for score bar
        assert "█" in output or "░" in output
