"""Tests for Trello custom field validation module."""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from bpsai_pair.trello.fields import (
    validate_field_value,
    map_value_to_option,
    get_default_mappings_for_field,
    get_cached_board_fields,
    fetch_board_custom_fields,
    FieldValidator,
    DEFAULT_STACK_MAPPINGS,
    DEFAULT_STATUS_MAPPINGS,
)


class TestValidateFieldValue:
    """Tests for validate_field_value function."""

    def test_valid_dropdown_option(self):
        """Test validating a valid dropdown option."""
        board_fields = {
            "Stack": {
                "id": "abc123",
                "type": "list",
                "options": {
                    "React": "opt1",
                    "Flask": "opt2",
                    "Worker/Function": "opt3"
                }
            }
        }
        is_valid, opt_id, error = validate_field_value("Stack", "React", board_fields)
        assert is_valid is True
        assert opt_id == "opt1"
        assert error is None

    def test_invalid_dropdown_option(self):
        """Test validating an invalid dropdown option."""
        board_fields = {
            "Stack": {
                "id": "abc123",
                "type": "list",
                "options": {
                    "React": "opt1",
                    "Flask": "opt2"
                }
            }
        }
        is_valid, opt_id, error = validate_field_value("Stack", "CLI", board_fields)
        assert is_valid is False
        assert opt_id is None
        assert "Invalid value 'CLI'" in error
        assert "React" in error

    def test_case_insensitive_match(self):
        """Test case-insensitive matching for dropdown options."""
        board_fields = {
            "Stack": {
                "id": "abc123",
                "type": "list",
                "options": {
                    "React": "opt1",
                    "Flask": "opt2"
                }
            }
        }
        is_valid, opt_id, error = validate_field_value("Stack", "react", board_fields)
        assert is_valid is True
        assert opt_id == "opt1"
        assert error is None

    def test_text_field_accepts_any_value(self):
        """Test that text fields accept any value."""
        board_fields = {
            "Deployment Tag": {
                "id": "def456",
                "type": "text",
                "options": None
            }
        }
        is_valid, opt_id, error = validate_field_value("Deployment Tag", "v2.6.0", board_fields)
        assert is_valid is True
        assert opt_id is None
        assert error is None

    def test_checkbox_field_valid_values(self):
        """Test checkbox field accepts boolean-like values."""
        board_fields = {
            "Agent Task": {
                "id": "ghi789",
                "type": "checkbox",
                "options": None
            }
        }
        for value in ["true", "false", "yes", "no", "1", "0"]:
            is_valid, opt_id, error = validate_field_value("Agent Task", value, board_fields)
            assert is_valid is True
            assert error is None

    def test_checkbox_field_invalid_value(self):
        """Test checkbox field rejects invalid values."""
        board_fields = {
            "Agent Task": {
                "id": "ghi789",
                "type": "checkbox",
                "options": None
            }
        }
        is_valid, opt_id, error = validate_field_value("Agent Task", "maybe", board_fields)
        assert is_valid is False
        assert "true/false" in error

    def test_field_not_found(self):
        """Test error when field doesn't exist."""
        board_fields = {
            "Stack": {
                "id": "abc123",
                "type": "list",
                "options": {"React": "opt1"}
            }
        }
        is_valid, opt_id, error = validate_field_value("NonExistent", "value", board_fields)
        assert is_valid is False
        assert "not found on board" in error

    def test_number_field_valid(self):
        """Test number field accepts numeric values."""
        board_fields = {
            "Complexity": {
                "id": "num123",
                "type": "number",
                "options": None
            }
        }
        is_valid, opt_id, error = validate_field_value("Complexity", "42", board_fields)
        assert is_valid is True
        assert error is None

    def test_number_field_invalid(self):
        """Test number field rejects non-numeric values."""
        board_fields = {
            "Complexity": {
                "id": "num123",
                "type": "number",
                "options": None
            }
        }
        is_valid, opt_id, error = validate_field_value("Complexity", "not-a-number", board_fields)
        assert is_valid is False
        assert "numeric value" in error


class TestMapValueToOption:
    """Tests for map_value_to_option function."""

    def test_direct_match(self):
        """Test direct option match without mappings."""
        board_fields = {
            "Stack": {
                "id": "abc123",
                "type": "list",
                "options": {
                    "React": "opt1",
                    "Flask": "opt2",
                    "Worker/Function": "opt3"
                }
            }
        }
        mapped, opt_id = map_value_to_option("Stack", "React", board_fields)
        assert mapped == "React"
        assert opt_id == "opt1"

    def test_mapping_applied(self):
        """Test that mappings are applied."""
        board_fields = {
            "Stack": {
                "id": "abc123",
                "type": "list",
                "options": {
                    "React": "opt1",
                    "Flask": "opt2",
                    "Worker/Function": "opt3"
                }
            }
        }
        mappings = {"cli": "Worker/Function", "python": "Flask"}
        mapped, opt_id = map_value_to_option("Stack", "cli", board_fields, mappings)
        assert mapped == "Worker/Function"
        assert opt_id == "opt3"

    def test_no_match_returns_none(self):
        """Test that no match returns None."""
        board_fields = {
            "Stack": {
                "id": "abc123",
                "type": "list",
                "options": {
                    "React": "opt1",
                    "Flask": "opt2"
                }
            }
        }
        mapped, opt_id = map_value_to_option("Stack", "NoMatch", board_fields)
        assert mapped is None
        assert opt_id is None

    def test_case_insensitive_fallback(self):
        """Test case-insensitive matching as fallback."""
        board_fields = {
            "Stack": {
                "id": "abc123",
                "type": "list",
                "options": {
                    "React": "opt1"
                }
            }
        }
        mapped, opt_id = map_value_to_option("Stack", "REACT", board_fields)
        assert mapped == "React"
        assert opt_id == "opt1"


class TestDefaultMappings:
    """Tests for default field mappings."""

    def test_stack_mappings_exist(self):
        """Test that stack mappings cover common values."""
        mappings = get_default_mappings_for_field("Stack")
        assert mappings is not None
        assert "cli" in mappings
        assert "python" in mappings
        assert "frontend" in mappings
        assert "backend" in mappings

    def test_status_mappings_exist(self):
        """Test that status mappings cover common values."""
        mappings = get_default_mappings_for_field("Status")
        assert mappings is not None
        assert "pending" in mappings
        assert "in_progress" in mappings
        assert "done" in mappings

    def test_unknown_field_returns_none(self):
        """Test that unknown field names return None."""
        mappings = get_default_mappings_for_field("UnknownField")
        assert mappings is None

    def test_case_insensitive_field_name(self):
        """Test field name matching is case-insensitive."""
        assert get_default_mappings_for_field("stack") is not None
        assert get_default_mappings_for_field("STACK") is not None
        assert get_default_mappings_for_field("Status") is not None


class TestCachedBoardFields:
    """Tests for caching functionality."""

    def test_cache_creation(self, tmp_path):
        """Test that cache file is created."""
        mock_client = MagicMock()
        mock_client.get_custom_fields.return_value = []

        cache_dir = tmp_path / "cache"
        fields = get_cached_board_fields("board123", mock_client, cache_dir=cache_dir)

        cache_file = cache_dir / "trello_fields_board123.json"
        assert cache_file.exists()

    def test_cache_reuse(self, tmp_path):
        """Test that cached values are reused."""
        mock_client = MagicMock()
        mock_client.get_custom_fields.return_value = []

        cache_dir = tmp_path / "cache"

        # First call - should fetch
        get_cached_board_fields("board123", mock_client, cache_dir=cache_dir)
        assert mock_client.get_custom_fields.call_count == 1

        # Second call - should use cache
        get_cached_board_fields("board123", mock_client, cache_dir=cache_dir)
        assert mock_client.get_custom_fields.call_count == 1  # Still 1

    def test_force_refresh_bypasses_cache(self, tmp_path):
        """Test that force_refresh bypasses cache."""
        mock_client = MagicMock()
        mock_client.get_custom_fields.return_value = []

        cache_dir = tmp_path / "cache"

        # First call
        get_cached_board_fields("board123", mock_client, cache_dir=cache_dir)
        assert mock_client.get_custom_fields.call_count == 1

        # Force refresh
        get_cached_board_fields("board123", mock_client, force_refresh=True, cache_dir=cache_dir)
        assert mock_client.get_custom_fields.call_count == 2


class TestFieldValidator:
    """Tests for FieldValidator class."""

    def test_validate_valid_option(self):
        """Test validating a valid option."""
        mock_client = MagicMock()

        with patch('bpsai_pair.trello.fields.get_cached_board_fields') as mock_cache:
            mock_cache.return_value = {
                "Stack": {
                    "id": "abc123",
                    "type": "list",
                    "options": {"React": "opt1", "Flask": "opt2"}
                }
            }
            validator = FieldValidator("board123", mock_client)
            is_valid, opt_id, error = validator.validate("Stack", "React")
            assert is_valid is True
            assert opt_id == "opt1"

    def test_map_and_validate_with_alias(self):
        """Test mapping an alias to valid option."""
        mock_client = MagicMock()

        with patch('bpsai_pair.trello.fields.get_cached_board_fields') as mock_cache:
            mock_cache.return_value = {
                "Stack": {
                    "id": "abc123",
                    "type": "list",
                    "options": {"Worker/Function": "opt3"}
                }
            }
            validator = FieldValidator("board123", mock_client)
            # Pass explicit mappings for alias support
            mappings = {"cli": "Worker/Function"}
            is_valid, mapped, opt_id, error = validator.map_and_validate("Stack", "cli", mappings=mappings)
            assert is_valid is True
            assert mapped == "Worker/Function"
            assert opt_id == "opt3"
            assert error is None

    def test_get_valid_options(self):
        """Test getting valid options for a field."""
        mock_client = MagicMock()

        with patch('bpsai_pair.trello.fields.get_cached_board_fields') as mock_cache:
            mock_cache.return_value = {
                "Effort": {
                    "id": "eff123",
                    "type": "list",
                    "options": {"S": "opt1", "M": "opt2", "L": "opt3"}
                }
            }
            validator = FieldValidator("board123", mock_client)
            options = validator.get_valid_options("Effort")
            assert options == ["L", "M", "S"]  # Sorted

    def test_get_valid_options_for_non_dropdown(self):
        """Test getting options for non-dropdown field returns None."""
        mock_client = MagicMock()

        with patch('bpsai_pair.trello.fields.get_cached_board_fields') as mock_cache:
            mock_cache.return_value = {
                "Deployment Tag": {
                    "id": "tag123",
                    "type": "text",
                    "options": None
                }
            }
            validator = FieldValidator("board123", mock_client)
            options = validator.get_valid_options("Deployment Tag")
            assert options is None
