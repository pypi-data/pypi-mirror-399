"""Tests for benchmarking framework."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from bpsai_pair.benchmarks.runner import (
    BenchmarkRunner,
    BenchmarkResult,
    BenchmarkConfig,
    BenchmarkTask,
    BenchmarkSuite,
)
from bpsai_pair.benchmarks.validation import (
    BenchmarkValidator,
    ValidationResult,
)
from bpsai_pair.benchmarks.reports import (
    BenchmarkReporter,
    AgentStats,
    BenchmarkComparison,
)


class TestBenchmarkTask:
    """Tests for BenchmarkTask."""

    def test_from_dict(self):
        """Test creating task from dictionary."""
        data = {
            "description": "Fix a bug",
            "category": "fix",
            "complexity": "low",
            "prompt": "Fix the bug in loop.py",
            "validation": [{"test": "pytest tests/"}],
        }

        task = BenchmarkTask.from_dict("simple-fix", data)

        assert task.id == "simple-fix"
        assert task.category == "fix"
        assert task.complexity == "low"
        assert len(task.validation) == 1


class TestBenchmarkResult:
    """Tests for BenchmarkResult."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = BenchmarkResult(
            benchmark_id="test-bench",
            agent="claude-code",
            model="claude-sonnet",
            iteration=0,
            timestamp="2025-01-15T10:00:00",
            success=True,
            validation_passed=["test:pytest"],
            duration_seconds=30.5,
            tokens_input=1000,
            tokens_output=500,
            cost_usd=0.045,
        )

        d = result.to_dict()

        assert d["benchmark_id"] == "test-bench"
        assert d["success"] is True
        assert d["duration_seconds"] == 30.5

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "benchmark_id": "test-bench",
            "agent": "claude-code",
            "model": "claude-sonnet",
            "iteration": 0,
            "timestamp": "2025-01-15T10:00:00",
            "success": True,
            "validation_passed": [],
            "validation_failed": [],
            "duration_seconds": 30.5,
            "tokens_input": 1000,
            "tokens_output": 500,
            "cost_usd": 0.045,
            "files_modified": [],
            "error": None,
        }

        result = BenchmarkResult.from_dict(data)

        assert result.benchmark_id == "test-bench"
        assert result.duration_seconds == 30.5


class TestBenchmarkSuite:
    """Tests for BenchmarkSuite."""

    def test_from_yaml(self):
        """Test loading suite from YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            suite_path = Path(tmpdir) / "suite.yaml"
            suite_path.write_text(yaml.dump({
                "name": "test-suite",
                "description": "Test benchmarks",
                "benchmarks": {
                    "simple-fix": {
                        "description": "Fix a simple bug",
                        "category": "fix",
                        "complexity": "low",
                        "prompt": "Fix the bug",
                    },
                    "feature-add": {
                        "description": "Add a feature",
                        "category": "implement",
                        "complexity": "medium",
                        "prompt": "Add pagination",
                    },
                },
            }))

            suite = BenchmarkSuite.from_yaml(suite_path)

            assert suite.name == "test-suite"
            assert len(suite.benchmarks) == 2
            assert "simple-fix" in suite.benchmarks
            assert suite.benchmarks["simple-fix"].category == "fix"


class TestBenchmarkValidator:
    """Tests for BenchmarkValidator."""

    def test_check_exists_pass(self):
        """Test file existence check passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            (workspace / "test.py").write_text("# test")

            validator = BenchmarkValidator(workspace)
            result = validator.validate([{"exists": "test.py"}])

            assert result.passed
            assert "exists:test.py" in result.passed_checks

    def test_check_exists_fail(self):
        """Test file existence check fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = BenchmarkValidator(Path(tmpdir))
            result = validator.validate([{"exists": "missing.py"}])

            assert not result.passed
            assert "exists:missing.py" in result.failed_checks

    def test_check_contains(self):
        """Test content check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            (workspace / "design.md").write_text("# Design\n\nThis includes cache invalidation strategy.")

            validator = BenchmarkValidator(workspace)
            result = validator.validate([
                {"contains": "design.md", "text": "cache invalidation"}
            ])

            assert result.passed

    def test_multiple_checks(self):
        """Test multiple validation checks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            (workspace / "main.py").write_text("def main(): pass")
            (workspace / "test.py").write_text("def test_main(): pass")

            validator = BenchmarkValidator(workspace)
            result = validator.validate([
                {"exists": "main.py"},
                {"exists": "test.py"},
                {"exists": "missing.py"},
            ])

            assert not result.passed
            assert len(result.passed_checks) == 2
            assert len(result.failed_checks) == 1


class TestBenchmarkRunner:
    """Tests for BenchmarkRunner."""

    def test_dry_run(self):
        """Test dry run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            suite_path = Path(tmpdir) / "suite.yaml"
            suite_path.write_text(yaml.dump({
                "benchmarks": {
                    "test-bench": {
                        "description": "Test",
                        "category": "fix",
                        "complexity": "low",
                        "prompt": "Do something",
                    },
                },
            }))

            output_dir = Path(tmpdir) / "output"
            config = BenchmarkConfig(
                iterations=1,
                agents=["claude-code"],
                dry_run=True,
            )

            runner = BenchmarkRunner(suite_path, output_dir, config)
            results = runner.run()

            assert len(results) == 1
            assert results[0].success
            assert results[0].model == "dry-run"

    def test_workspace_setup(self):
        """Test workspace setup with fixtures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create fixture
            fixtures_dir = Path(tmpdir) / "fixtures"
            fixtures_dir.mkdir()
            (fixtures_dir / "test.py").write_text("# fixture content")

            suite_path = Path(tmpdir) / "suite.yaml"
            suite_path.write_text(yaml.dump({
                "benchmarks": {
                    "test-bench": {
                        "description": "Test",
                        "category": "fix",
                        "complexity": "low",
                        "prompt": "Do something",
                        "setup": [{"copy": "test.py"}],
                    },
                },
            }))

            output_dir = Path(tmpdir) / "output"
            runner = BenchmarkRunner(suite_path, output_dir)

            # The setup happens during _run_single, tested indirectly via dry_run
            assert runner.fixtures_dir == fixtures_dir

    def test_compute_summary(self):
        """Test summary computation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            suite_path = Path(tmpdir) / "suite.yaml"
            suite_path.write_text(yaml.dump({"benchmarks": {}}))
            runner = BenchmarkRunner(suite_path, Path(tmpdir))

            results = [
                BenchmarkResult(
                    benchmark_id="bench-1", agent="claude-code", model="test",
                    iteration=0, timestamp="", success=True,
                    duration_seconds=10, cost_usd=0.01
                ),
                BenchmarkResult(
                    benchmark_id="bench-1", agent="claude-code", model="test",
                    iteration=1, timestamp="", success=True,
                    duration_seconds=15, cost_usd=0.02
                ),
                BenchmarkResult(
                    benchmark_id="bench-1", agent="codex-cli", model="test",
                    iteration=0, timestamp="", success=False,
                    duration_seconds=20, cost_usd=0.015
                ),
            ]

            summary = runner._compute_summary(results)

            assert summary["total"] == 3
            assert summary["passed"] == 2
            assert summary["failed"] == 1
            assert "claude-code" in summary["by_agent"]
            assert summary["by_agent"]["claude-code"]["passed"] == 2


class TestBenchmarkReporter:
    """Tests for BenchmarkReporter."""

    def test_get_agent_stats(self):
        """Test agent statistics calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reporter = BenchmarkReporter(Path(tmpdir))

            results = [
                BenchmarkResult(
                    benchmark_id="test", agent="claude-code", model="test",
                    iteration=0, timestamp="", success=True,
                    duration_seconds=30, cost_usd=0.05, tokens_input=1000, tokens_output=500
                ),
                BenchmarkResult(
                    benchmark_id="test", agent="claude-code", model="test",
                    iteration=1, timestamp="", success=True,
                    duration_seconds=20, cost_usd=0.03, tokens_input=800, tokens_output=400
                ),
                BenchmarkResult(
                    benchmark_id="test", agent="claude-code", model="test",
                    iteration=2, timestamp="", success=False,
                    duration_seconds=40, cost_usd=0.04, tokens_input=1200, tokens_output=600
                ),
            ]

            stats = reporter.get_agent_stats(results, "claude-code")

            assert stats.total_runs == 3
            assert stats.successful_runs == 2
            assert stats.success_rate == 2/3
            assert stats.avg_duration_seconds == 30  # (30+20+40)/3
            assert stats.total_tokens == 4500  # sum of all tokens

    def test_compare_agents(self):
        """Test agent comparison."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reporter = BenchmarkReporter(Path(tmpdir))

            results = [
                # Claude results - better success rate
                BenchmarkResult(
                    benchmark_id="test", agent="claude-code", model="test",
                    iteration=0, timestamp="", success=True,
                    duration_seconds=30, cost_usd=0.05
                ),
                BenchmarkResult(
                    benchmark_id="test", agent="claude-code", model="test",
                    iteration=1, timestamp="", success=True,
                    duration_seconds=35, cost_usd=0.06
                ),
                # Codex results - faster and cheaper but lower success
                BenchmarkResult(
                    benchmark_id="test", agent="codex-cli", model="test",
                    iteration=0, timestamp="", success=True,
                    duration_seconds=20, cost_usd=0.03
                ),
                BenchmarkResult(
                    benchmark_id="test", agent="codex-cli", model="test",
                    iteration=1, timestamp="", success=False,
                    duration_seconds=15, cost_usd=0.02
                ),
            ]

            comparison = reporter.compare_agents(results, "claude-code", "codex-cli")

            assert comparison.baseline == "claude-code"
            assert comparison.challenger == "codex-cli"
            assert comparison.winner_success == "claude-code"  # 100% vs 50%
            assert comparison.winner_speed == "codex-cli"  # 17.5s vs 32.5s
            assert comparison.winner_cost == "codex-cli"  # $0.025 vs $0.055
            assert len(comparison.recommendations) > 0

    def test_format_summary(self):
        """Test summary formatting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reporter = BenchmarkReporter(Path(tmpdir))

            results = [
                BenchmarkResult(
                    benchmark_id="test-1", agent="claude-code", model="test",
                    iteration=0, timestamp="", success=True,
                    duration_seconds=30, cost_usd=0.05
                ),
                BenchmarkResult(
                    benchmark_id="test-2", agent="claude-code", model="test",
                    iteration=0, timestamp="", success=False,
                    duration_seconds=20, cost_usd=0.03
                ),
            ]

            summary = reporter.format_summary(results)

            assert "Benchmark Results Summary" in summary
            assert "Total Runs:    2" in summary
            assert "Passed:        1" in summary
            assert "50.0%" in summary
