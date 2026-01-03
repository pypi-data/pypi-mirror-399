"""Tests for token counting and budget estimation module."""
import tempfile
from pathlib import Path
import pytest

from bpsai_pair.tokens import (
    count_tokens,
    count_file_tokens,
    estimate_task_tokens,
    get_budget_status,
    estimate_from_task_file,
    MODEL_LIMITS,
    THRESHOLDS,
    TASK_TYPE_MULTIPLIERS,
    TokenEstimate,
    BudgetStatus,
)


class TestCountTokens:
    """Tests for count_tokens function."""

    def test_empty_string(self):
        """Empty string returns 0 tokens."""
        assert count_tokens("") == 0

    def test_simple_text(self):
        """Simple text returns reasonable token count."""
        tokens = count_tokens("Hello, world!")
        assert tokens > 0
        assert tokens < 10  # Should be ~4 tokens

    def test_longer_text(self):
        """Longer text returns proportionally more tokens."""
        short = count_tokens("Hello")
        long = count_tokens("Hello, this is a much longer sentence with many words.")
        assert long > short

    def test_code_text(self):
        """Code text is tokenized correctly."""
        code = """
def hello():
    print("Hello, world!")
"""
        tokens = count_tokens(code)
        assert tokens > 0
        assert tokens < 50  # Reasonable for this snippet

    def test_unicode_text(self):
        """Unicode text is handled."""
        text = "Hello \u4e16\u754c"  # "Hello 世界"
        tokens = count_tokens(text)
        assert tokens > 0


class TestCountFileTokens:
    """Tests for count_file_tokens function."""

    def test_nonexistent_file(self):
        """Nonexistent file returns 0."""
        path = Path("/nonexistent/file.txt")
        assert count_file_tokens(path) == 0

    def test_empty_file(self, tmp_path):
        """Empty file returns 0 tokens."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")
        assert count_file_tokens(file_path) == 0

    def test_text_file(self, tmp_path):
        """Text file returns token count."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Hello, this is a test file with some content.")
        tokens = count_file_tokens(file_path)
        assert tokens > 0

    def test_binary_extension_skipped(self, tmp_path):
        """Files with binary extensions return 0."""
        for ext in ['.pyc', '.png', '.pdf', '.zip']:
            file_path = tmp_path / f"test{ext}"
            file_path.write_bytes(b"binary content")
            assert count_file_tokens(file_path) == 0

    def test_python_file(self, tmp_path):
        """Python file is counted correctly."""
        file_path = tmp_path / "test.py"
        file_path.write_text("""
def hello():
    print("Hello, world!")

if __name__ == "__main__":
    hello()
""")
        tokens = count_file_tokens(file_path)
        assert tokens > 0
        assert tokens < 100


class TestEstimateTaskTokens:
    """Tests for estimate_task_tokens function."""

    def test_basic_estimate(self, tmp_path):
        """Basic estimate returns TokenEstimate."""
        file1 = tmp_path / "test.py"
        file1.write_text("# Small file\nprint('hello')")

        estimate = estimate_task_tokens(
            task_id="T1",
            files=[file1],
            complexity=10
        )

        assert isinstance(estimate, TokenEstimate)
        assert estimate.base_context == 15000
        assert estimate.source_files > 0
        assert estimate.estimated_output > 0
        assert estimate.total > 0
        assert estimate.budget_percent > 0

    def test_complexity_affects_output(self, tmp_path):
        """Higher complexity increases estimated output."""
        file1 = tmp_path / "test.py"
        file1.write_text("# Small file")

        low = estimate_task_tokens(task_id="T1", files=[file1], complexity=5)
        high = estimate_task_tokens(task_id="T1", files=[file1], complexity=50)

        assert high.estimated_output > low.estimated_output

    def test_task_type_affects_output(self, tmp_path):
        """Task type multiplier affects estimated output."""
        file1 = tmp_path / "test.py"
        file1.write_text("# Small file")

        feature = estimate_task_tokens(task_id="T1", files=[file1], complexity=10, task_type="feature")
        chore = estimate_task_tokens(task_id="T1", files=[file1], complexity=10, task_type="chore")

        assert feature.estimated_output > chore.estimated_output

    def test_multiple_files(self, tmp_path):
        """Multiple files increase source_files count."""
        files = []
        for i in range(3):
            f = tmp_path / f"test{i}.py"
            f.write_text(f"# File {i}\nprint('hello')")
            files.append(f)

        single = estimate_task_tokens(task_id="T1", files=[files[0]], complexity=10)
        multi = estimate_task_tokens(task_id="T1", files=files, complexity=10)

        assert multi.source_files > single.source_files

    def test_empty_files_list(self):
        """Empty files list still returns estimate."""
        estimate = estimate_task_tokens(task_id="T1", files=[], complexity=10)
        assert estimate.source_files == 0
        assert estimate.total > 0  # Still has base context


class TestGetBudgetStatus:
    """Tests for get_budget_status function."""

    def test_ok_status(self):
        """Low usage returns ok status."""
        status = get_budget_status(estimated=30000)

        assert isinstance(status, BudgetStatus)
        assert status.status == "ok"
        assert status.percent < 50
        assert "healthy" in status.message.lower()

    def test_info_status(self):
        """50% usage returns info status."""
        limit = MODEL_LIMITS["claude-sonnet-4-5"]
        status = get_budget_status(estimated=int(limit * 0.55))

        assert status.status == "info"
        assert status.percent >= 50

    def test_warning_status(self):
        """75% usage returns warning status."""
        limit = MODEL_LIMITS["claude-sonnet-4-5"]
        status = get_budget_status(estimated=int(limit * 0.80))

        assert status.status == "warning"
        assert status.percent >= 75

    def test_critical_status(self):
        """90% usage returns critical status."""
        limit = MODEL_LIMITS["claude-sonnet-4-5"]
        status = get_budget_status(estimated=int(limit * 0.95))

        assert status.status == "critical"
        assert "compaction" in status.message.lower()

    def test_remaining_calculation(self):
        """Remaining tokens calculated correctly."""
        status = get_budget_status(estimated=50000)
        assert status.remaining == status.limit - status.used

    def test_different_models(self):
        """Different models have correct limits."""
        for model, limit in MODEL_LIMITS.items():
            status = get_budget_status(estimated=10000, model=model)
            assert status.limit == limit

    def test_unknown_model_uses_default(self):
        """Unknown model uses default limit."""
        status = get_budget_status(estimated=10000, model="unknown-model")
        assert status.limit == 200000


class TestEstimateFromTaskFile:
    """Tests for estimate_from_task_file function."""

    def test_nonexistent_file(self):
        """Nonexistent file returns None."""
        result = estimate_from_task_file(Path("/nonexistent/task.md"))
        assert result is None

    def test_parse_frontmatter(self, tmp_path):
        """Frontmatter is parsed correctly."""
        task_file = tmp_path / "T1.task.md"
        task_file.write_text("""---
id: T1
title: Test Task
type: bugfix
complexity: 25
---

# T1: Test Task

## Objective

Fix something.
""")

        estimate = estimate_from_task_file(task_file)
        assert estimate is not None
        # Type affects multiplier
        assert estimate.estimated_output < estimate_task_tokens(
            task_id="T1", files=[], complexity=25, task_type="feature"
        ).estimated_output

    def test_parse_files_section(self, tmp_path):
        """Files to Modify section is parsed."""
        # Create a source file that exists
        src_file = tmp_path / "test.py"
        src_file.write_text("print('hello')")

        task_file = tmp_path / "T1.task.md"
        task_file.write_text(f"""---
id: T1
complexity: 10
type: feature
---

# T1: Test Task

## Files to Modify

- {src_file}

## Notes

Done.
""")

        estimate = estimate_from_task_file(task_file)
        assert estimate is not None
        assert estimate.source_files > 0


class TestConstants:
    """Tests for module constants."""

    def test_model_limits_not_empty(self):
        """MODEL_LIMITS has entries."""
        assert len(MODEL_LIMITS) > 0

    def test_thresholds_ordered(self):
        """Thresholds are in ascending order."""
        assert THRESHOLDS["info"] < THRESHOLDS["warning"]
        assert THRESHOLDS["warning"] < THRESHOLDS["critical"]

    def test_task_type_multipliers(self):
        """Task type multipliers are reasonable."""
        for task_type, multiplier in TASK_TYPE_MULTIPLIERS.items():
            assert 0.5 <= multiplier <= 2.0
