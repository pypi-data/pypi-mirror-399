"""Tests for the constants module."""

import pytest

from bpsai_pair.core.constants import (
    TASK_ID_PATTERN,
    TASK_ID_REGEX,
    TASK_FILE_GLOBS,
    is_valid_task_id,
    extract_task_id,
    extract_task_id_from_card_name,
)


class TestTaskIdPattern:
    """Tests for task ID pattern matching."""

    @pytest.mark.parametrize(
        "task_id",
        [
            "TASK-001",
            "TASK-142",
            "TASK-9999",
            "T18.1",
            "T18.12",
            "T1.1",
            "T100.99",
            "REL-18-01",
            "REL-1-1",
            "REL-100-99",
            "BUG-001",
            "BUG-005",
            "BUG-9999",
        ],
    )
    def test_valid_task_ids(self, task_id: str):
        """Test that valid task IDs are recognized."""
        assert is_valid_task_id(task_id), f"{task_id} should be valid"

    @pytest.mark.parametrize(
        "task_id",
        [
            "task-001",  # lowercase (should still match case-insensitive)
            "t18.1",  # lowercase
            "rel-18-01",  # lowercase
            "bug-005",  # lowercase
        ],
    )
    def test_valid_task_ids_case_insensitive(self, task_id: str):
        """Test that task IDs are case-insensitive."""
        assert is_valid_task_id(task_id), f"{task_id} should be valid (case-insensitive)"

    @pytest.mark.parametrize(
        "invalid_id",
        [
            "TASK",
            "T18",
            "T.1",
            "REL-18",
            "BUG",
            "FEATURE-001",
            "random-text",
            "",
            "123",
        ],
    )
    def test_invalid_task_ids(self, invalid_id: str):
        """Test that invalid task IDs are rejected."""
        assert not is_valid_task_id(invalid_id), f"{invalid_id} should be invalid"


class TestExtractTaskId:
    """Tests for task ID extraction from text."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("TASK-001 implementation", "TASK-001"),
            ("[TASK-001] Title here", "TASK-001"),
            ("feature/TASK-142-description", "TASK-142"),
            ("T18.1-add-feature", "T18.1"),
            ("feature/T18.1/implementation", "T18.1"),
            ("[T18.12] Sprint task", "T18.12"),
            ("REL-18-01-release-prep", "REL-18-01"),
            ("[REL-18-01] Release", "REL-18-01"),
            ("BUG-005 fix", "BUG-005"),
            ("[BUG-123] Critical fix", "BUG-123"),
            ("No task here", None),
            ("", None),
        ],
    )
    def test_extract_task_id(self, text: str, expected: str | None):
        """Test task ID extraction from various text formats."""
        result = extract_task_id(text)
        if expected:
            assert result == expected.upper()
        else:
            assert result is None


class TestExtractTaskIdFromCardName:
    """Tests for task ID extraction from Trello card names."""

    @pytest.mark.parametrize(
        "card_name,expected",
        [
            ("[TASK-066] Title", "TASK-066"),
            ("[TASK-001] Implementation of feature", "TASK-001"),
            ("[T18.1] Sprint task", "T18.1"),
            ("[T18.12] Another task", "T18.12"),
            ("[REL-18-01] Release prep", "REL-18-01"),
            ("[BUG-005] Fix issue", "BUG-005"),
            ("No brackets here", None),
            ("[INVALID] Something", None),
            ("", None),
            ("[] Empty brackets", None),
        ],
    )
    def test_extract_from_card_name(self, card_name: str, expected: str | None):
        """Test task ID extraction from Trello card names."""
        assert extract_task_id_from_card_name(card_name) == expected


class TestTaskFileGlobs:
    """Tests for task file glob patterns."""

    def test_glob_patterns_exist(self):
        """Test that glob patterns are defined."""
        assert len(TASK_FILE_GLOBS) > 0

    def test_glob_patterns_cover_all_formats(self):
        """Test that glob patterns cover all task ID formats."""
        assert "TASK-*.task.md" in TASK_FILE_GLOBS
        assert "T*.task.md" in TASK_FILE_GLOBS
        assert "REL-*.task.md" in TASK_FILE_GLOBS
        assert "BUG-*.task.md" in TASK_FILE_GLOBS


class TestTaskIdRegex:
    """Tests for the compiled regex."""

    def test_regex_is_compiled(self):
        """Test that TASK_ID_REGEX is a compiled pattern."""
        import re
        assert isinstance(TASK_ID_REGEX, re.Pattern)

    def test_regex_case_insensitive(self):
        """Test that regex is case-insensitive."""
        assert TASK_ID_REGEX.flags & 2  # re.IGNORECASE = 2
