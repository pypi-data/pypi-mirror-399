"""Tests for metrics module."""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from bpsai_pair.metrics.collector import (
    MetricsCollector,
    MetricsEvent,
    TokenUsage,
    PricingConfig,
    DEFAULT_PRICING,
)
from bpsai_pair.metrics.budget import (
    BudgetEnforcer,
    BudgetConfig,
    BudgetStatus,
)
from bpsai_pair.metrics.reports import (
    MetricsReporter,
    MetricsSummary,
)


class TestTokenUsage:
    """Tests for TokenUsage dataclass."""

    def test_total_property(self):
        """Test that total is sum of input and output."""
        usage = TokenUsage(input=100, output=50)
        assert usage.total == 150

    def test_default_values(self):
        """Test default values are zero."""
        usage = TokenUsage()
        assert usage.input == 0
        assert usage.output == 0
        assert usage.total == 0


class TestMetricsEvent:
    """Tests for MetricsEvent dataclass."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        event = MetricsEvent(
            timestamp="2025-01-15T10:00:00",
            session_id="sess-123",
            task_id="TASK-001",
            agent="claude-code",
            model="claude-sonnet-4-5-20250929",
            operation="invoke",
            tokens=TokenUsage(input=1000, output=500),
            cost_usd=0.045,
            duration_ms=3000,
            success=True,
        )

        d = event.to_dict()

        assert d["timestamp"] == "2025-01-15T10:00:00"
        assert d["session_id"] == "sess-123"
        assert d["task_id"] == "TASK-001"
        assert d["agent"] == "claude-code"
        assert d["tokens"]["total"] == 1500
        assert d["cost_usd"] == 0.045

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "timestamp": "2025-01-15T10:00:00",
            "session_id": "sess-123",
            "task_id": "TASK-001",
            "agent": "claude-code",
            "model": "claude-sonnet-4-5-20250929",
            "operation": "invoke",
            "tokens": {"input": 1000, "output": 500, "total": 1500},
            "cost_usd": 0.045,
            "duration_ms": 3000,
            "success": True,
        }

        event = MetricsEvent.from_dict(data)

        assert event.timestamp == "2025-01-15T10:00:00"
        assert event.tokens.input == 1000
        assert event.tokens.output == 500


class TestPricingConfig:
    """Tests for PricingConfig."""

    def test_default_pricing(self):
        """Test default pricing is loaded."""
        config = PricingConfig()
        pricing = config.get_pricing("claude-code", "claude-sonnet-4-5-20250929")

        assert pricing["input_per_1m"] == 3.00
        assert pricing["output_per_1m"] == 15.00

    def test_fallback_to_default(self):
        """Test fallback to default pricing for unknown model."""
        config = PricingConfig()
        pricing = config.get_pricing("claude-code", "unknown-model")

        # Should fall back to claude-code's default
        assert "input_per_1m" in pricing


class TestMetricsCollector:
    """Tests for MetricsCollector."""

    def test_calculate_cost(self):
        """Test cost calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            cost = collector.calculate_cost(
                "claude-code",
                "claude-sonnet-4-5-20250929",
                input_tokens=1_000_000,
                output_tokens=100_000
            )

            # 1M input @ $3/1M = $3, 100K output @ $15/1M = $1.5
            assert cost == 4.5

    def test_record_and_load(self):
        """Test recording and loading events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            # Record event
            event = collector.record_invocation(
                agent="claude-code",
                model="claude-sonnet-4-5-20250929",
                input_tokens=1000,
                output_tokens=500,
                duration_ms=3000,
                session_id="test-session",
                task_id="TASK-001",
            )

            # Load events
            events = collector.load_events()

            assert len(events) == 1
            assert events[0].session_id == "test-session"
            assert events[0].task_id == "TASK-001"

    def test_create_event_with_cost(self):
        """Test event creation includes calculated cost."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            event = collector.create_event(
                agent="claude-code",
                model="claude-sonnet-4-5-20250929",
                input_tokens=1000,
                output_tokens=500,
                duration_ms=3000,
            )

            assert event.cost_usd > 0
            assert event.tokens.total == 1500

    def test_get_session_events(self):
        """Test filtering by session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            # Record events for different sessions
            collector.record_invocation(
                agent="claude-code", model="test",
                input_tokens=100, output_tokens=50,
                duration_ms=1000, session_id="session-1"
            )
            collector.record_invocation(
                agent="claude-code", model="test",
                input_tokens=100, output_tokens=50,
                duration_ms=1000, session_id="session-2"
            )
            collector.record_invocation(
                agent="claude-code", model="test",
                input_tokens=100, output_tokens=50,
                duration_ms=1000, session_id="session-1"
            )

            events = collector.get_session_events("session-1")

            assert len(events) == 2

    def test_get_daily_totals(self):
        """Test daily totals calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            # Record multiple events
            for _ in range(3):
                collector.record_invocation(
                    agent="claude-code", model="test",
                    input_tokens=1000, output_tokens=500,
                    duration_ms=1000
                )

            totals = collector.get_daily_totals()

            assert totals["events"] == 3
            assert totals["tokens"]["input"] == 3000
            assert totals["tokens"]["output"] == 1500


class TestBudgetEnforcer:
    """Tests for BudgetEnforcer."""

    def test_check_budget_empty(self):
        """Test budget check with no events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))
            config = BudgetConfig(daily_limit_usd=10.0, monthly_limit_usd=200.0)
            enforcer = BudgetEnforcer(collector, config)

            status = enforcer.check_budget()

            assert status.daily_spent == 0
            assert status.daily_remaining == 10.0
            assert status.monthly_remaining == 200.0
            assert status.within_budget

    def test_can_proceed_within_budget(self):
        """Test can_proceed returns True within budget."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))
            config = BudgetConfig(daily_limit_usd=10.0)
            enforcer = BudgetEnforcer(collector, config)

            can, msg = enforcer.can_proceed(estimated_cost=5.0)

            assert can
            assert msg == "OK"

    def test_can_proceed_exceeds_daily(self):
        """Test can_proceed returns False when exceeding daily limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            # Record some usage
            collector.record_invocation(
                agent="claude-code", model="test",
                input_tokens=1_000_000, output_tokens=500_000,  # ~$10.50
                duration_ms=1000
            )

            config = BudgetConfig(daily_limit_usd=10.0)
            enforcer = BudgetEnforcer(collector, config)

            can, msg = enforcer.can_proceed(estimated_cost=1.0)

            assert not can
            assert "daily limit" in msg.lower()

    def test_alert_threshold(self):
        """Test alert triggered at threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            # Record usage at 85% of limit
            collector.record_invocation(
                agent="claude-code", model="test",
                input_tokens=2_833_333, output_tokens=0,  # ~$8.50 at $3/1M
                duration_ms=1000
            )

            config = BudgetConfig(daily_limit_usd=10.0, alert_threshold=0.8)
            enforcer = BudgetEnforcer(collector, config)

            status = enforcer.check_budget()

            assert status.alert_triggered
            assert "80" in status.alert_message or "85" in status.alert_message


class TestMetricsReporter:
    """Tests for MetricsReporter."""

    def test_get_summary(self):
        """Test summary generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            # Record events
            for i in range(5):
                collector.record_invocation(
                    agent="claude-code" if i < 3 else "codex-cli",
                    model="test",
                    input_tokens=1000,
                    output_tokens=500,
                    duration_ms=1000,
                    task_id=f"TASK-00{i % 2 + 1}",
                )

            reporter = MetricsReporter(collector)
            summary = reporter.get_summary("daily")

            assert summary.total_events == 5
            assert summary.successful_events == 5
            assert summary.input_tokens == 5000
            assert summary.output_tokens == 2500
            assert "claude-code" in summary.by_agent
            assert "codex-cli" in summary.by_agent

    def test_get_breakdown(self):
        """Test breakdown by dimension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            collector.record_invocation(
                agent="claude-code", model="test",
                input_tokens=1000, output_tokens=500,
                duration_ms=1000
            )
            collector.record_invocation(
                agent="codex-cli", model="test",
                input_tokens=1000, output_tokens=500,
                duration_ms=1000
            )

            reporter = MetricsReporter(collector)
            breakdown = reporter.get_breakdown(by="agent")

            assert "claude-code" in breakdown
            assert "codex-cli" in breakdown
            assert breakdown["claude-code"]["events"] == 1

    def test_export_csv(self):
        """Test CSV export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            collector.record_invocation(
                agent="claude-code", model="test",
                input_tokens=1000, output_tokens=500,
                duration_ms=1000, task_id="TASK-001"
            )

            reporter = MetricsReporter(collector)
            csv_content = reporter.export_csv()

            assert "timestamp" in csv_content
            assert "claude-code" in csv_content
            assert "TASK-001" in csv_content

    def test_format_summary_report(self):
        """Test summary report formatting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector(Path(tmpdir))

            collector.record_invocation(
                agent="claude-code", model="test",
                input_tokens=1000, output_tokens=500,
                duration_ms=1000
            )

            reporter = MetricsReporter(collector)
            summary = reporter.get_summary("daily")
            report = reporter.format_summary_report(summary)

            assert "Metrics Summary" in report
            assert "Total Tokens" in report
            assert "Total Cost" in report
