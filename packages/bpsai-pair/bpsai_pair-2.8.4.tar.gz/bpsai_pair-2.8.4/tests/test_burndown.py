"""Tests for burndown chart data generation."""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from bpsai_pair.metrics.burndown import (
    BurndownGenerator,
    BurndownData,
    BurndownDataPoint,
    SprintConfig,
)


class TestSprintConfig:
    """Tests for SprintConfig dataclass."""

    def test_basic_creation(self):
        """Test creating a sprint config."""
        config = SprintConfig(
            sprint_id="sprint-17",
            start_date=datetime(2025, 12, 16),
            end_date=datetime(2025, 12, 20),
            total_points=230,
        )

        assert config.sprint_id == "sprint-17"
        assert config.start_date == datetime(2025, 12, 16)
        assert config.end_date == datetime(2025, 12, 20)
        assert config.total_points == 230

    def test_duration_days(self):
        """Test calculating duration in days."""
        config = SprintConfig(
            sprint_id="sprint-17",
            start_date=datetime(2025, 12, 16),
            end_date=datetime(2025, 12, 20),
            total_points=100,
        )

        assert config.duration_days == 5  # Dec 16-20 inclusive

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = SprintConfig(
            sprint_id="sprint-17",
            start_date=datetime(2025, 12, 16),
            end_date=datetime(2025, 12, 20),
            total_points=100,
        )

        d = config.to_dict()
        assert d["sprint_id"] == "sprint-17"
        assert d["start_date"] == "2025-12-16"
        assert d["end_date"] == "2025-12-20"
        assert d["total_points"] == 100


class TestBurndownDataPoint:
    """Tests for BurndownDataPoint dataclass."""

    def test_basic_creation(self):
        """Test creating a data point."""
        point = BurndownDataPoint(
            date=datetime(2025, 12, 17),
            remaining=200,
            ideal=180.0,
            completed=30,
        )

        assert point.date == datetime(2025, 12, 17)
        assert point.remaining == 200
        assert point.ideal == 180.0
        assert point.completed == 30

    def test_to_dict(self):
        """Test conversion to dictionary."""
        point = BurndownDataPoint(
            date=datetime(2025, 12, 17),
            remaining=200,
            ideal=180.0,
            completed=30,
        )

        d = point.to_dict()
        assert d["date"] == "2025-12-17"
        assert d["remaining"] == 200
        assert d["ideal"] == 180.0
        assert d["completed"] == 30


class TestBurndownData:
    """Tests for BurndownData dataclass."""

    def test_basic_creation(self):
        """Test creating burndown data."""
        config = SprintConfig(
            sprint_id="sprint-17",
            start_date=datetime(2025, 12, 16),
            end_date=datetime(2025, 12, 20),
            total_points=100,
        )

        data = BurndownData(
            config=config,
            data_points=[
                BurndownDataPoint(datetime(2025, 12, 16), 100, 100.0, 0),
                BurndownDataPoint(datetime(2025, 12, 17), 80, 75.0, 20),
            ],
        )

        assert data.config.sprint_id == "sprint-17"
        assert len(data.data_points) == 2

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = SprintConfig(
            sprint_id="sprint-17",
            start_date=datetime(2025, 12, 16),
            end_date=datetime(2025, 12, 20),
            total_points=100,
        )

        data = BurndownData(
            config=config,
            data_points=[
                BurndownDataPoint(datetime(2025, 12, 16), 100, 100.0, 0),
            ],
        )

        d = data.to_dict()
        assert d["sprint"] == "sprint-17"
        assert d["start_date"] == "2025-12-16"
        assert d["end_date"] == "2025-12-20"
        assert d["total_points"] == 100
        assert len(d["data"]) == 1

    def test_to_json(self):
        """Test JSON serialization."""
        config = SprintConfig(
            sprint_id="sprint-17",
            start_date=datetime(2025, 12, 16),
            end_date=datetime(2025, 12, 18),
            total_points=100,
        )

        data = BurndownData(
            config=config,
            data_points=[
                BurndownDataPoint(datetime(2025, 12, 16), 100, 100.0, 0),
            ],
        )

        json_str = data.to_json()
        parsed = json.loads(json_str)

        assert parsed["sprint"] == "sprint-17"
        assert "data" in parsed


class TestBurndownGenerator:
    """Tests for BurndownGenerator class."""

    def test_init(self):
        """Test BurndownGenerator initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = BurndownGenerator(Path(tmpdir))
            assert generator.history_dir == Path(tmpdir)

    def test_calculate_ideal_burndown(self):
        """Test ideal burndown calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = BurndownGenerator(Path(tmpdir))

            # 4 day sprint (Dec 16-19): burns 25 points per day
            config = SprintConfig(
                sprint_id="sprint-17",
                start_date=datetime(2025, 12, 16),
                end_date=datetime(2025, 12, 19),  # 4 days = 3 day delta
                total_points=100,
            )

            # Day 0 (start): 100 points remaining
            # Day 1: ~67 points (33% burned)
            # Day 2: ~33 points (67% burned)
            # Day 3 (end): 0 points (100% burned)

            ideal = generator._calculate_ideal_remaining(config, datetime(2025, 12, 16))
            assert ideal == 100.0

            # After 1 day: 100 - (100/3) = ~66.7
            ideal = generator._calculate_ideal_remaining(config, datetime(2025, 12, 17))
            assert ideal == pytest.approx(66.67, rel=0.01)

            # After 2 days: 100 - (200/3) = ~33.3
            ideal = generator._calculate_ideal_remaining(config, datetime(2025, 12, 18))
            assert ideal == pytest.approx(33.33, rel=0.01)

            # End of sprint: 0
            ideal = generator._calculate_ideal_remaining(config, datetime(2025, 12, 19))
            assert ideal == pytest.approx(0.0, rel=0.01)

    def test_generate_basic_burndown(self):
        """Test generating basic burndown data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = BurndownGenerator(Path(tmpdir))

            config = SprintConfig(
                sprint_id="sprint-17",
                start_date=datetime(2025, 12, 16),
                end_date=datetime(2025, 12, 18),  # 3 days
                total_points=100,
            )

            # Record some completions
            from bpsai_pair.metrics.velocity import VelocityTracker
            tracker = VelocityTracker(Path(tmpdir))
            tracker.record_completion("T1", 20, "sprint-17", datetime(2025, 12, 16, 14, 0))
            tracker.record_completion("T2", 30, "sprint-17", datetime(2025, 12, 17, 10, 0))

            data = generator.generate(config)

            assert data.config.sprint_id == "sprint-17"
            assert len(data.data_points) == 3  # 3 days

            # Check first day
            day1 = data.data_points[0]
            assert day1.date.date() == datetime(2025, 12, 16).date()
            assert day1.remaining == 80  # 100 - 20 completed
            assert day1.completed == 20

            # Check second day
            day2 = data.data_points[1]
            assert day2.date.date() == datetime(2025, 12, 17).date()
            assert day2.remaining == 50  # 100 - 20 - 30 completed
            assert day2.completed == 50

    def test_generate_empty_sprint(self):
        """Test generating burndown with no completions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = BurndownGenerator(Path(tmpdir))

            config = SprintConfig(
                sprint_id="sprint-17",
                start_date=datetime(2025, 12, 16),
                end_date=datetime(2025, 12, 18),
                total_points=100,
            )

            data = generator.generate(config)

            assert len(data.data_points) == 3
            # All points should show remaining = total
            for point in data.data_points:
                assert point.remaining == 100
                assert point.completed == 0

    def test_generate_with_future_dates(self):
        """Test generating burndown with future dates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = BurndownGenerator(Path(tmpdir))

            # Sprint that extends into the future
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            config = SprintConfig(
                sprint_id="sprint-17",
                start_date=today - timedelta(days=2),
                end_date=today + timedelta(days=2),
                total_points=100,
            )

            data = generator.generate(config)

            # Should have data points up to today (not future)
            assert len(data.data_points) <= 5

    def test_from_tasks(self):
        """Test creating config from tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = BurndownGenerator(Path(tmpdir))

            # Mock tasks
            class MockTask:
                def __init__(self, task_id, complexity, sprint):
                    self.id = task_id
                    self.complexity = complexity
                    self.sprint = sprint

            tasks = [
                MockTask("T1", 40, "sprint-17"),
                MockTask("T2", 30, "sprint-17"),
                MockTask("T3", 30, "sprint-17"),
            ]

            config = generator.create_config_from_tasks(
                sprint_id="sprint-17",
                tasks=tasks,
                start_date=datetime(2025, 12, 16),
                end_date=datetime(2025, 12, 20),
            )

            assert config.sprint_id == "sprint-17"
            assert config.total_points == 100

    def test_completion_tracking_by_day(self):
        """Test that completions are correctly tracked by day."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = BurndownGenerator(Path(tmpdir))

            config = SprintConfig(
                sprint_id="sprint-17",
                start_date=datetime(2025, 12, 16),
                end_date=datetime(2025, 12, 19),  # 4 days
                total_points=100,
            )

            # Record completions on different days
            from bpsai_pair.metrics.velocity import VelocityTracker
            tracker = VelocityTracker(Path(tmpdir))

            # Day 1: 20 points
            tracker.record_completion("T1", 20, "sprint-17", datetime(2025, 12, 16, 14, 0))

            # Day 2: 30 more points (50 total)
            tracker.record_completion("T2", 30, "sprint-17", datetime(2025, 12, 17, 10, 0))

            # Day 3: 25 more points (75 total)
            tracker.record_completion("T3", 25, "sprint-17", datetime(2025, 12, 18, 16, 0))

            data = generator.generate(config)

            # Verify cumulative completion
            assert data.data_points[0].completed == 20
            assert data.data_points[0].remaining == 80

            assert data.data_points[1].completed == 50
            assert data.data_points[1].remaining == 50

            assert data.data_points[2].completed == 75
            assert data.data_points[2].remaining == 25

    def test_generate_for_date_range(self):
        """Test generating burndown for specific date range (past dates)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = BurndownGenerator(Path(tmpdir))

            # Use past dates to ensure all data points are generated
            config = SprintConfig(
                sprint_id="sprint-17",
                start_date=datetime(2025, 12, 1),
                end_date=datetime(2025, 12, 10),  # 10 days, all in past
                total_points=100,
            )

            data = generator.generate(config)

            assert len(data.data_points) == 10

    def test_burndown_with_overcompletion(self):
        """Test burndown when more is completed than planned."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = BurndownGenerator(Path(tmpdir))

            config = SprintConfig(
                sprint_id="sprint-17",
                start_date=datetime(2025, 12, 16),
                end_date=datetime(2025, 12, 18),
                total_points=50,  # Only 50 planned
            )

            # Complete 60 points (more than planned)
            from bpsai_pair.metrics.velocity import VelocityTracker
            tracker = VelocityTracker(Path(tmpdir))
            tracker.record_completion("T1", 60, "sprint-17", datetime(2025, 12, 17, 10, 0))

            data = generator.generate(config)

            # Remaining should be 0 or negative
            day2 = data.data_points[1]
            assert day2.completed == 60
            # Remaining can be negative (or clamped to 0)
            assert day2.remaining <= 0

    def test_get_completions_for_date(self):
        """Test getting completions for a specific date."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = BurndownGenerator(Path(tmpdir))

            from bpsai_pair.metrics.velocity import VelocityTracker
            tracker = VelocityTracker(Path(tmpdir))

            # Record completions on Dec 17
            tracker.record_completion("T1", 20, "sprint-17", datetime(2025, 12, 17, 10, 0))
            tracker.record_completion("T2", 15, "sprint-17", datetime(2025, 12, 17, 14, 0))

            # Record completion on different day
            tracker.record_completion("T3", 30, "sprint-17", datetime(2025, 12, 18, 10, 0))

            completions = generator._get_completions_for_date(
                "sprint-17",
                datetime(2025, 12, 17),
            )

            assert completions == 35  # 20 + 15

    def test_persistence(self):
        """Test that burndown uses persisted velocity data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # First, record completions
            from bpsai_pair.metrics.velocity import VelocityTracker
            tracker = VelocityTracker(Path(tmpdir))
            tracker.record_completion("T1", 40, "sprint-17", datetime(2025, 12, 16, 12, 0))

            # Now create a new generator and verify it sees the data
            generator = BurndownGenerator(Path(tmpdir))
            config = SprintConfig(
                sprint_id="sprint-17",
                start_date=datetime(2025, 12, 16),
                end_date=datetime(2025, 12, 17),
                total_points=100,
            )

            data = generator.generate(config)

            assert data.data_points[0].completed == 40
            assert data.data_points[0].remaining == 60

    def test_sprint_filter(self):
        """Test that only completions for the specified sprint are counted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = BurndownGenerator(Path(tmpdir))

            from bpsai_pair.metrics.velocity import VelocityTracker
            tracker = VelocityTracker(Path(tmpdir))

            # Record completions for different sprints
            tracker.record_completion("T1", 40, "sprint-17", datetime(2025, 12, 17, 10, 0))
            tracker.record_completion("T2", 30, "sprint-16", datetime(2025, 12, 17, 11, 0))  # Different sprint

            config = SprintConfig(
                sprint_id="sprint-17",
                start_date=datetime(2025, 12, 16),
                end_date=datetime(2025, 12, 18),
                total_points=100,
            )

            data = generator.generate(config)

            # Only sprint-17 completions should count
            day2 = data.data_points[1]
            assert day2.completed == 40  # Only T1
