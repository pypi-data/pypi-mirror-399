"""Tests for estimation accuracy reporting."""
import json
from datetime import datetime
from pathlib import Path

import pytest

from bpsai_pair.metrics.accuracy import (
    AccuracyAnalyzer,
    AccuracyStats,
    TaskTypeAccuracy,
    ComplexityBandAccuracy,
)


@pytest.fixture
def tmp_history_dir(tmp_path):
    """Create a temporary history directory."""
    history_dir = tmp_path / ".paircoder" / "history"
    history_dir.mkdir(parents=True)
    return history_dir


@pytest.fixture
def sample_completions(tmp_history_dir):
    """Create sample task completion data for testing."""
    completions = [
        # Feature tasks - tend to underestimate
        {
            "task_id": "TASK-001",
            "estimated_hours": 4.0,
            "actual_hours": 5.0,  # 25% over
            "variance_hours": 1.0,
            "variance_percent": 25.0,
            "completed_at": "2025-12-01T10:00:00",
            "task_type": "feature",
            "complexity": 25,  # S band
        },
        {
            "task_id": "TASK-002",
            "estimated_hours": 8.0,
            "actual_hours": 10.0,  # 25% over
            "variance_hours": 2.0,
            "variance_percent": 25.0,
            "completed_at": "2025-12-02T10:00:00",
            "task_type": "feature",
            "complexity": 45,  # M band
        },
        # Bugfix tasks - tend to be accurate
        {
            "task_id": "TASK-003",
            "estimated_hours": 2.0,
            "actual_hours": 1.8,  # 10% under
            "variance_hours": -0.2,
            "variance_percent": -10.0,
            "completed_at": "2025-12-03T10:00:00",
            "task_type": "bugfix",
            "complexity": 15,  # XS band
        },
        {
            "task_id": "TASK-004",
            "estimated_hours": 4.0,
            "actual_hours": 4.2,  # 5% over
            "variance_hours": 0.2,
            "variance_percent": 5.0,
            "completed_at": "2025-12-04T10:00:00",
            "task_type": "bugfix",
            "complexity": 30,  # S band
        },
        # Refactor tasks - tend to significantly underestimate
        {
            "task_id": "TASK-005",
            "estimated_hours": 6.0,
            "actual_hours": 9.0,  # 50% over
            "variance_hours": 3.0,
            "variance_percent": 50.0,
            "completed_at": "2025-12-05T10:00:00",
            "task_type": "refactor",
            "complexity": 60,  # L band
        },
        # XL complexity task
        {
            "task_id": "TASK-006",
            "estimated_hours": 16.0,
            "actual_hours": 20.0,  # 25% over
            "variance_hours": 4.0,
            "variance_percent": 25.0,
            "completed_at": "2025-12-06T10:00:00",
            "task_type": "feature",
            "complexity": 85,  # XL band
        },
    ]

    # Write to task-completions.jsonl
    completions_file = tmp_history_dir / "task-completions.jsonl"
    with open(completions_file, "w") as f:
        for c in completions:
            f.write(json.dumps(c) + "\n")

    return completions


class TestAccuracyStats:
    """Tests for AccuracyStats dataclass."""

    def test_accuracy_stats_creation(self):
        """Test creating AccuracyStats."""
        stats = AccuracyStats(
            total_tasks=10,
            overall_accuracy=82.0,
            bias_direction="optimistic",
            bias_percent=18.0,
            avg_variance_percent=18.0,
        )
        assert stats.total_tasks == 10
        assert stats.overall_accuracy == 82.0
        assert stats.bias_direction == "optimistic"
        assert stats.bias_percent == 18.0

    def test_accuracy_stats_to_dict(self):
        """Test converting AccuracyStats to dict."""
        stats = AccuracyStats(
            total_tasks=10,
            overall_accuracy=82.0,
            bias_direction="optimistic",
            bias_percent=18.0,
            avg_variance_percent=18.0,
        )
        data = stats.to_dict()
        assert data["total_tasks"] == 10
        assert data["overall_accuracy"] == 82.0
        assert data["bias_direction"] == "optimistic"


class TestTaskTypeAccuracy:
    """Tests for TaskTypeAccuracy dataclass."""

    def test_task_type_accuracy_creation(self):
        """Test creating TaskTypeAccuracy."""
        accuracy = TaskTypeAccuracy(
            task_type="feature",
            count=5,
            accuracy_percent=75.0,
            bias_direction="underestimate",
            bias_percent=25.0,
        )
        assert accuracy.task_type == "feature"
        assert accuracy.count == 5
        assert accuracy.accuracy_percent == 75.0


class TestComplexityBandAccuracy:
    """Tests for ComplexityBandAccuracy dataclass."""

    def test_complexity_band_accuracy_creation(self):
        """Test creating ComplexityBandAccuracy."""
        accuracy = ComplexityBandAccuracy(
            band="S",
            complexity_range="16-30",
            count=3,
            accuracy_percent=85.0,
        )
        assert accuracy.band == "S"
        assert accuracy.count == 3


class TestAccuracyAnalyzer:
    """Tests for AccuracyAnalyzer."""

    def test_analyzer_creation(self, tmp_history_dir):
        """Test creating AccuracyAnalyzer."""
        analyzer = AccuracyAnalyzer(tmp_history_dir)
        assert analyzer.history_dir == tmp_history_dir

    def test_load_completions_empty(self, tmp_history_dir):
        """Test loading completions when file doesn't exist."""
        analyzer = AccuracyAnalyzer(tmp_history_dir)
        completions = analyzer.load_completions()
        assert completions == []

    def test_load_completions_with_data(self, tmp_history_dir, sample_completions):
        """Test loading completions with data."""
        analyzer = AccuracyAnalyzer(tmp_history_dir)
        completions = analyzer.load_completions()
        assert len(completions) == 6

    def test_calculate_overall_accuracy(self, tmp_history_dir, sample_completions):
        """Test calculating overall accuracy."""
        analyzer = AccuracyAnalyzer(tmp_history_dir)
        stats = analyzer.get_accuracy_stats()

        assert stats.total_tasks == 6
        # Average variance is (25 + 25 + 10 + 5 + 50 + 25) / 6 = 23.33%
        # Accuracy is 100 - 23.33 = 76.67%
        assert 70 <= stats.overall_accuracy <= 85
        assert stats.bias_direction == "optimistic"  # Most tasks took longer

    def test_get_accuracy_by_task_type(self, tmp_history_dir, sample_completions):
        """Test getting accuracy breakdown by task type."""
        analyzer = AccuracyAnalyzer(tmp_history_dir)
        by_type = analyzer.get_accuracy_by_task_type()

        assert len(by_type) == 3  # feature, bugfix, refactor

        # Find feature accuracy
        feature_acc = next(t for t in by_type if t.task_type == "feature")
        assert feature_acc.count == 3  # TASK-001, TASK-002, TASK-006
        assert feature_acc.bias_direction == "optimistic"  # Took longer = optimistic estimates

        # Find bugfix accuracy
        bugfix_acc = next(t for t in by_type if t.task_type == "bugfix")
        assert bugfix_acc.count == 2  # TASK-003, TASK-004
        # Bugfixes are more accurate (variance -10% and 5%)

        # Find refactor accuracy
        refactor_acc = next(t for t in by_type if t.task_type == "refactor")
        assert refactor_acc.count == 1
        assert refactor_acc.bias_percent == 50.0

    def test_get_accuracy_by_complexity_band(self, tmp_history_dir, sample_completions):
        """Test getting accuracy breakdown by complexity band."""
        analyzer = AccuracyAnalyzer(tmp_history_dir)
        by_band = analyzer.get_accuracy_by_complexity_band()

        # Should have XS, S, M, L, XL bands
        bands = {b.band for b in by_band}
        assert "XS" in bands or "S" in bands  # At least some bands present

    def test_get_recommendation_optimistic(self, tmp_history_dir, sample_completions):
        """Test getting recommendation for optimistic estimates."""
        analyzer = AccuracyAnalyzer(tmp_history_dir)
        recommendation = analyzer.get_recommendation()

        # Since most tasks took longer, recommendation should suggest adding buffer
        assert "buffer" in recommendation.lower() or "%" in recommendation

    def test_no_data_returns_defaults(self, tmp_history_dir):
        """Test that no data returns sensible defaults."""
        analyzer = AccuracyAnalyzer(tmp_history_dir)
        stats = analyzer.get_accuracy_stats()

        assert stats.total_tasks == 0
        assert stats.overall_accuracy == 100.0  # No data = perfect accuracy by default
        assert stats.bias_direction == "neutral"

    def test_generate_report(self, tmp_history_dir, sample_completions):
        """Test generating a full accuracy report."""
        analyzer = AccuracyAnalyzer(tmp_history_dir)
        report = analyzer.generate_report()

        assert "stats" in report
        assert "by_task_type" in report
        assert "by_complexity_band" in report
        assert "recommendation" in report

        assert report["stats"]["total_tasks"] == 6


class TestAccuracyCalculations:
    """Tests for accuracy calculation edge cases."""

    def test_perfect_estimation(self, tmp_history_dir):
        """Test 100% accuracy when estimates match actuals."""
        completions = [
            {
                "task_id": "TASK-001",
                "estimated_hours": 4.0,
                "actual_hours": 4.0,
                "variance_hours": 0.0,
                "variance_percent": 0.0,
                "completed_at": "2025-12-01T10:00:00",
                "task_type": "feature",
                "complexity": 25,
            }
        ]
        completions_file = tmp_history_dir / "task-completions.jsonl"
        with open(completions_file, "w") as f:
            for c in completions:
                f.write(json.dumps(c) + "\n")

        analyzer = AccuracyAnalyzer(tmp_history_dir)
        stats = analyzer.get_accuracy_stats()

        assert stats.overall_accuracy == 100.0
        assert stats.bias_direction == "neutral"

    def test_overestimate_bias(self, tmp_history_dir):
        """Test when we consistently overestimate (tasks finish faster)."""
        completions = [
            {
                "task_id": "TASK-001",
                "estimated_hours": 8.0,
                "actual_hours": 4.0,  # 50% under
                "variance_hours": -4.0,
                "variance_percent": -50.0,
                "completed_at": "2025-12-01T10:00:00",
                "task_type": "feature",
                "complexity": 25,
            }
        ]
        completions_file = tmp_history_dir / "task-completions.jsonl"
        with open(completions_file, "w") as f:
            for c in completions:
                f.write(json.dumps(c) + "\n")

        analyzer = AccuracyAnalyzer(tmp_history_dir)
        stats = analyzer.get_accuracy_stats()

        assert stats.bias_direction == "pessimistic"  # Overestimate = pessimistic

    def test_complexity_band_mapping(self, tmp_history_dir):
        """Test that complexity values map to correct bands."""
        analyzer = AccuracyAnalyzer(tmp_history_dir)

        assert analyzer._get_complexity_band(10) == "XS"  # 0-15
        assert analyzer._get_complexity_band(20) == "S"  # 16-30
        assert analyzer._get_complexity_band(40) == "M"  # 31-50
        assert analyzer._get_complexity_band(60) == "L"  # 51-75
        assert analyzer._get_complexity_band(90) == "XL"  # 76-100
