"""Tests for estimation module."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from bpsai_pair.metrics.estimation import (
    EstimationService,
    EstimationConfig,
    HoursEstimate,
    estimate_hours,
    DEFAULT_COMPLEXITY_TO_HOURS,
)
from bpsai_pair.planning.models import Task, TaskStatus


class TestHoursEstimate:
    """Tests for HoursEstimate dataclass."""

    def test_str_representation(self):
        """Test string representation."""
        estimate = HoursEstimate(
            min_hours=1.0,
            expected_hours=2.0,
            max_hours=4.0,
            complexity=25,
            size_band="s",
        )
        assert str(estimate) == "2.0h (S)"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        estimate = HoursEstimate(
            min_hours=0.5,
            expected_hours=1.0,
            max_hours=2.0,
            complexity=10,
            size_band="xs",
        )
        result = estimate.to_dict()
        assert result["min_hours"] == 0.5
        assert result["expected_hours"] == 1.0
        assert result["max_hours"] == 2.0
        assert result["complexity"] == 10
        assert result["size_band"] == "xs"


class TestEstimationConfig:
    """Tests for EstimationConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = EstimationConfig()
        assert "xs" in config.complexity_to_hours
        assert "s" in config.complexity_to_hours
        assert "m" in config.complexity_to_hours
        assert "l" in config.complexity_to_hours
        assert "xl" in config.complexity_to_hours

    def test_from_dict_empty(self):
        """Test from_dict with empty data."""
        config = EstimationConfig.from_dict({})
        assert config.complexity_to_hours == DEFAULT_COMPLEXITY_TO_HOURS

    def test_from_dict_with_overrides(self):
        """Test from_dict with custom values."""
        data = {
            "complexity_to_hours": {
                "xs": {"range": [0, 10], "hours": [0.25, 0.5, 1.0]},
            }
        }
        config = EstimationConfig.from_dict(data)
        # List or tuple are both acceptable
        hours = config.complexity_to_hours["xs"]["hours"]
        assert list(hours) == [0.25, 0.5, 1.0]

    def test_from_dict_simplified_format(self):
        """Test from_dict with simplified list format."""
        data = {
            "complexity_to_hours": {
                "s": [2.0, 3.0, 5.0],
            }
        }
        config = EstimationConfig.from_dict(data)
        assert config.complexity_to_hours["s"]["hours"] == (2.0, 3.0, 5.0)


class TestEstimationService:
    """Tests for EstimationService."""

    def test_default_service(self):
        """Test service with default config."""
        service = EstimationService()
        assert service.config is not None

    def test_get_size_band_xs(self):
        """Test XS band detection."""
        service = EstimationService()
        assert service.get_size_band(0) == "xs"
        assert service.get_size_band(10) == "xs"
        assert service.get_size_band(15) == "xs"

    def test_get_size_band_s(self):
        """Test S band detection."""
        service = EstimationService()
        assert service.get_size_band(16) == "s"
        assert service.get_size_band(25) == "s"
        assert service.get_size_band(30) == "s"

    def test_get_size_band_m(self):
        """Test M band detection."""
        service = EstimationService()
        assert service.get_size_band(31) == "m"
        assert service.get_size_band(40) == "m"
        assert service.get_size_band(50) == "m"

    def test_get_size_band_l(self):
        """Test L band detection."""
        service = EstimationService()
        assert service.get_size_band(51) == "l"
        assert service.get_size_band(65) == "l"
        assert service.get_size_band(75) == "l"

    def test_get_size_band_xl(self):
        """Test XL band detection."""
        service = EstimationService()
        assert service.get_size_band(76) == "xl"
        assert service.get_size_band(90) == "xl"
        assert service.get_size_band(100) == "xl"

    def test_get_size_band_clamping(self):
        """Test complexity clamping to valid range."""
        service = EstimationService()
        assert service.get_size_band(-10) == "xs"
        assert service.get_size_band(150) == "xl"

    def test_estimate_hours_xs(self):
        """Test XS estimate returns valid hours."""
        service = EstimationService()
        estimate = service.estimate_hours(10)
        assert estimate.size_band == "xs"
        assert estimate.min_hours > 0
        assert estimate.min_hours <= estimate.expected_hours
        assert estimate.expected_hours <= estimate.max_hours

    def test_estimate_hours_s(self):
        """Test S estimate returns valid hours."""
        service = EstimationService()
        estimate = service.estimate_hours(25)
        assert estimate.size_band == "s"
        assert estimate.min_hours > 0
        assert estimate.min_hours <= estimate.expected_hours
        assert estimate.expected_hours <= estimate.max_hours

    def test_estimate_hours_m(self):
        """Test M estimate."""
        service = EstimationService()
        estimate = service.estimate_hours(40)
        assert estimate.size_band == "m"
        assert estimate.min_hours == 2.0
        assert estimate.expected_hours == 4.0
        assert estimate.max_hours == 8.0

    def test_estimate_hours_l(self):
        """Test L estimate."""
        service = EstimationService()
        estimate = service.estimate_hours(60)
        assert estimate.size_band == "l"
        assert estimate.min_hours == 4.0
        assert estimate.expected_hours == 8.0
        assert estimate.max_hours == 16.0

    def test_estimate_hours_xl(self):
        """Test XL estimate."""
        service = EstimationService()
        estimate = service.estimate_hours(85)
        assert estimate.size_band == "xl"
        assert estimate.min_hours == 8.0
        assert estimate.expected_hours == 16.0
        assert estimate.max_hours == 32.0

    def test_estimate_hours_for_tasks(self):
        """Test estimating hours for multiple tasks."""
        service = EstimationService()
        tasks = [
            Task(id="TASK-1", title="Small", plan_id="plan-1", complexity=20),
            Task(id="TASK-2", title="Medium", plan_id="plan-1", complexity=40),
            Task(id="TASK-3", title="Large", plan_id="plan-1", complexity=70),
        ]
        estimates = service.estimate_hours_for_tasks(tasks)

        assert "TASK-1" in estimates
        assert "TASK-2" in estimates
        assert "TASK-3" in estimates
        assert estimates["TASK-1"].size_band == "s"
        assert estimates["TASK-2"].size_band == "m"
        assert estimates["TASK-3"].size_band == "l"

    def test_get_total_hours(self):
        """Test total hours calculation."""
        service = EstimationService()
        tasks = [
            Task(id="TASK-1", title="Small", plan_id="plan-1", complexity=20),
            Task(id="TASK-2", title="Medium", plan_id="plan-1", complexity=40),
        ]
        min_total, expected_total, max_total = service.get_total_hours(tasks)

        # Verify order: min <= expected <= max
        assert min_total > 0
        assert min_total <= expected_total
        assert expected_total <= max_total
        # Verify totals are sum of individual estimates
        estimates = service.estimate_hours_for_tasks(tasks)
        assert min_total == sum(e.min_hours for e in estimates.values())
        assert expected_total == sum(e.expected_hours for e in estimates.values())

    def test_format_estimate(self):
        """Test estimate formatting."""
        service = EstimationService()
        estimate = HoursEstimate(
            min_hours=1.0,
            expected_hours=2.0,
            max_hours=4.0,
            complexity=25,
            size_band="s",
        )
        formatted = service.format_estimate(estimate)
        assert formatted == "2.0h (S) [1.0h - 4.0h]"

    def test_from_config_file(self):
        """Test loading from config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_data = {
                "estimation": {
                    "complexity_to_hours": {
                        "xs": {"range": [0, 20], "hours": [0.25, 0.5, 1.0]},
                    }
                }
            }
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            service = EstimationService.from_config_file(config_path)
            estimate = service.estimate_hours(15)
            assert estimate.expected_hours == 0.5

    def test_from_config_file_missing(self):
        """Test loading from missing config file."""
        service = EstimationService.from_config_file(Path("/nonexistent/path"))
        # Should use defaults
        assert service.config is not None


class TestEstimateHoursFunction:
    """Tests for the estimate_hours convenience function."""

    def test_basic_usage(self):
        """Test basic function usage."""
        estimate = estimate_hours(30)
        assert estimate.size_band == "s"
        # Verify valid estimate structure
        assert estimate.min_hours > 0
        assert estimate.min_hours <= estimate.expected_hours
        assert estimate.expected_hours <= estimate.max_hours

    def test_with_config_file(self):
        """Test with config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_data = {
                "estimation": {
                    "complexity_to_hours": {
                        "s": {"range": [16, 30], "hours": [2.0, 3.0, 6.0]},
                    }
                }
            }
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            estimate = estimate_hours(25, config_path)
            assert estimate.expected_hours == 3.0


class TestTaskEstimatedHours:
    """Tests for Task.estimated_hours property."""

    def test_estimated_hours_property(self):
        """Test that Task has estimated_hours property."""
        task = Task(
            id="TASK-1",
            title="Test Task",
            plan_id="plan-1",
            complexity=25,
        )
        estimate = task.estimated_hours
        assert estimate.size_band == "s"
        # Just verify it returns an estimate with the right band
        assert estimate.expected_hours > 0

    def test_actual_hours_without_tracking(self):
        """Test actual_hours returns None when no time tracking."""
        task = Task(
            id="TASK-1",
            title="Test Task",
            plan_id="plan-1",
            complexity=25,
        )
        # Without a paircoder_dir, actual_hours should be None
        assert task.actual_hours is None

    def test_actual_hours_with_tracking(self):
        """Test actual_hours computed from time tracking entries."""
        from bpsai_pair.integrations.time_tracking import LocalTimeCache, TimerEntry
        from datetime import timedelta

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "time-cache.json"
            cache = LocalTimeCache(cache_path)

            # Add a time entry for the task
            entry = TimerEntry(
                id="timer-1",
                task_id="TASK-1",
                description="Working on task",
                start=datetime.now() - timedelta(hours=2),
                end=datetime.now(),
                duration=timedelta(hours=2),
            )
            cache.add_entry("TASK-1", entry)

            task = Task(
                id="TASK-1",
                title="Test Task",
                plan_id="plan-1",
                complexity=25,
            )

            # Get actual hours using the cache
            actual = task.get_actual_hours(Path(tmpdir))
            assert actual is not None
            assert actual == pytest.approx(2.0, rel=0.01)

    def test_estimated_hours_str_property(self):
        """Test estimated_hours_str property."""
        task = Task(
            id="TASK-1",
            title="Test Task",
            plan_id="plan-1",
            complexity=25,
        )
        # Format should be like "X.Xh (S)"
        assert "h (S)" in task.estimated_hours_str

    def test_different_complexities(self):
        """Test different complexity values."""
        xs_task = Task(id="T1", title="XS", plan_id="p", complexity=10)
        xl_task = Task(id="T2", title="XL", plan_id="p", complexity=90)

        assert xs_task.estimated_hours.size_band == "xs"
        assert xl_task.estimated_hours.size_band == "xl"
        assert xs_task.estimated_hours.expected_hours < xl_task.estimated_hours.expected_hours


class TestTaskComparison:
    """Tests for TaskComparison dataclass."""

    def test_comparison_creation(self):
        """Test creating a task comparison."""
        from bpsai_pair.metrics.estimation import TaskComparison

        comparison = TaskComparison(
            task_id="TASK-100",
            estimated_hours=4.0,
            actual_hours=3.5,
        )

        assert comparison.task_id == "TASK-100"
        assert comparison.estimated_hours == 4.0
        assert comparison.actual_hours == 3.5
        assert comparison.variance_hours == -0.5
        assert comparison.variance_percent == pytest.approx(-12.5)

    def test_comparison_over_estimate(self):
        """Test variance when actual exceeds estimate."""
        from bpsai_pair.metrics.estimation import TaskComparison

        comparison = TaskComparison(
            task_id="TASK-101",
            estimated_hours=2.0,
            actual_hours=3.0,
        )

        assert comparison.variance_hours == 1.0  # Over by 1 hour
        assert comparison.variance_percent == pytest.approx(50.0)

    def test_comparison_zero_estimate(self):
        """Test variance when estimate is zero."""
        from bpsai_pair.metrics.estimation import TaskComparison

        comparison = TaskComparison(
            task_id="TASK-102",
            estimated_hours=0.0,
            actual_hours=2.0,
        )

        assert comparison.variance_hours == 2.0
        assert comparison.variance_percent == 0.0  # Avoid division by zero

    def test_comparison_to_dict(self):
        """Test converting comparison to dictionary."""
        from bpsai_pair.metrics.estimation import TaskComparison
        from datetime import datetime

        completed_at = datetime(2025, 12, 18, 13, 30, 0)
        comparison = TaskComparison(
            task_id="TASK-103",
            estimated_hours=4.0,
            actual_hours=3.5,
            completed_at=completed_at,
        )

        d = comparison.to_dict()
        assert d["task_id"] == "TASK-103"
        assert d["estimated_hours"] == 4.0
        assert d["actual_hours"] == 3.5
        assert d["variance_hours"] == -0.5
        assert d["variance_percent"] == pytest.approx(-12.5)
        assert d["completed_at"] == "2025-12-18T13:30:00"

    def test_comparison_from_task(self):
        """Test creating comparison from task and actual hours."""
        from bpsai_pair.metrics.estimation import TaskComparison

        task = Task(
            id="TASK-104",
            title="Test Task",
            plan_id="plan-1",
            complexity=40,  # M size = 4h expected
        )

        comparison = TaskComparison.from_task(task, actual_hours=3.5)

        assert comparison.task_id == "TASK-104"
        assert comparison.estimated_hours == 4.0  # M complexity = 4h
        assert comparison.actual_hours == 3.5
        assert comparison.variance_hours == -0.5


class TestEstimationServiceComparison:
    """Tests for estimation service comparison methods."""

    def test_create_comparison(self):
        """Test creating a comparison through the service."""
        from bpsai_pair.metrics.estimation import EstimationService, TaskComparison

        service = EstimationService()
        task = Task(
            id="TASK-200",
            title="Medium Task",
            plan_id="plan-1",
            complexity=40,
        )

        comparison = service.create_comparison(task, actual_hours=5.0)

        assert isinstance(comparison, TaskComparison)
        assert comparison.task_id == "TASK-200"
        assert comparison.estimated_hours == 4.0
        assert comparison.actual_hours == 5.0
        assert comparison.variance_hours == 1.0

    def test_format_comparison(self):
        """Test formatting a comparison for display."""
        from bpsai_pair.metrics.estimation import EstimationService, TaskComparison

        service = EstimationService()
        comparison = TaskComparison(
            task_id="TASK-201",
            estimated_hours=4.0,
            actual_hours=3.5,
        )

        formatted = service.format_comparison(comparison)
        assert "Est: 4.0h" in formatted
        assert "Act: 3.5h" in formatted
        assert "-12.5%" in formatted or "12.5%" in formatted

    def test_format_comparison_over_time(self):
        """Test formatting when over time."""
        from bpsai_pair.metrics.estimation import EstimationService, TaskComparison

        service = EstimationService()
        comparison = TaskComparison(
            task_id="TASK-202",
            estimated_hours=2.0,
            actual_hours=4.0,
        )

        formatted = service.format_comparison(comparison)
        assert "+100.0%" in formatted or "100.0%" in formatted


class TestMetricsCollectorTaskCompletion:
    """Tests for MetricsCollector task completion recording."""

    def test_record_task_completion(self):
        """Test recording a task completion."""
        from bpsai_pair.metrics import MetricsCollector

        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            data = collector.record_task_completion(
                task_id="TASK-300",
                estimated_hours=4.0,
                actual_hours=3.5,
            )

            assert data["task_id"] == "TASK-300"
            assert data["estimated_hours"] == 4.0
            assert data["actual_hours"] == 3.5
            assert data["variance_hours"] == -0.5
            assert data["variance_percent"] == pytest.approx(-12.5)
            assert "completed_at" in data

    def test_load_task_completions(self):
        """Test loading task completions."""
        from bpsai_pair.metrics import MetricsCollector

        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            # Record multiple completions
            collector.record_task_completion("TASK-301", 2.0, 1.5)
            collector.record_task_completion("TASK-302", 4.0, 5.0)
            collector.record_task_completion("TASK-303", 8.0, 8.0)

            completions = collector.load_task_completions()
            assert len(completions) == 3

            # Filter by task ID
            task_completions = collector.load_task_completions("TASK-302")
            assert len(task_completions) == 1
            assert task_completions[0]["task_id"] == "TASK-302"

    def test_get_estimation_accuracy(self):
        """Test getting estimation accuracy statistics."""
        from bpsai_pair.metrics import MetricsCollector

        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            # Record various completions
            collector.record_task_completion("T1", 2.0, 1.5)  # Over-estimated (25% early)
            collector.record_task_completion("T2", 4.0, 5.0)  # Under-estimated (25% over)
            collector.record_task_completion("T3", 8.0, 8.5)  # Accurate (6.25% over)

            stats = collector.get_estimation_accuracy()

            assert stats["total_tasks"] == 3
            assert stats["over_estimates"] == 1  # T1 - finished early
            assert stats["under_estimates"] == 1  # T2 - took longer
            assert stats["accurate"] == 1  # T3 - within 10%

    def test_get_estimation_accuracy_empty(self):
        """Test accuracy stats with no completions."""
        from bpsai_pair.metrics import MetricsCollector

        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            stats = collector.get_estimation_accuracy()

            assert stats["total_tasks"] == 0
            assert stats["avg_variance_percent"] == 0.0


# ============================================================================
# Token Estimation Tests
# ============================================================================


class TestTokenEstimate:
    """Tests for TokenEstimate dataclass."""

    def test_token_estimate_creation(self):
        """Test creating a TokenEstimate."""
        from bpsai_pair.metrics.estimation import TokenEstimate

        estimate = TokenEstimate(
            base_tokens=15000,
            complexity_tokens=12500,
            type_multiplier=1.2,
            file_tokens=4000,
            total_tokens=33000,
            task_type="feature",
        )
        assert estimate.base_tokens == 15000
        assert estimate.complexity_tokens == 12500
        assert estimate.type_multiplier == 1.2
        assert estimate.file_tokens == 4000
        assert estimate.total_tokens == 33000
        assert estimate.task_type == "feature"

    def test_token_estimate_to_dict(self):
        """Test converting TokenEstimate to dict."""
        from bpsai_pair.metrics.estimation import TokenEstimate

        estimate = TokenEstimate(
            base_tokens=15000,
            complexity_tokens=12500,
            type_multiplier=1.0,
            file_tokens=4000,
            total_tokens=31500,
            task_type="bugfix",
        )
        d = estimate.to_dict()
        assert d["base_tokens"] == 15000
        assert d["complexity_tokens"] == 12500
        assert d["total_tokens"] == 31500
        assert d["task_type"] == "bugfix"

    def test_token_estimate_str(self):
        """Test string representation of TokenEstimate."""
        from bpsai_pair.metrics.estimation import TokenEstimate

        estimate = TokenEstimate(
            base_tokens=15000,
            complexity_tokens=12500,
            type_multiplier=1.0,
            file_tokens=4000,
            total_tokens=31500,
            task_type="bugfix",
        )
        s = str(estimate)
        assert "31K" in s or "31500" in s  # Format: ~31K tokens


class TestTokenEstimationConfig:
    """Tests for TokenEstimationConfig."""

    def test_default_config(self):
        """Test default token estimation config."""
        from bpsai_pair.metrics.estimation import TokenEstimationConfig

        config = TokenEstimationConfig()
        assert config.base_context > 0
        assert config.per_complexity_point > 0
        assert "feature" in config.by_task_type
        assert "bugfix" in config.by_task_type
        assert config.per_file_touched > 0

    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        from bpsai_pair.metrics.estimation import TokenEstimationConfig

        data = {
            "base_context": 20000,
            "per_complexity_point": 600,
            "by_task_type": {
                "feature": 1.5,
                "bugfix": 0.7,
            },
            "per_file_touched": 2500,
        }
        config = TokenEstimationConfig.from_dict(data)
        assert config.base_context == 20000
        assert config.per_complexity_point == 600
        assert config.by_task_type["feature"] == 1.5
        assert config.per_file_touched == 2500

    def test_config_from_dict_partial(self):
        """Test config from partial dictionary uses defaults for missing."""
        from bpsai_pair.metrics.estimation import TokenEstimationConfig

        data = {"base_context": 10000}
        config = TokenEstimationConfig.from_dict(data)
        assert config.base_context == 10000
        # Other values should be defaults
        assert config.per_complexity_point > 0
        assert "feature" in config.by_task_type


class TestTokenEstimator:
    """Tests for TokenEstimator."""

    def test_estimator_creation(self):
        """Test creating a TokenEstimator."""
        from bpsai_pair.metrics.estimation import TokenEstimator

        estimator = TokenEstimator()
        assert estimator.config is not None

    def test_estimate_tokens_basic(self):
        """Test basic token estimation."""
        from bpsai_pair.metrics.estimation import TokenEstimator

        estimator = TokenEstimator()
        estimate = estimator.estimate_tokens(
            complexity=50,
            task_type="feature",
            file_count=2,
        )

        assert estimate.total_tokens > 0
        assert estimate.base_tokens > 0
        assert estimate.complexity_tokens > 0
        assert estimate.file_tokens > 0

    def test_estimate_tokens_formula(self):
        """Test token estimation formula is correct."""
        from bpsai_pair.metrics.estimation import TokenEstimator, TokenEstimationConfig

        config = TokenEstimationConfig(
            base_context=15000,
            per_complexity_point=500,
            by_task_type={"feature": 1.2, "bugfix": 0.8},
            per_file_touched=2000,
        )
        estimator = TokenEstimator(config)

        # Formula: tokens = base + (complexity * per_point) * multiplier + (files * per_file)
        # 50 complexity, feature (1.2x), 2 files
        # = 15000 + (50 * 500) * 1.2 + (2 * 2000)
        # = 15000 + 30000 + 4000 = 49000
        estimate = estimator.estimate_tokens(
            complexity=50,
            task_type="feature",
            file_count=2,
        )

        assert estimate.base_tokens == 15000
        assert estimate.complexity_tokens == 30000  # 50 * 500 * 1.2
        assert estimate.file_tokens == 4000  # 2 * 2000
        assert estimate.total_tokens == 49000

    def test_different_task_types(self):
        """Test different task types produce different estimates."""
        from bpsai_pair.metrics.estimation import TokenEstimator

        estimator = TokenEstimator()

        feature_est = estimator.estimate_tokens(50, "feature", 2)
        bugfix_est = estimator.estimate_tokens(50, "bugfix", 2)
        refactor_est = estimator.estimate_tokens(50, "refactor", 2)
        docs_est = estimator.estimate_tokens(50, "docs", 2)

        # Feature and refactor should be higher than bugfix
        assert feature_est.total_tokens > bugfix_est.total_tokens
        assert refactor_est.total_tokens > bugfix_est.total_tokens
        # Docs should be lowest
        assert docs_est.total_tokens < bugfix_est.total_tokens

    def test_unknown_task_type_defaults_to_1(self):
        """Test unknown task type uses multiplier of 1.0."""
        from bpsai_pair.metrics.estimation import TokenEstimator, TokenEstimationConfig

        config = TokenEstimationConfig(
            base_context=10000,
            per_complexity_point=100,
            by_task_type={"feature": 1.5},
            per_file_touched=1000,
        )
        estimator = TokenEstimator(config)

        estimate = estimator.estimate_tokens(50, "unknown_type", 1)

        # Should use multiplier of 1.0
        # 10000 + (50 * 100) * 1.0 + (1 * 1000) = 16000
        assert estimate.type_multiplier == 1.0
        assert estimate.total_tokens == 16000

    def test_zero_files(self):
        """Test estimation with zero files."""
        from bpsai_pair.metrics.estimation import TokenEstimator

        estimator = TokenEstimator()
        estimate = estimator.estimate_tokens(50, "feature", 0)

        assert estimate.file_tokens == 0
        assert estimate.total_tokens > 0  # Still has base + complexity

    def test_high_complexity(self):
        """Test high complexity produces high token estimate."""
        from bpsai_pair.metrics.estimation import TokenEstimator

        estimator = TokenEstimator()

        low = estimator.estimate_tokens(10, "feature", 1)
        high = estimator.estimate_tokens(100, "feature", 1)

        assert high.total_tokens > low.total_tokens
        assert high.complexity_tokens > low.complexity_tokens

    def test_file_count_impact(self):
        """Test more files increases token estimate."""
        from bpsai_pair.metrics.estimation import TokenEstimator

        estimator = TokenEstimator()

        few_files = estimator.estimate_tokens(50, "feature", 1)
        many_files = estimator.estimate_tokens(50, "feature", 10)

        assert many_files.total_tokens > few_files.total_tokens
        assert many_files.file_tokens > few_files.file_tokens

    def test_estimate_from_task(self):
        """Test estimating tokens from a Task object."""
        from bpsai_pair.metrics.estimation import TokenEstimator

        task = Task(
            id="TASK-1",
            title="Test",
            plan_id="plan-1",
            type="feature",
            complexity=40,
            files_touched=["file1.py", "file2.py", "file3.py"],
        )

        estimator = TokenEstimator()
        estimate = estimator.estimate_for_task(task)

        assert estimate.task_type == "feature"
        assert estimate.total_tokens > 0
        # Should account for 3 files
        assert estimate.file_tokens == estimator.config.per_file_touched * 3


class TestTaskEstimatedTokens:
    """Tests for Task.estimated_tokens property."""

    def test_estimated_tokens_property(self):
        """Test that Task has estimated_tokens property."""
        task = Task(
            id="TASK-1",
            title="Test Task",
            plan_id="plan-1",
            type="feature",
            complexity=50,
        )
        estimate = task.estimated_tokens
        assert estimate is not None
        assert estimate.total_tokens > 0

    def test_estimated_tokens_str_property(self):
        """Test estimated_tokens_str property."""
        task = Task(
            id="TASK-1",
            title="Test Task",
            plan_id="plan-1",
            type="feature",
            complexity=50,
        )
        s = task.estimated_tokens_str
        # Should be formatted like "~45K tokens"
        assert "tokens" in s.lower() or "k" in s.lower()

    def test_estimated_tokens_varies_by_type(self):
        """Test that different task types get different estimates."""
        feature_task = Task(
            id="T1", title="Feature", plan_id="p", type="feature", complexity=50
        )
        bugfix_task = Task(
            id="T2", title="Bugfix", plan_id="p", type="bugfix", complexity=50
        )

        assert feature_task.estimated_tokens.total_tokens > bugfix_task.estimated_tokens.total_tokens

    def test_estimated_tokens_varies_by_files(self):
        """Test that file count affects token estimate."""
        no_files = Task(
            id="T1", title="No files", plan_id="p", complexity=50, files_touched=[]
        )
        with_files = Task(
            id="T2",
            title="With files",
            plan_id="p",
            complexity=50,
            files_touched=["a.py", "b.py", "c.py", "d.py", "e.py"],
        )

        assert with_files.estimated_tokens.total_tokens > no_files.estimated_tokens.total_tokens


# ============================================================================
# Token Feedback Loop Tests
# ============================================================================


class TestTokenComparison:
    """Tests for TokenComparison dataclass."""

    def test_token_comparison_creation(self):
        """Test creating a TokenComparison."""
        from bpsai_pair.metrics.estimation import TokenComparison

        comparison = TokenComparison(
            task_id="TASK-100",
            estimated_tokens=45000,
            actual_tokens=50000,
            task_type="feature",
            complexity=50,
        )
        assert comparison.task_id == "TASK-100"
        assert comparison.estimated_tokens == 45000
        assert comparison.actual_tokens == 50000
        assert comparison.ratio == pytest.approx(50000 / 45000)

    def test_token_comparison_ratio_calculation(self):
        """Test ratio calculation (actual/estimated)."""
        from bpsai_pair.metrics.estimation import TokenComparison

        comparison = TokenComparison(
            task_id="TASK-101",
            estimated_tokens=40000,
            actual_tokens=50000,  # 25% more than estimated
            task_type="feature",
            complexity=50,
        )
        assert comparison.ratio == pytest.approx(1.25)

    def test_token_comparison_zero_estimated(self):
        """Test ratio when estimated is zero."""
        from bpsai_pair.metrics.estimation import TokenComparison

        comparison = TokenComparison(
            task_id="TASK-102",
            estimated_tokens=0,
            actual_tokens=50000,
            task_type="feature",
            complexity=50,
        )
        assert comparison.ratio == 1.0  # Default to 1.0

    def test_token_comparison_to_dict(self):
        """Test converting TokenComparison to dict."""
        from bpsai_pair.metrics.estimation import TokenComparison
        from datetime import datetime

        completed_at = datetime(2025, 12, 18, 15, 0, 0)
        comparison = TokenComparison(
            task_id="TASK-103",
            estimated_tokens=45000,
            actual_tokens=42000,
            task_type="bugfix",
            complexity=30,
            completed_at=completed_at,
        )
        d = comparison.to_dict()
        assert d["task_id"] == "TASK-103"
        assert d["estimated_tokens"] == 45000
        assert d["actual_tokens"] == 42000
        assert d["ratio"] == pytest.approx(42000 / 45000)
        assert d["task_type"] == "bugfix"


class TestTokenFeedbackTracker:
    """Tests for TokenFeedbackTracker."""

    def test_tracker_creation(self, tmp_path):
        """Test creating a TokenFeedbackTracker."""
        from bpsai_pair.metrics.estimation import TokenFeedbackTracker

        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)
        tracker = TokenFeedbackTracker(history_dir)
        assert tracker.history_dir == history_dir

    def test_record_token_usage(self, tmp_path):
        """Test recording token usage comparison."""
        from bpsai_pair.metrics.estimation import TokenFeedbackTracker

        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)
        tracker = TokenFeedbackTracker(history_dir)

        tracker.record_usage(
            task_id="TASK-100",
            estimated_tokens=45000,
            actual_tokens=50000,
            task_type="feature",
            complexity=50,
        )

        # Verify it was recorded
        comparisons = tracker.load_comparisons()
        assert len(comparisons) == 1
        assert comparisons[0]["task_id"] == "TASK-100"
        assert comparisons[0]["estimated_tokens"] == 45000
        assert comparisons[0]["actual_tokens"] == 50000

    def test_load_comparisons_empty(self, tmp_path):
        """Test loading comparisons when none exist."""
        from bpsai_pair.metrics.estimation import TokenFeedbackTracker

        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)
        tracker = TokenFeedbackTracker(history_dir)

        comparisons = tracker.load_comparisons()
        assert comparisons == []

    def test_get_accuracy_stats(self, tmp_path):
        """Test getting token accuracy statistics."""
        from bpsai_pair.metrics.estimation import TokenFeedbackTracker

        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)
        tracker = TokenFeedbackTracker(history_dir)

        # Record multiple usages
        tracker.record_usage("T1", 40000, 45000, "feature", 50)  # 1.125x
        tracker.record_usage("T2", 30000, 27000, "bugfix", 30)   # 0.9x
        tracker.record_usage("T3", 50000, 55000, "feature", 60)  # 1.1x

        stats = tracker.get_accuracy_stats()
        assert stats["total_tasks"] == 3
        assert "avg_ratio" in stats
        assert "by_task_type" in stats

    def test_get_accuracy_by_task_type(self, tmp_path):
        """Test accuracy breakdown by task type."""
        from bpsai_pair.metrics.estimation import TokenFeedbackTracker

        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)
        tracker = TokenFeedbackTracker(history_dir)

        # Feature tasks tend to use more tokens
        tracker.record_usage("T1", 40000, 48000, "feature", 50)  # 1.2x
        tracker.record_usage("T2", 45000, 54000, "feature", 55)  # 1.2x
        # Bugfix tasks are more accurate
        tracker.record_usage("T3", 30000, 28500, "bugfix", 30)   # 0.95x
        tracker.record_usage("T4", 25000, 26250, "bugfix", 25)   # 1.05x

        stats = tracker.get_accuracy_stats()
        by_type = stats["by_task_type"]

        assert "feature" in by_type
        assert "bugfix" in by_type
        assert by_type["feature"]["avg_ratio"] > by_type["bugfix"]["avg_ratio"]

    def test_get_recommended_adjustments(self, tmp_path):
        """Test getting recommended coefficient adjustments."""
        from bpsai_pair.metrics.estimation import TokenFeedbackTracker

        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)
        tracker = TokenFeedbackTracker(history_dir)

        # Consistently underestimate features
        tracker.record_usage("T1", 40000, 52000, "feature", 50)  # 1.3x
        tracker.record_usage("T2", 45000, 58500, "feature", 55)  # 1.3x
        tracker.record_usage("T3", 35000, 45500, "feature", 45)  # 1.3x

        adjustments = tracker.get_recommended_adjustments()

        # Should recommend increasing feature multiplier
        assert "feature" in adjustments
        assert adjustments["feature"] > 1.0  # Increase multiplier

    def test_apply_learning(self, tmp_path):
        """Test applying learning to adjust coefficients."""
        from bpsai_pair.metrics.estimation import (
            TokenFeedbackTracker,
            TokenEstimationConfig,
        )

        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)
        tracker = TokenFeedbackTracker(history_dir)

        # Consistently underestimate refactors
        tracker.record_usage("T1", 50000, 75000, "refactor", 50)  # 1.5x
        tracker.record_usage("T2", 55000, 82500, "refactor", 55)  # 1.5x
        tracker.record_usage("T3", 45000, 67500, "refactor", 45)  # 1.5x

        # Get current config
        old_config = TokenEstimationConfig()
        old_refactor_mult = old_config.by_task_type["refactor"]

        # Apply learning
        new_config = tracker.apply_learning(old_config)

        # Refactor multiplier should have increased
        assert new_config.by_task_type["refactor"] > old_refactor_mult

    def test_learning_clamps_to_bounds(self, tmp_path):
        """Test that learning clamps multipliers to reasonable bounds."""
        from bpsai_pair.metrics.estimation import (
            TokenFeedbackTracker,
            TokenEstimationConfig,
        )

        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)
        tracker = TokenFeedbackTracker(history_dir)

        # Extreme underestimation
        tracker.record_usage("T1", 10000, 100000, "feature", 50)  # 10x
        tracker.record_usage("T2", 10000, 100000, "feature", 50)  # 10x

        old_config = TokenEstimationConfig()
        new_config = tracker.apply_learning(old_config)

        # Should be clamped to max reasonable value (e.g., 3.0x)
        assert new_config.by_task_type["feature"] <= 3.0

    def test_minimum_samples_for_learning(self, tmp_path):
        """Test that learning requires minimum samples."""
        from bpsai_pair.metrics.estimation import (
            TokenFeedbackTracker,
            TokenEstimationConfig,
        )

        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)
        tracker = TokenFeedbackTracker(history_dir)

        # Only 1 sample - not enough for learning
        tracker.record_usage("T1", 40000, 60000, "feature", 50)

        old_config = TokenEstimationConfig()
        new_config = tracker.apply_learning(old_config, min_samples=3)

        # Should not change (not enough samples)
        assert new_config.by_task_type["feature"] == old_config.by_task_type["feature"]


class TestTokenAccuracyReport:
    """Tests for token accuracy reporting."""

    def test_generate_token_report(self, tmp_path):
        """Test generating a token accuracy report."""
        from bpsai_pair.metrics.estimation import TokenFeedbackTracker

        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)
        tracker = TokenFeedbackTracker(history_dir)

        # Add some data
        tracker.record_usage("T1", 40000, 44000, "feature", 50)
        tracker.record_usage("T2", 30000, 28000, "bugfix", 30)
        tracker.record_usage("T3", 60000, 90000, "refactor", 70)

        report = tracker.generate_report()

        assert "stats" in report
        assert "by_task_type" in report
        assert "recommendations" in report
        assert report["stats"]["total_tasks"] == 3

    def test_empty_report(self, tmp_path):
        """Test report with no data."""
        from bpsai_pair.metrics.estimation import TokenFeedbackTracker

        history_dir = tmp_path / ".paircoder" / "history"
        history_dir.mkdir(parents=True)
        tracker = TokenFeedbackTracker(history_dir)

        report = tracker.generate_report()

        assert report["stats"]["total_tasks"] == 0
        assert report["stats"]["avg_ratio"] == 1.0
