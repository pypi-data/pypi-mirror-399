"""Tests for velocity tracking module."""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from bpsai_pair.metrics.velocity import (
    VelocityTracker,
    VelocityStats,
    TaskCompletionRecord,
)


class TestTaskCompletionRecord:
    """Tests for TaskCompletionRecord dataclass."""

    def test_basic_creation(self):
        """Test creating a task completion record."""
        completed_at = datetime(2025, 12, 15, 10, 30, 0)
        record = TaskCompletionRecord(
            task_id="TASK-100",
            complexity=40,
            sprint="sprint-17",
            completed_at=completed_at,
        )

        assert record.task_id == "TASK-100"
        assert record.complexity == 40
        assert record.sprint == "sprint-17"
        assert record.completed_at == completed_at

    def test_to_dict(self):
        """Test conversion to dictionary."""
        completed_at = datetime(2025, 12, 15, 10, 30, 0)
        record = TaskCompletionRecord(
            task_id="TASK-100",
            complexity=40,
            sprint="sprint-17",
            completed_at=completed_at,
        )

        d = record.to_dict()
        assert d["task_id"] == "TASK-100"
        assert d["complexity"] == 40
        assert d["sprint"] == "sprint-17"
        assert d["completed_at"] == "2025-12-15T10:30:00"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "task_id": "TASK-101",
            "complexity": 25,
            "sprint": "sprint-16",
            "completed_at": "2025-12-10T14:00:00",
        }

        record = TaskCompletionRecord.from_dict(data)

        assert record.task_id == "TASK-101"
        assert record.complexity == 25
        assert record.sprint == "sprint-16"
        assert record.completed_at == datetime(2025, 12, 10, 14, 0, 0)


class TestVelocityStats:
    """Tests for VelocityStats dataclass."""

    def test_creation(self):
        """Test creating velocity stats."""
        stats = VelocityStats(
            points_this_week=45,
            points_this_sprint=120,
            avg_weekly_velocity=52.0,
            avg_sprint_velocity=180.0,
            weeks_tracked=4,
            sprints_tracked=3,
        )

        assert stats.points_this_week == 45
        assert stats.points_this_sprint == 120
        assert stats.avg_weekly_velocity == 52.0
        assert stats.avg_sprint_velocity == 180.0
        assert stats.weeks_tracked == 4
        assert stats.sprints_tracked == 3

    def test_to_dict(self):
        """Test conversion to dictionary."""
        stats = VelocityStats(
            points_this_week=45,
            points_this_sprint=120,
            avg_weekly_velocity=52.0,
            avg_sprint_velocity=180.0,
            weeks_tracked=4,
            sprints_tracked=3,
        )

        d = stats.to_dict()
        assert d["points_this_week"] == 45
        assert d["points_this_sprint"] == 120
        assert d["avg_weekly_velocity"] == 52.0


class TestVelocityTracker:
    """Tests for VelocityTracker class."""

    def test_init(self):
        """Test VelocityTracker initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))
            assert tracker.history_dir == Path(tmpdir)

    def test_record_task_completion(self):
        """Test recording a task completion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))

            record = tracker.record_completion(
                task_id="TASK-100",
                complexity=40,
                sprint="sprint-17",
            )

            assert record.task_id == "TASK-100"
            assert record.complexity == 40
            assert record.sprint == "sprint-17"
            assert record.completed_at is not None

    def test_record_with_custom_time(self):
        """Test recording with a specific completion time."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))
            completed_at = datetime(2025, 12, 15, 10, 0, 0)

            record = tracker.record_completion(
                task_id="TASK-100",
                complexity=40,
                sprint="sprint-17",
                completed_at=completed_at,
            )

            assert record.completed_at == completed_at

    def test_load_completions(self):
        """Test loading recorded completions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))

            # Record multiple completions
            tracker.record_completion("TASK-100", 40, "sprint-17")
            tracker.record_completion("TASK-101", 25, "sprint-17")
            tracker.record_completion("TASK-102", 60, "sprint-17")

            completions = tracker.load_completions()

            assert len(completions) == 3
            assert sum(c.complexity for c in completions) == 125

    def test_points_this_week(self):
        """Test calculating points completed this week."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))
            now = datetime.now()
            # Use weekday-aware offset: stay within current week (Mon=0, Sun=6)
            days_into_week = now.weekday()  # 0 on Monday, 6 on Sunday

            # Record tasks completed this week (within days_into_week range)
            if days_into_week >= 1:
                tracker.record_completion("TASK-100", 40, "sprint-17", now - timedelta(days=1))
            else:
                # On Monday, record for today
                tracker.record_completion("TASK-100", 40, "sprint-17", now)
            if days_into_week >= 2:
                tracker.record_completion("TASK-101", 25, "sprint-17", now - timedelta(days=2))
            else:
                # Record for earlier today or same day
                tracker.record_completion("TASK-101", 25, "sprint-17", now - timedelta(hours=1))

            # Record task from last week (should not count) - always 10+ days back
            tracker.record_completion("TASK-102", 60, "sprint-17", now - timedelta(days=10))

            points = tracker.get_points_this_week()

            assert points == 65  # 40 + 25

    def test_points_this_sprint(self):
        """Test calculating points for current sprint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))
            now = datetime.now()

            # Record tasks in current sprint
            tracker.record_completion("TASK-100", 40, "sprint-17", now - timedelta(days=1))
            tracker.record_completion("TASK-101", 25, "sprint-17", now - timedelta(days=3))

            # Record task from different sprint
            tracker.record_completion("TASK-102", 60, "sprint-16", now - timedelta(days=2))

            points = tracker.get_points_for_sprint("sprint-17")

            assert points == 65  # 40 + 25

    def test_weekly_velocity_average(self):
        """Test calculating rolling weekly velocity average."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))
            now = datetime.now()
            # Get start of current week (Monday 00:00:00)
            week_start = tracker._get_week_start(now)

            # Record tasks across 4 weeks using week boundaries
            # Week 1 (current): 45 points - place at start of week + a few hours
            tracker.record_completion("T1", 25, "s17", week_start + timedelta(hours=10))
            tracker.record_completion("T2", 20, "s17", week_start + timedelta(hours=12))

            # Week 2 (previous): 50 points
            tracker.record_completion("T3", 30, "s17", week_start - timedelta(days=7) + timedelta(hours=10))
            tracker.record_completion("T4", 20, "s17", week_start - timedelta(days=7) + timedelta(hours=12))

            # Week 3: 60 points
            tracker.record_completion("T5", 40, "s17", week_start - timedelta(days=14) + timedelta(hours=10))
            tracker.record_completion("T6", 20, "s17", week_start - timedelta(days=14) + timedelta(hours=12))

            # Week 4: 55 points
            tracker.record_completion("T7", 35, "s17", week_start - timedelta(days=21) + timedelta(hours=10))
            tracker.record_completion("T8", 20, "s17", week_start - timedelta(days=21) + timedelta(hours=12))

            avg = tracker.get_weekly_velocity_average(weeks=4)

            # Average of 45, 50, 60, 55 = 210 / 4 = 52.5
            assert avg == pytest.approx(52.5, rel=0.1)

    def test_sprint_velocity_average(self):
        """Test calculating sprint velocity average."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))
            now = datetime.now()

            # Sprint 17: 120 points
            tracker.record_completion("T1", 40, "sprint-17", now - timedelta(days=1))
            tracker.record_completion("T2", 40, "sprint-17", now - timedelta(days=2))
            tracker.record_completion("T3", 40, "sprint-17", now - timedelta(days=3))

            # Sprint 16: 180 points
            tracker.record_completion("T4", 60, "sprint-16", now - timedelta(days=15))
            tracker.record_completion("T5", 60, "sprint-16", now - timedelta(days=16))
            tracker.record_completion("T6", 60, "sprint-16", now - timedelta(days=17))

            # Sprint 15: 150 points
            tracker.record_completion("T7", 50, "sprint-15", now - timedelta(days=29))
            tracker.record_completion("T8", 50, "sprint-15", now - timedelta(days=30))
            tracker.record_completion("T9", 50, "sprint-15", now - timedelta(days=31))

            avg = tracker.get_sprint_velocity_average(sprints=3)

            # Average of 120, 180, 150 = 450 / 3 = 150
            assert avg == pytest.approx(150.0, rel=0.1)

    def test_get_velocity_stats(self):
        """Test getting comprehensive velocity stats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))
            now = datetime.now()
            # Get start of current week (Monday 00:00:00)
            week_start = tracker._get_week_start(now)

            # Record some completions - use week boundaries to avoid day-of-week issues
            # This week: 45 points
            tracker.record_completion("T1", 45, "sprint-17", week_start + timedelta(hours=10))
            # Last week: 75 points
            tracker.record_completion("T2", 75, "sprint-17", week_start - timedelta(days=7) + timedelta(hours=10))

            stats = tracker.get_velocity_stats(
                current_sprint="sprint-17",
                weeks_for_average=4,
                sprints_for_average=3,
            )

            assert isinstance(stats, VelocityStats)
            assert stats.points_this_week == 45
            assert stats.points_this_sprint == 120  # 45 + 75

    def test_empty_velocity_stats(self):
        """Test velocity stats with no completions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))

            stats = tracker.get_velocity_stats(current_sprint="sprint-17")

            assert stats.points_this_week == 0
            assert stats.points_this_sprint == 0
            assert stats.avg_weekly_velocity == 0.0
            assert stats.avg_sprint_velocity == 0.0

    def test_persistence(self):
        """Test that completions persist across tracker instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # First tracker instance
            tracker1 = VelocityTracker(Path(tmpdir))
            tracker1.record_completion("TASK-100", 40, "sprint-17")
            tracker1.record_completion("TASK-101", 25, "sprint-17")

            # Second tracker instance (same directory)
            tracker2 = VelocityTracker(Path(tmpdir))
            completions = tracker2.load_completions()

            assert len(completions) == 2
            assert sum(c.complexity for c in completions) == 65

    def test_filter_by_date_range(self):
        """Test filtering completions by date range."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))

            # Record across different dates
            tracker.record_completion("T1", 40, "s17", datetime(2025, 12, 10))
            tracker.record_completion("T2", 25, "s17", datetime(2025, 12, 15))
            tracker.record_completion("T3", 60, "s17", datetime(2025, 12, 18))

            completions = tracker.load_completions(
                start_date=datetime(2025, 12, 12),
                end_date=datetime(2025, 12, 17),
            )

            assert len(completions) == 1
            assert completions[0].task_id == "T2"

    def test_week_boundaries(self):
        """Test that week calculation uses Monday as start."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))

            # Get a known Monday
            monday = datetime(2025, 12, 15)  # This is a Monday

            # Record on the Monday and previous Sunday
            tracker.record_completion("T1", 40, "s17", monday)  # This week
            tracker.record_completion("T2", 30, "s17", monday - timedelta(days=1))  # Last week

            points = tracker.get_points_for_week(monday)

            assert points == 40  # Only Monday's task

    def test_get_weekly_breakdown(self):
        """Test getting breakdown by week."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))
            now = datetime.now()

            # Record across weeks
            tracker.record_completion("T1", 40, "s17", now - timedelta(days=1))
            tracker.record_completion("T2", 50, "s17", now - timedelta(days=8))
            tracker.record_completion("T3", 60, "s17", now - timedelta(days=15))

            breakdown = tracker.get_weekly_breakdown(weeks=4)

            assert len(breakdown) == 4  # 4 weeks
            assert all("week_start" in entry for entry in breakdown)
            assert all("points" in entry for entry in breakdown)

    def test_get_sprint_breakdown(self):
        """Test getting breakdown by sprint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VelocityTracker(Path(tmpdir))
            now = datetime.now()

            # Record in different sprints
            tracker.record_completion("T1", 40, "sprint-17", now)
            tracker.record_completion("T2", 40, "sprint-17", now)
            tracker.record_completion("T3", 60, "sprint-16", now)
            tracker.record_completion("T4", 50, "sprint-15", now)

            breakdown = tracker.get_sprint_breakdown()

            assert "sprint-17" in breakdown
            assert breakdown["sprint-17"] == 80
            assert "sprint-16" in breakdown
            assert breakdown["sprint-16"] == 60
